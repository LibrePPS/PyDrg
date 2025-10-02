import os
from sqlalchemy import Engine
from datetime import datetime
from typing import Optional
from logging import Logger, getLogger
import jpype
from pydantic import BaseModel

from pydrg.helpers.utils import (
    ReturnCode,
    float_or_none,
    py_date_to_java_date,
    create_supported_years,
    handle_java_exceptions,
)
from pydrg.input.claim import Claim
from pydrg.plugins import apply_client_methods, run_client_load_classes
from pydrg.pricers.url_loader import UrlLoader
from pydrg.pricers.opsf import OPSFProvider

COMORBIDITY_CODES = {
    "K2211": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K250": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K252": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K254": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K256": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K260": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K262": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K264": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K266": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K270": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K272": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K274": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K276": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K280": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K282": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K284": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K286": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K31811": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K5521": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K5701": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K5711": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K5713": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K5721": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K5731": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K5733": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K5741": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K5751": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K5753": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K5781": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K5791": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "K5793": {
        "category": "MA",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "A1884": {
        "category": "MC",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "I300": {
        "category": "MC",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "I301": {
        "category": "MC",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "I308": {
        "category": "MC",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "I309": {
        "category": "MC",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "I32": {
        "category": "MC",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "M3212": {
        "category": "MC",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D550": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D551": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D552": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D553": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D558": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D559": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D560": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D561": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D562": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D563": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D565": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D568": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D5700": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D5701": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D5702": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D5703": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D5709": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D571": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D5720": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57211": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57212": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57213": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57218": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57219": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D5740": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57411": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57412": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57413": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57418": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57419": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D5742": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57431": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57432": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57433": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57438": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57439": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D5744": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57451": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57452": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57453": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57458": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57459": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D5780": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57811": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57812": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57813": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57818": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D57819": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D580": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D581": {
        "category": "MD",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D460": {
        "category": "ME",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D461": {
        "category": "ME",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D4620": {
        "category": "ME",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D4621": {
        "category": "ME",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D4622": {
        "category": "ME",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D464": {
        "category": "ME",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D469": {
        "category": "ME",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D46A": {
        "category": "ME",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D46B": {
        "category": "ME",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D46C": {
        "category": "ME",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D46Z": {
        "category": "ME",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D471": {
        "category": "ME",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
    "D473": {
        "category": "ME",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2050, 1, 1),
    },
}


class EsrdBundledPayment(BaseModel):
    blended_composite_rate: Optional[float] = None
    blended_outlier_rate: Optional[float] = None
    blended_payment_rate: Optional[float] = None
    comorbidity_payment_code: Optional[str] = None
    full_composite_rate: Optional[float] = None
    full_outlier_rate: Optional[float] = None
    full_payment_rate: Optional[float] = None

    def from_java(self, java_obj: jpype.JObject) -> None:
        self.blended_composite_rate = float_or_none(java_obj.getBlendedCompositeRate())
        self.blended_outlier_rate = float_or_none(java_obj.getBlendedOutlierRate())
        self.blended_payment_rate = float_or_none(java_obj.getBlendedPaymentRate())
        self.comorbidity_payment_code = str(java_obj.getComorbidityPaymentCode())
        self.full_composite_rate = float_or_none(java_obj.getFullCompositeRate())
        self.full_outlier_rate = float_or_none(java_obj.getFullOutlierRate())
        self.full_payment_rate = float_or_none(java_obj.getFullPaymentRate())


class EsrdAdditionalPayment(BaseModel):
    age_adjustment_factor: Optional[float] = None
    body_mass_index_factor: Optional[float] = None
    body_surface_area_factor: Optional[float] = None
    budget_neutrality_rate: Optional[float] = None
    national_labor_percent: Optional[float] = None
    national_non_labor_percent: Optional[float] = None
    wage_adjustment_rate: Optional[float] = None

    def from_java(self, java_obj: jpype.JObject) -> None:
        self.age_adjustment_factor = float_or_none(java_obj.getAgeAdjustmentFactor())
        self.body_mass_index_factor = float_or_none(java_obj.getBodyMassIndexFactor())
        self.body_surface_area_factor = float_or_none(
            java_obj.getBodySurfaceAreaFactor()
        )
        self.budget_neutrality_rate = float_or_none(java_obj.getBudgetNeutralityRate())
        self.national_labor_percent = float_or_none(java_obj.getNationalLaborPercent())
        self.national_non_labor_percent = float_or_none(
            java_obj.getNationalNonLaborPercent()
        )
        self.wage_adjustment_rate = float_or_none(java_obj.getWageAdjustmentRate())


class EsrdOutput(BaseModel):
    claim_id: str = ""
    return_code: Optional[ReturnCode] = None
    calculation_version: Optional[str] = None
    total_payment: Optional[float] = None
    adj_base_wage_before_etc: Optional[float] = None
    low_volume_amount: Optional[float] = None
    network_reduction_amount: Optional[float] = None
    outlier_non_per_diem_payment: Optional[float] = None
    ppa_adjustment_amount: Optional[float] = None
    pre_ppa_adjustment_amount: Optional[float] = None
    post_ppa_adjustment_amount: Optional[float] = None
    tdapa_adjustment_amount: Optional[float] = None
    tpniescra_adjustment_amount: Optional[float] = None
    tpnies_adjustment_amount: Optional[float] = None
    hdpa_adjustment_amount: Optional[float] = None
    final_wage_index: Optional[float] = None
    additional_payment_data: Optional[EsrdAdditionalPayment] = None
    bundled_payment_data: Optional[EsrdBundledPayment] = None

    def from_java(self, java_obj: jpype.JObject) -> None:
        self.calculation_version = str(java_obj.getCalculationVersion())
        ret_code = java_obj.getReturnCodeData()
        if ret_code:
            self.return_code = ReturnCode()
            self.return_code.from_java(ret_code)
        payment_data = java_obj.getPaymentData()
        if payment_data:
            self.total_payment = float_or_none(payment_data.getTotalPayment())
            self.adj_base_wage_before_etc = float_or_none(
                payment_data.getAdjustedBaseWageBeforeEtcHdpaAmount()
            )
            self.low_volume_amount = float_or_none(payment_data.getLowVolumeAmount())
            self.network_reduction_amount = float_or_none(
                payment_data.getNetworkReductionAmount()
            )
            self.outlier_non_per_diem_payment = float_or_none(
                payment_data.getOutlierNonPerDiemPaymentAmount()
            )
            self.ppa_adjustment_amount = float_or_none(
                payment_data.getPpaAdjustmentAmount()
            )
            self.pre_ppa_adjustment_amount = float_or_none(
                payment_data.getPrePpaAdjustmentAmount()
            )
            self.post_ppa_adjustment_amount = float_or_none(
                payment_data.getPostPpaAdjustmentAmount()
            )
            self.tdapa_adjustment_amount = float_or_none(
                payment_data.getTdapaPaymentAdjustmentAmount()
            )
            self.tpniescra_adjustment_amount = float_or_none(
                payment_data.getTpniesCraPaymentAdjustmentAmount()
            )
            self.tpnies_adjustment_amount = float_or_none(
                payment_data.getTpniesPaymentAdjustmentAmount()
            )
            self.hdpa_adjustment_amount = float_or_none(
                payment_data.getHdpaAdjustmentAmount()
            )
            self.final_wage_index = float_or_none(payment_data.getFinalWageIndex())
            additional_data = payment_data.getAdditionalPaymentInformation()
            if additional_data:
                self.additional_payment_data = EsrdAdditionalPayment()
                self.additional_payment_data.from_java(additional_data)
            bundled_data = payment_data.getBundledPaymentInformation()
            if bundled_data:
                self.bundled_payment_data = EsrdBundledPayment()
                self.bundled_payment_data.from_java(bundled_data)


class EsrdClient:
    def __init__(
        self,
        jar_path=None,
        db: Optional[Engine] = None,
        logger: Optional[Logger] = None,
    ):
        if not jpype.isJVMStarted():
            raise RuntimeError(
                "JVM is not started. Please start the JVM before using EsrdClient."
            )
        # We need to use the URL class loader from Java to prevent classpath issues with other CMS pricers
        if jar_path is None:
            raise ValueError("jar_path must be provided to EsrdClient")
        if not os.path.exists(jar_path):
            raise ValueError(f"jar_path does not exist: {jar_path}")
        self.url_loader = UrlLoader()
        # This loads the jar file into our URL class loader
        self.url_loader.load_urls([f"file://{jar_path}"])
        self.db = db
        if logger is not None:
            self.logger = logger
        else:
            self.logger = getLogger("EsrdClient")
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
        self.esrd_pricer_config_class = jpype.JClass(
            "gov.cms.fiss.pricers.esrd.EsrdPricerConfiguration",
            loader=self.url_loader.class_loader,
        )
        self.provider_data_class = jpype.JClass(
            "gov.cms.fiss.pricers.esrd.api.v2.EsrdOutpatientProviderData",
            loader=self.url_loader.class_loader,
        )

        self.esrd_pricer_dispatch_class = jpype.JClass(
            "gov.cms.fiss.pricers.esrd.core.EsrdPricerDispatch",
            loader=self.url_loader.class_loader,
        )
        self.esrd_pricer_request_class = jpype.JClass(
            "gov.cms.fiss.pricers.esrd.api.v2.EsrdClaimPricingRequest",
            loader=self.url_loader.class_loader,
        )
        self.esrd_pricer_response_class = jpype.JClass(
            "gov.cms.fiss.pricers.esrd.api.v2.EsrdClaimPricingResponse",
            loader=self.url_loader.class_loader,
        )
        self.esrd_pricer_payment_data_class = jpype.JClass(
            "gov.cms.fiss.pricers.esrd.api.v2.EsrdPaymentData",
            loader=self.url_loader.class_loader,
        )
        self.esrd_pricer_claim_data_class = jpype.JClass(
            "gov.cms.fiss.pricers.esrd.api.v2.EsrdClaimData",
            loader=self.url_loader.class_loader,
        )
        self.esrd_csv_ingest_class = jpype.JClass(
            "gov.cms.fiss.pricers.common.csv.CsvIngestionConfiguration",
            loader=self.url_loader.class_loader,
        )
        self.esrd_data_table_class = jpype.JClass(
            "gov.cms.fiss.pricers.esrd.core.tables.DataTables",
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
        self.comorbid_conditions_class = jpype.JClass(
            "gov.cms.fiss.pricers.esrd.api.v2.ComorbidityData",
            loader=self.url_loader.class_loader,
        )

    def pricer_setup(self):
        self.esrd_config_obj = self.esrd_pricer_config_class()
        self.csv_ingest_obj = self.esrd_csv_ingest_class()
        self.esrd_config_obj.setCsvIngestionConfiguration(self.csv_ingest_obj)

        # Get today's year
        supported_years = create_supported_years("ESRD")
        self.esrd_config_obj.setSupportedYears(supported_years)
        self.esrd_data_table_class.loadDataTables(self.esrd_config_obj)
        self.dispatch_obj = self.esrd_pricer_dispatch_class(self.esrd_config_obj)
        if self.dispatch_obj is None:
            raise RuntimeError(
                "Failed to create EsrdPricerDispatch object. Check your JAR file and classpath."
            )

    def py_date_to_java_date(self, py_date):
        return py_date_to_java_date(self, py_date)

    def get_dialysis_rev(self, claim: Claim) -> str:
        for line in claim.lines:
            if (
                line.revenue_code == "0821"
                or line.revenue_code == "0831"
                or line.revenue_code == "0841"
                or line.revenue_code == "0851"
                or line.revenue_code == "0881"
            ):
                return line.revenue_code
        raise ValueError("No dialysis revenue code found in claim lines")

    def get_dialysis_session_count(self, claim: Claim, dialysis_rev: str) -> int:
        dialysis_dates = set()
        for line in claim.lines:
            if line.revenue_code == dialysis_rev:
                if line.service_date is not None:
                    dialysis_dates.add(line.service_date)
        return len(dialysis_dates)

    def create_input_claim(self, claim: Claim, **kwargs) -> jpype.JObject:
        if self.db is None:
            raise ValueError("Database connection is required for ESRD pricing")
        claim_object = self.esrd_pricer_claim_data_class()
        pricing_request = self.esrd_pricer_request_class()
        provider_data = self.provider_data_class()
        if claim.esrd_initial_date is None:
            raise ValueError("esrd_initial_date is required for ESRD pricing")
        claim_object.setDialysisStartDate(
            self.py_date_to_java_date(claim.esrd_initial_date)
        )

        cond_code_list = self.array_list_class()
        for cond in claim.cond_codes:
            cond_code_list.add(cond)
        claim_object.setConditionCodes(cond_code_list)

        dialysis_rev = self.get_dialysis_rev(claim)
        session_count = self.get_dialysis_session_count(claim, dialysis_rev)
        if session_count == 0:
            raise ValueError("No dialysis sessions found in claim")
        claim_object.setDialysisSessionCount(self.java_integer_class(session_count))
        claim_object.setRevenueCode(dialysis_rev)

        if claim.patient is None:
            raise ValueError("Patient Date of Birth is required for ESRD pricing")
        if claim.patient.date_of_birth is None:
            raise ValueError("Patient Date of Birth is required for ESRD pricing")
        claim_object.setPatientDateOfBirth(
            self.py_date_to_java_date(claim.patient.date_of_birth)
        )

        height_set = False
        weight_set = False
        for val in claim.value_codes:
            if val.code == "A8":
                claim_object.setPatientWeight(self.java_big_decimal_class(val.amount))
                weight_set = True
            elif val.code == "A9":
                claim_object.setPatientHeight(self.java_big_decimal_class(val.amount))
                height_set = True
            if val.code == "Q8":
                claim_object.setTotalTdapaAmountQ8(
                    self.java_big_decimal_class(val.amount)
                )
            elif val.code == "QG":
                claim_object.setTotalTpniesAmountQg(
                    self.java_big_decimal_class(val.amount)
                )
            elif val.code == "QH":
                claim_object.setTotalTpniesCraAmountQh(
                    self.java_big_decimal_class(val.amount)
                )

        if not height_set:
            raise ValueError("Patient Height is required for ESRD pricing")
        if not weight_set:
            raise ValueError("Patient Weight is required for ESRD pricing")

        claim_object.setServiceDate(self.py_date_to_java_date(claim.from_date))
        claim_object.setServiceThroughDate(self.py_date_to_java_date(claim.thru_date))

        demo_codes = self.array_list_class()
        for code in claim.demo_codes:
            demo_codes.add(str(code))
        claim_object.setDemoCodes(demo_codes)

        ect_choice = ""
        if "esrd" in claim.additional_data and isinstance(
            claim.additional_data["esrd"], dict
        ):
            esrd_data = claim.additional_data["esrd"]
            if "ect_choice" in esrd_data:
                if esrd_data["ect_choice"] in ["H", "P", "B", None, ""]:
                    ect_choice = esrd_data["ect_choice"]
                    if "ppa_adjustment" not in esrd_data and ect_choice in ("P", "B"):
                        raise ValueError(
                            "ppa_adjustment must be provided when ECT is 'P' or 'B'"
                        )
                    else:
                        ppa_adjustment = 1
                        if "ppa_adjustment" in esrd_data:
                            if isinstance(esrd_data["ppa_adjustment"], float):
                                ppa_adjustment = esrd_data["ppa_adjustment"]
                                claim_object.setPpaAdjustmentPercent(
                                    self.java_big_decimal_class(ppa_adjustment)
                                )
                else:
                    raise ValueError("ect_choice must be 'H', 'P', 'B', or None/empty")
        claim_object.setTreatmentChoicesIndicator(str(ect_choice))

        comorbidity_codes = self.array_list_class()
        for code in claim.secondary_dxs:
            val = COMORBIDITY_CODES.get(code.code.replace(".", ""))
            if val:
                if (
                    val["start_date"] >= claim.from_date
                    and val["end_date"] <= claim.thru_date
                ):
                    comorbidity_codes.add(val["category"])
        comorbidity_obj = self.comorbid_conditions_class()
        comorbidity_obj.setComorbidityCodes(comorbidity_codes)
        claim_object.setComorbidities(comorbidity_obj)

        if claim.billing_provider is not None:
            if isinstance(claim.thru_date, datetime):
                date_int = int(claim.thru_date.strftime("%Y%m%d"))
            else:
                date_int = int(str(claim.thru_date).replace("-", ""))
            opsf_provider = OPSFProvider()
            opsf_provider.from_sqlite(self.db, claim.billing_provider, date_int, **kwargs)
        elif claim.servicing_provider is not None:
            if isinstance(claim.thru_date, datetime):
                date_int = int(claim.thru_date.strftime("%Y%m%d"))
            else:
                date_int = int(str(claim.thru_date).replace("-", ""))
            opsf_provider = OPSFProvider()
            opsf_provider.from_sqlite(self.db, claim.servicing_provider, date_int, **kwargs)
        else:
            raise ValueError(
                "Either billing or servicing provider must be provided for IPPS pricing."
            )
        if opsf_provider:
            opsf_provider.set_java_values(provider_data, self)
            if (
                opsf_provider.special_payment_indicator is None
                or opsf_provider.special_payment_indicator.strip() == ""
            ):
                provider_data.setSpecialPaymentIndicator("")
            pricing_request.setProviderData(provider_data)
        pricing_request.setClaimData(claim_object)
        return pricing_request

    def process_claim(
        self, claim: Claim, pricing_request: jpype.JObject
    ) -> jpype.JObject:
        if hasattr(self.dispatch_obj, "process"):
            return self.dispatch_obj.process(pricing_request)
        raise ValueError("Dispatch object does not have a process method.")

    @handle_java_exceptions
    def process(self, claim: Claim, **kwargs) -> EsrdOutput:
        """
        Process the claim and return the SNF pricing response.

        :param claim: Claim object to process.
        :return: SnfOutput object.
        """
        if not isinstance(claim, Claim):
            raise ValueError("claim must be an instance of Claim")
        pricing_request = self.create_input_claim(claim, **kwargs)
        pricing_response = self.process_claim(claim, pricing_request)
        esrd_output = EsrdOutput()
        esrd_output.claim_id = claim.claimid
        esrd_output.from_java(pricing_response)
        return esrd_output
