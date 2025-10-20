import os
from sqlalchemy import Engine
from datetime import datetime
from typing import Optional
from logging import Logger, getLogger
import jpype
from pydantic import BaseModel

from pydrg.helpers.utils import (
    float_or_none,
    py_date_to_java_date,
    create_supported_years,
    ReturnCode,
    handle_java_exceptions,
)
from pydrg.input.claim import Claim
from pydrg.plugins import apply_client_methods, run_client_load_classes
from pydrg.pricers.ipsf import IPSFProvider
from pydrg.pricers.url_loader import UrlLoader


class SnfOutput(BaseModel):
    claim_id: str = ""
    return_code: Optional[ReturnCode] = None
    calculation_version: Optional[str] = None
    aids_indicator: Optional[str] = None
    quality_reporting_indicator: Optional[str] = None
    region_indicator: Optional[str] = None
    vbp_payment_difference: Optional[float] = None
    cbsa: Optional[str] = None
    wage_index: Optional[float] = None
    total_payment: Optional[float] = None

    def from_java(self, java_response: jpype.JClass):
        self.calculation_version = str(java_response.getCalculationVersion())
        ret_code = java_response.getReturnCodeData()
        if ret_code is not None:
            self.return_code = ReturnCode()
            self.return_code.from_java(ret_code)
        payment_data = java_response.getPaymentData()
        self.aids_indicator = str(payment_data.getAidsAddOnIndicator())
        self.quality_reporting_indicator = str(
            payment_data.getQualityReportingProgramIndicator()
        )
        self.region_indicator = str(payment_data.getRegionIndicator())
        self.vbp_payment_difference = float_or_none(
            payment_data.getValueBasedPurchasingPaymentDifference()
        )
        self.cbsa = str(payment_data.getFinalCbsa())
        self.wage_index = float_or_none(payment_data.getFinalWageIndex())
        self.total_payment = float_or_none(payment_data.getTotalPayment())


