import os
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
from logging import Logger, getLogger

import jpype
from pydantic import BaseModel, Field

from pydrg.helpers.utils import (
    ReturnCode,
    float_or_none,
    py_date_to_java_date,
    create_supported_years,
    handle_java_exceptions,
)
from pydrg.helpers import Zip9Data
from pydrg.input.claim import Claim
from pydrg.plugins import apply_client_methods, run_client_load_classes
from pydrg.pricers.url_loader import UrlLoader
from pydrg.ioce.ioce_output import IoceOutput


class FqhcLineOutput(BaseModel):
    return_code: Optional[ReturnCode] = None
    addon_payment: Optional[float] = None
    coinsurance_amount: Optional[float] = None
    line_number: Optional[int] = None
    mdpcp_reduction_amount: Optional[float] = None
    payment: Optional[float] = None

    def from_java(self, java_obj: jpype.JObject) -> None:
        ret_code = java_obj.getReturnCodeData()
        if ret_code:
            self.return_code = ReturnCode()
            self.return_code.from_java(ret_code)
        self.addon_payment = float_or_none(java_obj.getAddOnPayment())
        self.coinsurance_amount = float_or_none(java_obj.getCoinsuranceAmount())
        self.line_number = java_obj.getLineNumber()
        self.mdpcp_reduction_amount = float_or_none(java_obj.getMdpcpReductionAmount())
        self.payment = float_or_none(java_obj.getPayment())


class FqhcOutput(BaseModel):
    claim_id: str = ""
    calculation_version: Optional[str] = None
    return_code: Optional[ReturnCode] = None
    total_payment: Optional[float] = None
    geographic_adjustment_factor: Optional[float] = None
    coinsurance_amount: Optional[float] = None
    line_payment_data: List[FqhcLineOutput] = Field(default_factory=list)

    def from_java(self, java_obj: jpype.JObject) -> None:
        self.calculation_version = str(java_obj.getCalculationVersion())
        return_code = java_obj.getReturnCodeData()
        if return_code:
            self.return_code = ReturnCode()
            self.return_code.from_java(return_code)
        payment_data = java_obj.getPaymentData()
        self.total_payment = float_or_none(payment_data.getTotalPayment())
        self.geographic_adjustment_factor = float_or_none(
            payment_data.getGeographicAdjustmentFactor()
        )
        self.coinsurance_amount = float_or_none(
            payment_data.getTotalClaimCoinsuranceAmount()
        )
        line_items = payment_data.getServiceLinePayments()
        for line_item in line_items:
            line_output = FqhcLineOutput()
            line_output.from_java(line_item)
            self.line_payment_data.append(line_output)