class SnfClient:
    def __init__(
        self,
        jar_path: str,
        db: Optional[Engine] = None,
        logger: Optional[Logger] = None,
    ):
        if not jpype.isJVMStarted():
            raise RuntimeError(
                "JVM is not started. Please start the JVM before creating a SnfClient instance."
            )
        if jar_path is None or not os.path.exists(jar_path):
            raise ValueError(f"Invalid jar_path: {jar_path}")
        self.url_loader = UrlLoader()
        # This loads the jar file into our URL class loader
        self.url_loader.load_urls([f"file://{jar_path}"])
        self.db = db
        if logger is not None:
            self.logger = logger
        else:
            self.logger = getLogger("IppsClient")
        self.load_classes()
        # Allow plugins to load extra/override Java classes before pricer setup
        try:
            run_client_load_classes(self)
        except Exception:
            # Plugins are optional; ignore failures here to avoid breaking core use
            pass
        self.pricer_setup()
        # Bind plugin-provided methods to this client instance
        try:
            apply_client_methods(self)
        except Exception:
            pass

    def load_classes(self):
        self.snf_pricer_config_class = jpype.JClass(
            "gov.cms.fiss.pricers.snf.SnfPricerConfiguration",
            loader=self.url_loader.class_loader,
        )
        self.snf_pricer_dispatch_class = jpype.JClass(
            "gov.cms.fiss.pricers.snf.core.SnfPricerDispatch",
            loader=self.url_loader.class_loader,
        )
        self.snf_pricer_request_class = jpype.JClass(
            "gov.cms.fiss.pricers.snf.api.v2.SnfClaimPricingRequest",
            loader=self.url_loader.class_loader,
        )
        self.snf_pricer_response_class = jpype.JClass(
            "gov.cms.fiss.pricers.snf.api.v2.SnfClaimPricingResponse",
            loader=self.url_loader.class_loader,
        )
        self.snf_pricer_payment_data_class = jpype.JClass(
            "gov.cms.fiss.pricers.snf.api.v2.SnfPaymentData",
            loader=self.url_loader.class_loader,
        )
        self.snf_pricer_provider_data_class = jpype.JClass(
            "gov.cms.fiss.pricers.snf.api.v2.SnfInpatientProviderData",
            loader=self.url_loader.class_loader,
        )
        self.snf_pricer_claim_data_class = jpype.JClass(
            "gov.cms.fiss.pricers.snf.api.v2.SnfClaimData",
            loader=self.url_loader.class_loader,
        )
        self.snf_csv_ingest_class = jpype.JClass(
            "gov.cms.fiss.pricers.common.csv.CsvIngestionConfiguration",
            loader=self.url_loader.class_loader,
        )
        self.snf_data_table_class = jpype.JClass(
            "gov.cms.fiss.pricers.snf.core.tables.DataTables",
            loader=self.url_loader.class_loader,
        )
        self.array_list_class = jpype.JClass(
            "java.util.ArrayList", loader=self.url_loader.class_loader
        )
        self.java_integer_class = jpype.JClass(
            "java.lang.Integer", loader=self.url_loader.class_loader
        )
        self.java_big_decimal_class = jpype.JClass(
            "java.math.BigDecimal", loader=self.url_loader.class_loader
        )
        self.java_date_class = jpype.JClass(
            "java.time.LocalDate", loader=self.url_loader.class_loader
        )
        self.java_data_formatter = jpype.JClass(
            "java.time.format.DateTimeFormatter", loader=self.url_loader.class_loader
        )

    def create_dispatch(self) -> jpype.JObject:
        return self.snf_pricer_dispatch_class(self.snf_config_obj)

    def py_date_to_java_date(self, py_date):
        return py_date_to_java_date(self, py_date)

    def pricer_setup(self):
        self.snf_config_obj = self.snf_pricer_config_class()
        self.csv_ingest_obj = self.snf_csv_ingest_class()
        self.snf_config_obj.setCsvIngestionConfiguration(self.csv_ingest_obj)
        supported_years = create_supported_years(pps="SNF")
        self.snf_config_obj.setSupportedYears(supported_years)
        self.snf_data_table_class.loadDataTables(self.snf_config_obj)
        self.dispatch_obj = self.create_dispatch()
        if self.dispatch_obj is None:
            raise RuntimeError(
                "Failed to create SnfPricerDispatch object. Check your JAR file and classpath."
            )

    def create_input_claim(self, claim: Claim, **kwargs) -> jpype.JObject:
        if self.db is None:
            raise ValueError("Database connection is required for SnfClient.")
        claim_obj = self.snf_pricer_claim_data_class()
        provider_data = self.snf_pricer_provider_data_class()
        pricing_request = self.snf_pricer_request_class()
        hipps_code = ""
        hipps_units = 0
        hipps_date = None
        for line in claim.lines:
            if line.revenue_code == "0022":
                if hipps_date is None:
                    hipps_code = line.hcpcs
                    hipps_units = line.units
                    hipps_date = line.service_date
                elif line.service_date is not None and hipps_date > line.service_date:
                    hipps_code = line.hcpcs
                    hipps_units = line.units
                    hipps_date = line.service_date
        if hipps_date is None or hipps_code.strip() == "" or hipps_units <= 0:
            raise ValueError(
                "Claim must have at least one line with revenue code 0022 and valid HCPCS code, units, and service date."
            )

        claim_obj.setHippsCode(hipps_code)
        claim_obj.setServiceUnits(self.java_integer_class(hipps_units))
        claim_obj.setServiceFromDate(self.py_date_to_java_date(claim.from_date))
        claim_obj.setServiceThroughDate(self.py_date_to_java_date(claim.thru_date))

        prior_pdpm_days = 0
        if isinstance(claim.additional_data, dict):
            if "snf" in claim.additional_data:
                snf_data = claim.additional_data["snf"]
                if isinstance(snf_data, dict):
                    if "prior_pdpm_days" in snf_data:
                        if isinstance(snf_data["prior_pdpm_days"], int):
                            prior_pdpm_days = snf_data["prior_pdpm_days"]
        claim_obj.setPdpmPriorDays(self.java_integer_class(prior_pdpm_days))
        dx_list = self.array_list_class()
        # @TODO need to verify if we need to strip out decimal points from diagnosis codes
        if claim.principal_dx is not None:
            dx_list.add(claim.principal_dx.code)
        if claim.admit_dx is not None:
            dx_list.add(claim.admit_dx.code)
        for dx in claim.secondary_dxs:
            if dx.code is not None and dx.code.strip() != "":
                dx_list.add(dx.code)
        claim_obj.setDiagnosisCodes(dx_list)

        if claim.billing_provider is not None:
            if isinstance(claim.thru_date, datetime):
                date_int = int(claim.thru_date.strftime("%Y%m%d"))
            elif isinstance(claim.thru_date, str):
                date_int = int(claim.thru_date.replace("-", ""))
            ipsf_provider = IPSFProvider()
            ipsf_provider.from_sqlite(self.db, claim.billing_provider, date_int, **kwargs)
        elif claim.servicing_provider is not None:
            if isinstance(claim.thru_date, datetime):
                date_int = int(claim.thru_date.strftime("%Y%m%d"))
            elif isinstance(claim.thru_date, str):
                date_int = int(claim.thru_date.replace("-", ""))
            ipsf_provider = IPSFProvider()
            ipsf_provider.from_sqlite(self.db, claim.servicing_provider, date_int, **kwargs)
        else:
            raise ValueError(
                "Either billing or servicing provider must be provided for IPPS pricing."
            )
        claim_obj.setProviderCcn(ipsf_provider.provider_ccn)
        pricing_request.setClaimData(claim_obj)
        ipsf_provider.set_java_values(provider_data, self)
        pricing_request.setProviderData(provider_data)
        return pricing_request

    def process_claim(
        self, claim: Claim, pricing_request: jpype.JObject
    ) -> jpype.JObject:
        if hasattr(self.dispatch_obj, "process"):
            return self.dispatch_obj.process(pricing_request)
        raise ValueError("Dispatch object does not have a process method.")

    @handle_java_exceptions
    def process(self, claim: Claim, **kwargs):
        """
        Process the claim and return the SNF pricing response.

        :param claim: Claim object to process.
        :return: SnfOutput object.
        """
        if not isinstance(claim, Claim):
            raise ValueError("claim must be an instance of Claim")
        pricing_request = self.create_input_claim(claim, **kwargs)
        pricing_response = self.process_claim(claim, pricing_request)
        snf_output = SnfOutput()
        snf_output.claim_id = claim.claimid
        snf_output.from_java(pricing_response)
        return snf_output