class FqhcClient:
    def __init__(
        self,
        jar_path=None,
        db: Optional[Engine] = None,
        logger: Optional[Logger] = None,
    ):
        if not jpype.isJVMStarted():
            raise RuntimeError(
                "JVM is not started. Please start the JVM before using HospiceClient."
            )
        # We need to use the URL class loader from Java to prevent classpath issues with other CMS pricers
        if jar_path is None:
            raise ValueError("jar_path must be provided to HospiceClient")
        if not os.path.exists(jar_path):
            raise ValueError(f"jar_path does not exist: {jar_path}")
        self.url_loader = UrlLoader()
        # This loads the jar file into our URL class loader
        self.url_loader.load_urls([f"file://{jar_path}"])
        self.db = db
        if logger is not None:
            self.logger = logger
        else:
            self.logger = getLogger("HospiceClient")
        self.load_classes()
        try:
            run_client_load_classes(self)
        except Exception:
            pass
        self.pricer_setup()
        try:
            apply_client_methods(self)
        except Exception:
            pass

    def load_classes(self):
        self.fqhc_pricer_config_class = jpype.JClass(
            "gov.cms.fiss.pricers.fqhc.FqhcPricerConfiguration",
            loader=self.url_loader.class_loader,
        )
        self.fqhc_pricer_dispatch_class = jpype.JClass(
            "gov.cms.fiss.pricers.fqhc.core.FqhcPricerDispatch",
            loader=self.url_loader.class_loader,
        )
        self.fqhc_pricer_request_class = jpype.JClass(
            "gov.cms.fiss.pricers.fqhc.api.v2.FqhcClaimPricingRequest",
            loader=self.url_loader.class_loader,
        )
        self.fqhc_pricer_response_class = jpype.JClass(
            "gov.cms.fiss.pricers.fqhc.api.v2.FqhcClaimPricingResponse",
            loader=self.url_loader.class_loader,
        )
        self.fqhc_pricer_payment_data_class = jpype.JClass(
            "gov.cms.fiss.pricers.fqhc.api.v2.FqhcPaymentData",
            loader=self.url_loader.class_loader,
        )
        self.fqhc_pricer_claim_data_class = jpype.JClass(
            "gov.cms.fiss.pricers.fqhc.api.v2.FqhcClaimData",
            loader=self.url_loader.class_loader,
        )
        self.fqhc_csv_ingest_class = jpype.JClass(
            "gov.cms.fiss.pricers.common.csv.CsvIngestionConfiguration",
            loader=self.url_loader.class_loader,
        )
        self.fqhc_data_table_class = jpype.JClass(
            "gov.cms.fiss.pricers.fqhc.core.tables.DataTables",
            loader=self.url_loader.class_loader,
        )
        self.fqhc_ioce_service_line_class = jpype.JClass(
            "gov.cms.fiss.pricers.fqhc.api.v2.IoceServiceLineData",
            loader=self.url_loader.class_loader,
        )
        self.rtn_code_data = jpype.JClass(
            "gov.cms.fiss.pricers.common.api.ReturnCodeData",
            loader=self.url_loader.class_loader,
        )
        self.java_integer_class = jpype.JClass(
            "java.lang.Integer", loader=self.url_loader.class_loader
        )
        self.java_big_decimal_class = jpype.JClass(
            "java.math.BigDecimal", loader=self.url_loader.class_loader
        )
        self.java_string_class = jpype.JClass(
            "java.lang.String", loader=self.url_loader.class_loader
        )
        self.array_list_class = jpype.JClass(
            "java.util.ArrayList", loader=self.url_loader.class_loader
        )
        self.java_date_class = jpype.JClass(
            "java.time.LocalDate", loader=self.url_loader.class_loader
        )
        self.java_data_formatter = jpype.JClass(
            "java.time.format.DateTimeFormatter", loader=self.url_loader.class_loader
        )

    def pricer_setup(self):
        self.fqhc_config_obj = self.fqhc_pricer_config_class()
        self.csv_ingest_obj = self.fqhc_csv_ingest_class()
        self.fqhc_config_obj.setCsvIngestionConfiguration(self.csv_ingest_obj)

        # Get today's year
        supported_years = create_supported_years("FQHC")
        self.fqhc_config_obj.setSupportedYears(supported_years)
        self.fqhc_data_table_class.loadDataTables(self.fqhc_config_obj)
        self.dispatch_obj = self.fqhc_pricer_dispatch_class(self.fqhc_config_obj)
        if self.dispatch_obj is None:
            raise RuntimeError(
                "Failed to create FQHCPricerDispatch object. Check your JAR file and classpath."
            )

    def py_date_to_java_date(self, py_date):
        return py_date_to_java_date(self, py_date)

    def create_input_claim(
        self, claim: Claim, ioce_output: IoceOutput
    ) -> jpype.JObject:
        claim_object = self.fqhc_pricer_claim_data_class()
        pricing_request = self.fqhc_pricer_request_class()

        found_carrier_locality = False
        zip_code = ""
        plus4 = ""
        if claim.billing_provider is not None:
            if claim.billing_provider.address is not None:
                if (
                    claim.billing_provider.carrier.strip() != ""
                    and claim.billing_provider.locality.strip() != ""
                ):
                    claim_object.setCarrier(claim.billing_provider.carrier)
                    claim_object.setLocality(claim.billing_provider.locality)
                    found_carrier_locality = True
                else:
                    if claim.billing_provider.address.zip.strip() != "":
                        zip_code = claim.billing_provider.address.zip.strip()
                        plus4 = claim.billing_provider.address.zip4.strip()
        elif claim.servicing_provider is not None:
            if claim.servicing_provider.address is not None:
                if (
                    claim.servicing_provider.carrier.strip() != ""
                    and claim.servicing_provider.locality.strip() != ""
                ):
                    claim_object.setCarrier(claim.servicing_provider.carrier)
                    claim_object.setLocality(claim.servicing_provider.locality)
                    found_carrier_locality = True
                else:
                    if claim.servicing_provider.address.zip.strip() != "":
                        zip_code = claim.servicing_provider.address.zip.strip()
                        plus4 = claim.servicing_provider.address.zip4.strip()

        if found_carrier_locality == False and zip_code == "":
            raise ValueError(
                "Either billing or servicing provider with a carrier and locality is required."
            )

        if self.db is not None and found_carrier_locality == False:
            try:
                with Session(self.db) as session:
                    result = (
                        session.query(
                            Zip9Data.zip_code,
                            Zip9Data.carrier,
                            Zip9Data.pricing_locality,
                            Zip9Data.plus_four,
                        )
                        .filter(
                            Zip9Data.zip_code == zip_code,
                            Zip9Data.effective_date <= claim.from_date,
                            Zip9Data.end_date >= claim.thru_date,
                        )
                        .order_by(Zip9Data.plus_four.desc())
                        .all()
                    )
                    if result:
                        for row in result:
                            zip_code_val, carrier_val, loc_val, plus_four_val = row
                            if (
                                plus_four_val is None
                                or str(plus_four_val).strip() == ""
                            ):
                                claim_object.setCarrierCode(carrier_val)
                                claim_object.setLocalityCode(loc_val)
                                found_carrier_locality = True
                                break
                            elif plus4 != "" and plus4 == str(plus_four_val).strip():
                                claim_object.setCarrierCode(carrier_val)
                                claim_object.setLocalityCode(loc_val)
                                found_carrier_locality = True
                                break
                    if not found_carrier_locality:
                        raise ValueError(
                            f"Failed to find carrier and locality for zip code: {zip_code}"
                        )
            except Exception:
                raise ValueError("Failed to lookup carrier and locality from zip code.")
        else:
            raise ValueError(
                "Database connection is required to lookup carrier and locality from zip code."
            )

        if not found_carrier_locality:
            raise ValueError(
                "Failed to find carrier and locality information needed for pricing."
            )

        demo_codes = self.array_list_class()
        for code in claim.demo_codes:
            demo_codes.add(self.java_string_class(code))
        claim_object.setDemoCodes(demo_codes)

        if "fqhc" in claim.additional_data:
            fqhc_data = claim.additional_data["fqhc"]
            if "mdpcp_reduction_percentage" in fqhc_data:
                if isinstance(fqhc_data["mdpcp_reduction_percentage"], (float, int)):
                    claim_object.setMdpcpReductionPercent(
                        float(fqhc_data["mdpcp_reduction_percentage"])
                    )
            if "med_advantage_plan_amount" in fqhc_data:
                if isinstance(fqhc_data["med_advantage_plan_amount"], (float, int)):
                    claim_object.setMedicareAdvantagePlanAmount(
                        float(fqhc_data["med_advantage_plan_amount"])
                    )

        claim_object.setServiceFromDate(self.py_date_to_java_date(claim.from_date))
        claim_object.setServiceThroughDate(self.py_date_to_java_date(claim.thru_date))

        ioce_service_lines = self.array_list_class()
        line_id = 1
        for line in ioce_output.line_item_list:
            ioce_service_line = self.fqhc_ioce_service_line_class()
            ioce_service_line.setActionFlag(line.action_flag_output)
            ioce_service_line.setBilledUnits(line.units_input)
            ioce_service_line.setCompositeAdjustmentFlag(line.composite_adjustment_flag)
            ioce_service_line.setCoveredCharges(
                self.java_big_decimal_class(line.charge)
            )
            ioce_service_line.setDateOfService(
                self.py_date_to_java_date(line.service_date)
            )
            ioce_service_line.setDenyOrRejectFlag(line.rejection_denial_flag)
            ioce_service_line.setDiscountingFormula(line.discounting_formula)
            ioce_service_line.setHcpcsCode(line.hcpcs)
            modifiers = self.array_list_class()
            for mod in line.hcpcs_modifier_output_list:
                modifiers.add(mod.hcpcs_modifier)
            ioce_service_line.setHcpcsModifiers(modifiers)
            ioce_service_line.setLineNumber(line_id)
            line_id += 1
            payment_adjustment_flags = self.array_list_class()
            if line.payment_adjustment_flag01.flag.strip() != "":
                payment_adjustment_flags.add(line.payment_adjustment_flag01.flag)
            if line.payment_adjustment_flag02.flag.strip() != "":
                payment_adjustment_flags.add(line.payment_adjustment_flag02.flag)
            ioce_service_line.setPaymentAdjustmentFlags(payment_adjustment_flags)
            ioce_service_line.setPackageFlag(line.packaging_flag.flag)
            ioce_service_line.setPaymentIndicator(line.payment_indicator)
            ioce_service_line.setPaymentMethodFlag(line.payment_method_flag)
            ioce_service_line.setRevenueCode(line.revenue_code)
            ioce_service_line.setServiceUnits(line.units_output)
            ioce_service_line.setStatusIndicator(line.status_indicator)
            ioce_service_lines.add(ioce_service_line)
        claim_object.setIoceServiceLines(ioce_service_lines)
        pricing_request.setClaimData(claim_object)
        return pricing_request

    @handle_java_exceptions
    def process(self, claim: Claim, ioce_output: IoceOutput) -> FqhcOutput:
        pricing_request = self.create_input_claim(claim, ioce_output)
        pricing_response = self.dispatch_obj.process(pricing_request)
        fqhc_output = FqhcOutput()
        fqhc_output.claim_id = claim.claimid
        fqhc_output.from_java(pricing_response)
        return fqhc_output
