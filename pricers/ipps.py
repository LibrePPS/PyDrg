import jpype
from pricers.url_loader import UrlLoader
import os
from datetime import datetime
from input.claim import Claim
from msdrg.msdrg_output import MsdrgOutput
from pricers.ipsf import IPSFProvider
import sqlite3
from pydantic import BaseModel, Field
from typing import Optional

def float_or_none(value):
    """
    Convert a value to float or return None if conversion fails.
    """
    if value is None:
        return None
    try:
        return float(value.floatValue())
    except (ValueError, TypeError) as e:
        return None

class AdditionalCapitalVariableData(BaseModel):
    capital_cost_outlier: Optional[float] = 0.0
    capital_disproportionate_share_hospital_adjustment: Optional[float] = 0.0
    capital_disproportionate_share_hospital_amount: Optional[float] = 0.0
    capital_exception_amount: Optional[float] = None
    capital_federal_rate: Optional[float] = 0.0
    capital_federal_specific_portion: Optional[float] = 0.0
    capital_federal_specific_portion_2b: Optional[float] = 0.0
    capital_federal_specific_portion_percent: Optional[float] = 0.0
    capital_geographic_adjustment_factor: Optional[float] = 1.0
    capital_hospital_specific_portion: Optional[float] = None
    capital_hospital_specific_portion_part: Optional[float] = None
    capital_hospital_specific_portion_percent: Optional[float] = None
    capital_indirect_medical_education_adjustment: Optional[float] = 0.0
    capital_indirect_medical_education_amount: Optional[float] = 0.0
    capital_large_urban_factor: Optional[float] = 1
    capital_old_hold_harmless_amount: Optional[float] = None
    capital_old_hold_harmless_rate: Optional[float] = None
    capital_outlier: Optional[float] = None
    capital_outlier_2b: Optional[float] = None
    capital_payment_code: Optional[str] = None
    capital_total_payment: Optional[float] = 0.0

    def from_java(self, java_obj):
        self.capital_cost_outlier = float_or_none(java_obj.getCapitalCostOutlier())
        self.capital_disproportionate_share_hospital_adjustment = float_or_none(java_obj.getCapitalDisproportionateShareHospitalAdjustment())
        self.capital_disproportionate_share_hospital_amount = float_or_none(java_obj.getCapitalDisproportionateShareHospitalAmount())
        self.capital_exception_amount = float_or_none(java_obj.getCapitalExceptionAmount())
        self.capital_federal_rate = float_or_none(java_obj.getCapitalFederalRate())
        self.capital_federal_specific_portion = float_or_none(java_obj.getCapitalFederalSpecificPortion())
        self.capital_federal_specific_portion_2b = float_or_none(java_obj.getCapitalFederalSpecificPortion2B())
        self.capital_federal_specific_portion_percent = float_or_none(java_obj.getCapitalFederalSpecificPortionPercent())
        self.capital_geographic_adjustment_factor = float_or_none(java_obj.getCapitalGeographicAdjustmentFactor())
        self.capital_hospital_specific_portion = float_or_none(java_obj.getCapitalHospitalSpecificPortion())
        self.capital_hospital_specific_portion_part = float_or_none(java_obj.getCapitalHospitalSpecificPortionPart())
        self.capital_hospital_specific_portion_percent = float_or_none(java_obj.getCapitalHospitalSpecificPortionPercent())
        self.capital_indirect_medical_education_adjustment = float_or_none(java_obj.getCapitalIndirectMedicalEducationAdjustment())
        self.capital_indirect_medical_education_amount = float_or_none(java_obj.getCapitalIndirectMedicalEducationAmount())
        self.capital_large_urban_factor = float_or_none(java_obj.getCapitalLargeUrbanFactor())
        self.capital_old_hold_harmless_amount = float_or_none(java_obj.getCapitalOldHoldHarmlessAmount())
        self.capital_old_hold_harmless_rate = float_or_none(java_obj.getCapitalOldHoldHarmlessRate())
        self.capital_outlier = float_or_none(java_obj.getCapitalOutlier())
        self.capital_outlier_2b = float_or_none(java_obj.getCapitalOutlier2B())
        self.capital_payment_code = str(java_obj.getCapitalPaymentCode())
        self.capital_total_payment = float_or_none(java_obj.getCapitalTotalPayment())

    def to_json(self):
        return {
            "capital_cost_outlier": self.capital_cost_outlier,
            "capital_disproportionate_share_hospital_adjustment": self.capital_disproportionate_share_hospital_adjustment,
            "capital_disproportionate_share_hospital_amount": self.capital_disproportionate_share_hospital_amount,
            "capital_exception_amount": self.capital_exception_amount,
            "capital_federal_rate": self.capital_federal_rate,
            "capital_federal_specific_portion": self.capital_federal_specific_portion,
            "capital_federal_specific_portion_2b": self.capital_federal_specific_portion_2b,
            "capital_federal_specific_portion_percent": self.capital_federal_specific_portion_percent,
            "capital_geographic_adjustment_factor": self.capital_geographic_adjustment_factor,
            "capital_hospital_specific_portion": self.capital_hospital_specific_portion,
            "capital_hospital_specific_portion_part": self.capital_hospital_specific_portion_part,
            "capital_hospital_specific_portion_percent": self.capital_hospital_specific_portion_percent,
            "capital_indirect_medical_education_adjustment": self.capital_indirect_medical_education_adjustment,
            "capital_indirect_medical_education_amount": self.capital_indirect_medical_education_amount,
            "capital_large_urban_factor": self.capital_large_urban_factor,
            "capital_old_hold_harmless_amount": self.capital_old_hold_harmless_amount,
            "capital_old_hold_harmless_rate": self.capital_old_hold_harmless_rate,
            "capital_outlier": self.capital_outlier,
            "capital_outlier_2b": self.capital_outlier_2b,
            "capital_payment_code": self.capital_payment_code,
            "capital_total_payment": self.capital_total_payment
        }

class AdditionalOperatingVariableData(BaseModel):
    operating_base_drg_payment: Optional[float] = 0.0
    operating_disproportionate_share_hospital_amount: Optional[float] = 0.0
    operating_disproportionate_share_hospital_ratio: Optional[float] = 0.0
    operating_dollar_threshold: Optional[float] = 0.0
    operating_federal_specific_portion_part: Optional[float] = 0.0
    operating_hospital_specific_portion_part: Optional[float] = 0.0
    operating_indirect_medical_education_amount: Optional[float] = 0.0

    def from_java(self, java_obj):
        self.operating_base_drg_payment = float_or_none(java_obj.getOperatingBaseDrgPayment())
        self.operating_disproportionate_share_hospital_amount = float_or_none(java_obj.getOperatingDisproportionateShareHospitalAmount())
        self.operating_disproportionate_share_hospital_ratio = float_or_none(java_obj.getOperatingDisproportionateShareHospitalRatio())
        self.operating_dollar_threshold = float_or_none(java_obj.getOperatingDollarThreshold())
        self.operating_federal_specific_portion_part = float_or_none(java_obj.getOperatingFederalSpecificPortionPart())
        self.operating_hospital_specific_portion_part = float_or_none(java_obj.getOperatingHospitalSpecificPortionPart())
        self.operating_indirect_medical_education_amount = float_or_none(java_obj.getOperatingIndirectMedicalEducationAmount())

    def to_json(self):
        return {
            "operating_base_drg_payment": self.operating_base_drg_payment,
            "operating_disproportionate_share_hospital_amount": self.operating_disproportionate_share_hospital_amount,
            "operating_disproportionate_share_hospital_ratio": self.operating_disproportionate_share_hospital_ratio,
            "operating_dollar_threshold": self.operating_dollar_threshold,
            "operating_federal_specific_portion_part": self.operating_federal_specific_portion_part,
            "operating_hospital_specific_portion_part": self.operating_hospital_specific_portion_part,
            "operating_indirect_medical_education_amount": self.operating_indirect_medical_education_amount
        }

class AdditionalPaymentInformationData(BaseModel):
    bundled_adjustment_payment: Optional[float] = None
    electronic_health_record_adjustment_payment: Optional[float] = None
    hospital_acquired_condition_payment: Optional[float] = None
    hospital_readmission_reduction_adjustment_payment: Optional[float] = 0.0
    standard_value: Optional[float] = 0.0
    uncompensated_care_payment: Optional[float] = 0.0
    value_based_purchasing_adjustment_payment: Optional[float] = 0.0

    def from_java(self, java_obj):
        self.bundled_adjustment_payment = float_or_none(java_obj.getBundledAdjustmentPayment())
        self.electronic_health_record_adjustment_payment = float_or_none(java_obj.getElectronicHealthRecordAdjustmentPayment())
        self.hospital_acquired_condition_payment = float_or_none(java_obj.getHospitalAcquiredConditionPayment())
        self.hospital_readmission_reduction_adjustment_payment = float_or_none(java_obj.getHospitalReadmissionReductionAdjustmentPayment())
        self.standard_value = float_or_none(java_obj.getStandardValue())
        self.uncompensated_care_payment = float_or_none(java_obj.getUncompensatedCarePayment())
        self.value_based_purchasing_adjustment_payment = float_or_none(java_obj.getValueBasedPurchasingAdjustmentPayment())

    def to_json(self):
        return {
            "bundled_adjustment_payment": self.bundled_adjustment_payment,
            "electronic_health_record_adjustment_payment": self.electronic_health_record_adjustment_payment,
            "hospital_acquired_condition_payment": self.hospital_acquired_condition_payment,
            "hospital_readmission_reduction_adjustment_payment": self.hospital_readmission_reduction_adjustment_payment,
            "standard_value": self.standard_value,
            "uncompensated_care_payment": self.uncompensated_care_payment,
            "value_based_purchasing_adjustment_payment": self.value_based_purchasing_adjustment_payment
        }

class AdditionalCalculationVariableData(BaseModel):
    additional_capital_variables: AdditionalCapitalVariableData = AdditionalCapitalVariableData()
    additional_operating_variables: AdditionalOperatingVariableData = AdditionalOperatingVariableData()
    additional_payment_information: AdditionalPaymentInformationData = AdditionalPaymentInformationData()
    cost_threshold: Optional[float] = 0.0
    discharge_fraction: Optional[float] = 1.0
    drg_relative_weight: Optional[float] = 0.0
    drg_relative_weight_fraction: Optional[float] = 0.0
    federal_specific_portion_percent: Optional[float] = 1.0
    flx7_payment: Optional[float] = 0.0
    hospital_readmission_reduction_adjustment: Optional[float] = 1.0
    hospital_readmission_reduction_indicator: Optional[str] = ""
    hospital_specific_portion_percent: Optional[float] = None
    hospital_specific_portion_rate: Optional[float] = 0.0
    islet_isolation_add_on_payment: Optional[float] = None
    low_volume_payment: Optional[float] = None
    national_labor_cost: Optional[float] = 0.0
    national_labor_percent: Optional[float] = 0.62
    national_non_labor_cost: Optional[float] = 0.0
    national_non_labor_percent: Optional[float] = 0.38
    national_percent: Optional[float] = 1.0
    new_technology_add_on_payment: Optional[float] = None
    passthrough_total_plus_misc: Optional[float] = None
    regular_labor_cost: Optional[float] = 0.0
    regular_non_labor_cost: Optional[float] = 0.0
    regular_percent: Optional[float] = None
    value_based_purchasing_adjustment_amount: Optional[float] = 1.0
    value_based_purchasing_participant_indicator: Optional[str] = "Y"
    wage_index: Optional[float] = 1.0

    def from_java(self, java_obj):
        self.additional_payment_information = AdditionalPaymentInformationData()
        self.additional_payment_information.from_java(java_obj.getAdditionalPaymentInformation())
        self.additional_capital_variables = AdditionalCapitalVariableData()
        self.additional_capital_variables.from_java(java_obj.getAdditionalCapitalVariables())
        self.additional_operating_variables = AdditionalOperatingVariableData()
        self.additional_operating_variables.from_java(java_obj.getAdditionalOperatingVariables())
        self.cost_threshold = float_or_none(java_obj.getCostThreshold())
        self.discharge_fraction = float_or_none(java_obj.getDischargeFraction())
        self.drg_relative_weight = float_or_none(java_obj.getDrgRelativeWeight())
        self.drg_relative_weight_fraction = float_or_none(java_obj.getDrgRelativeWeightFraction())
        self.federal_specific_portion_percent = float_or_none(java_obj.getFederalSpecificPortionPercent())
        self.flx7_payment = float_or_none(java_obj.getFlx7Payment())
        self.hospital_readmission_reduction_adjustment = float_or_none(java_obj.getHospitalReadmissionReductionAdjustment())
        self.hospital_readmission_reduction_indicator = str(java_obj.getHospitalReadmissionReductionIndicator())
        self.hospital_specific_portion_percent = float_or_none(java_obj.getHospitalSpecificPortionPercent())
        self.hospital_specific_portion_rate = float_or_none(java_obj.getHospitalSpecificPortionRate())
        self.islet_isolation_add_on_payment = float_or_none(java_obj.getIsletIsolationAddOnPayment())
        self.low_volume_payment = float_or_none(java_obj.getLowVolumePayment())
        self.national_labor_cost = float_or_none(java_obj.getNationalLaborCost())
        self.national_labor_percent = float_or_none(java_obj.getNationalLaborPercent())
        self.national_non_labor_cost = float_or_none(java_obj.getNationalNonLaborCost())
        self.national_non_labor_percent = float_or_none(java_obj.getNationalNonLaborPercent())
        self.national_percent = float_or_none(java_obj.getNationalPercent())
        self.new_technology_add_on_payment = float_or_none(java_obj.getNewTechnologyAddOnPayment())
        self.passthrough_total_plus_misc = float_or_none(java_obj.getPassthroughTotalPlusMisc())
        self.regular_labor_cost = float_or_none(java_obj.getRegularLaborCost())
        self.regular_non_labor_cost = float_or_none(java_obj.getRegularNonLaborCost())
        self.regular_percent = float_or_none(java_obj.getRegularPercent())
        self.value_based_purchasing_adjustment_amount = float_or_none(java_obj.getValueBasedPurchasingAdjustmentAmount())
        self.value_based_purchasing_participant_indicator = str(java_obj.getValueBasedPurchasingParticipantIndicator())
        self.wage_index = float_or_none(java_obj.getWageIndex())

    def to_json(self):
        return {
            "cost_threshold": self.cost_threshold,
            "discharge_fraction": self.discharge_fraction,
            "drg_relative_weight": self.drg_relative_weight,
            "drg_relative_weight_fraction": self.drg_relative_weight_fraction,
            "federal_specific_portion_percent": self.federal_specific_portion_percent,
            "flx7_payment": self.flx7_payment,
            "hospital_readmission_reduction_adjustment": self.hospital_readmission_reduction_adjustment,
            "hospital_readmission_reduction_indicator": self.hospital_readmission_reduction_indicator,
            "hospital_specific_portion_percent": self.hospital_specific_portion_percent,
            "hospital_specific_portion_rate": self.hospital_specific_portion_rate,
            "islet_isolation_add_on_payment": self.islet_isolation_add_on_payment,
            "low_volume_payment": self.low_volume_payment,
            "national_labor_cost": self.national_labor_cost,
            "national_labor_percent": self.national_labor_percent,
            "national_non_labor_cost": self.national_non_labor_cost,
            "national_non_labor_percent": self.national_non_labor_percent,
            "national_percent": self.national_percent,
            "new_technology_add_on_payment": self.new_technology_add_on_payment,
            "passthrough_total_plus_misc": self.passthrough_total_plus_misc,
            "regular_labor_cost": self.regular_labor_cost,
            "regular_non_labor_cost": self.regular_non_labor_cost,
            "regular_percent": self.regular_percent,
            "value_based_purchasing_adjustment_amount": self.value_based_purchasing_adjustment_amount,
            "value_based_purchasing_participant_indicator": self.value_based_purchasing_participant_indicator,
            "wage_index": self.wage_index,
            "additional_capital_variables": self.additional_capital_variables.to_json(),
            "additional_operating_variables": self.additional_operating_variables.to_json(),
            "additional_payment_information": self.additional_payment_information.to_json()
        }

class IppsOutput(BaseModel):
    """
    Represents the output of the IPPS pricer.

            self.ipps_output.?.average_los = libre_env.getBigDecimal(payment_data, payment_data_methods.getPtr("getAverageLengthOfStay").?.method, f64);
        self.ipps_output.?.days_cutoff = libre_env.getBigDecimal(payment_data, payment_data_methods.getPtr("getDaysCutoff").?.method, f64);
        self.ipps_output.?.lifetime_reserve_days_used = libre_env.getInt(usize, payment_data, payment_data_methods.getPtr("getLifetimeReserveDaysUsed").?.method, false);
        self.ipps_output.?.operating_dsh_adjustment = libre_env.getBigDecimal(payment_data, payment_data_methods.getPtr("getOperatingDisproportionateShareHospitalAdjustment").?.method, f64);
        self.ipps_output.?.operating_fsp_part = libre_env.getBigDecimal(payment_data, payment_data_methods.getPtr("getOperatingFederalSpecificPortionPart").?.method, f64);
        self.ipps_output.?.operating_hsp_part = libre_env.getBigDecimal(payment_data, payment_data_methods.getPtr("getOperatingHospitalSpecificPortionPart").?.method, f64);
        self.ipps_output.?.operating_ime_adjustment = libre_env.getBigDecimal(payment_data, payment_data_methods.getPtr("getOperatingIndirectMedicalEducationAdjustment").?.method, f64);
        self.ipps_output.?.operating_outlier_payment_part = libre_env.getBigDecimal(payment_data, payment_data_methods.getPtr("getOperatingOutlierPaymentPart").?.method, f64);
        self.ipps_output.?.outlier_days = libre_env.getInt(usize, payment_data, payment_data_methods.getPtr("getOutlierDays").?.method, false);
        self.ipps_output.?.regular_days_used = libre_env.getInt(usize, payment_data, payment_data_methods.getPtr("getRegularDaysUsed").?.method, false);
        self.ipps_output.?.final_cbsa = libre_env.getJavaString(payment_data, payment_data_methods.getPtr("getFinalCbsa").?.method, &self.allocator, null);
        self.ipps_output.?.final_wage_index = libre_env.getBigDecimal(payment_data, payment_data_methods.getPtr("getFinalWageIndex").?.method, f64);
        self.ipps_output.?.total_payment = libre_env.getBigDecimal(payment_data, payment_data_methods.getPtr("getTotalPayment").?.method, f64);

    """
    average_length_of_stay: Optional[float] = None
    days_cutoff: Optional[float] = None
    lifetime_reserved_days_used: Optional[int] = 0
    operating_dsh_adjustment: Optional[float] = 0.0
    operating_fsp_part: Optional[float] = 0.0
    operating_hsp_part: Optional[float] = 0.0
    operating_ime_adjustment: Optional[float] = 0.0
    operating_outlier_payment_part: Optional[float] = 0.0
    outlier_days: Optional[int] = 0
    regular_days_used: Optional[int] = 0
    final_cbsa: Optional[str] = None
    final_wage_index: Optional[float] = 1.0
    total_payment: Optional[float] = 0.0
    additional_calculation_variables: AdditionalCalculationVariableData = AdditionalCalculationVariableData()

    def from_java(self, java_obj):
        payment_data = java_obj.getPaymentData()
        self.average_length_of_stay = float_or_none(payment_data.getAverageLengthOfStay())
        self.days_cutoff = float_or_none(payment_data.getDaysCutoff())
        self.lifetime_reserved_days_used = payment_data.getLifetimeReserveDaysUsed() if payment_data.getLifetimeReserveDaysUsed() is not None else 0
        self.operating_dsh_adjustment = float_or_none(payment_data.getOperatingDisproportionateShareHospitalAdjustment())
        self.operating_fsp_part = float_or_none(payment_data.getOperatingFederalSpecificPortionPart())
        self.operating_hsp_part = float_or_none(payment_data.getOperatingHospitalSpecificPortionPart())
        self.operating_ime_adjustment = float_or_none(payment_data.getOperatingIndirectMedicalEducationAdjustment())
        self.operating_outlier_payment_part = float_or_none(payment_data.getOperatingOutlierPaymentPart())
        self.outlier_days = payment_data.getOutlierDays() if payment_data.getOutlierDays() is not None else 0
        self.regular_days_used = payment_data.getRegularDaysUsed() if payment_data.getRegularDaysUsed() is not None else 0
        self.final_cbsa = str(payment_data.getFinalCbsa()) if payment_data.getFinalCbsa() is not None else None
        self.final_wage_index = float_or_none(payment_data.getFinalWageIndex())
        self.total_payment = float_or_none(payment_data.getTotalPayment())
        self.additional_calculation_variables.from_java(java_obj.getAdditionalCalculationVariables())

    def to_json(self):
        return {
            "additional_calculation_variables": self.additional_calculation_variables.to_json(),
        }

class IppsClient:
    def __init__(self, jar_path=None, db:sqlite3.Connection=None):
        if not jpype.isJVMStarted():
            raise RuntimeError("JVM is not started. Please start the JVM before using IppsClient.")
        #We need to use the URL class loader from Java to prevent classpath issues with other CMS pricers
        if jar_path is None:
            raise ValueError("jar_path must be provided to IppsClient")
        if not os.path.exists(jar_path):
            raise ValueError(f"jar_path does not exist: {jar_path}")    
        self.url_loader = UrlLoader()
        #This loads the jar file into our URL class loader
        self.url_loader.load_urls([f"file://{jar_path}"])
        self.db = db
        self.load_classes()
        self.pricer_setup()
    
    def load_classes(self):
        self.ipps_csv_ingest_class = jpype.JClass("gov.cms.fiss.pricers.common.csv.CsvIngestionConfiguration", loader=self.url_loader.class_loader)
        self.ipps_claim_data_class = jpype.JClass("gov.cms.fiss.pricers.ipps.api.v2.IppsClaimData", loader=self.url_loader.class_loader)
        self.ipps_price_request = jpype.JClass("gov.cms.fiss.pricers.ipps.api.v2.IppsClaimPricingRequest", loader=self.url_loader.class_loader)
        self.ipps_price_response = jpype.JClass("gov.cms.fiss.pricers.ipps.api.v2.IppsClaimPricingResponse", loader=self.url_loader.class_loader)
        self.ipps_payment_data = jpype.JClass("gov.cms.fiss.pricers.ipps.api.v2.IppsPaymentData", loader=self.url_loader.class_loader)
        self.ipps_add_calc_vars = jpype.JClass("gov.cms.fiss.pricers.ipps.api.v2.AdditionalCalculationVariableData", loader=self.url_loader.class_loader)
        self.ipps_add_capital_vars = jpype.JClass("gov.cms.fiss.pricers.ipps.api.v2.AdditionalCapitalVariableData", loader=self.url_loader.class_loader)
        self.ipps_add_operating_vars = jpype.JClass("gov.cms.fiss.pricers.ipps.api.v2.AdditionalOperatingVariableData", loader=self.url_loader.class_loader)
        self.ipps_add_payment_info = jpype.JClass("gov.cms.fiss.pricers.ipps.api.v2.AdditionalPaymentInformationData", loader=self.url_loader.class_loader)
        self.ipps_price_config = jpype.JClass("gov.cms.fiss.pricers.ipps.IppsPricerConfiguration", loader=self.url_loader.class_loader)
        self.ipps_dispatch = jpype.JClass("gov.cms.fiss.pricers.ipps.core.IppsPricerDispatch", loader=self.url_loader.class_loader)
        self.inpatient_prov_data = jpype.JClass("gov.cms.fiss.pricers.ipps.api.v2.IppsInpatientProviderData", loader=self.url_loader.class_loader)
        self.rtn_code_data = jpype.JClass("gov.cms.fiss.pricers.common.api.ReturnCodeData", loader=self.url_loader.class_loader)
        self.ipps_data_tables_class = jpype.JClass("gov.cms.fiss.pricers.ipps.core.tables.DataTables", loader=self.url_loader.class_loader)
        self.array_list_class = jpype.JClass("java.util.ArrayList", loader=self.url_loader.class_loader)
        self.java_integer_class = jpype.JClass("java.lang.Integer", loader=self.url_loader.class_loader)
        self.java_date_class = jpype.JClass("java.time.LocalDate", loader=self.url_loader.class_loader)
        self.java_data_formatter = jpype.JClass("java.time.format.DateTimeFormatter", loader=self.url_loader.class_loader)
        self.java_big_decimal_class = jpype.JClass("java.math.BigDecimal", loader=self.url_loader.class_loader)
        self.java_string_class = jpype.JClass("java.lang.String", loader=self.url_loader.class_loader)

    def py_date_to_java_date(self, py_date):
        """
        Convert a Python datetime object to a Java Date object.
        """
        if py_date is None:
            return None
        if isinstance(py_date, datetime):
            date = py_date.strftime("%Y%m%d")
            formatter = self.java_data_formatter.ofPattern("yyyyMMdd")
            return self.java_date_class.parse(date, formatter)
        elif isinstance(py_date, str):
            #Check that we're in YYYY-MM-DD format
            try:
                date = datetime.strptime(py_date, "%Y-%m-%d")
                return self.py_date_to_java_date(date)
            except ValueError:
                raise ValueError(f"Invalid date format: {py_date}. Expected format is YYYY-MM-DD.")
        elif isinstance(py_date, int):
            #Assuming the int is in YYYYMMDD format
            date_str = str(py_date)
            if len(date_str) != 8:
                raise ValueError(f"Invalid date integer: {py_date}. Expected format is YYYYMMDD.")
            formatter = self.java_data_formatter.ofPattern("yyyyMMdd")
            return self.java_date_class.parse(date_str, formatter)
        else:
            raise TypeError(f"Unsupported date type: {type(py_date)}. Expected datetime, str, or int in YYYYMMDD format.")

    def pricer_setup(self):
        self.ipps_config_obj = self.ipps_price_config()
        self.csv_ingest_obj = self.ipps_csv_ingest_class()
        self.ipps_config_obj.setCsvIngestionConfiguration(self.csv_ingest_obj)

        #Get today's year
        today = datetime.now()
        year = today.year
        supported_years = self.array_list_class()
        while year >= today.year - 3:
            supported_years.add(self.java_integer_class(year))
            year -= 1
        self.ipps_config_obj.setSupportedYears(supported_years)
        self.ipps_data_tables_class.loadDataTables(self.ipps_config_obj)
        self.dispatch_obj = self.ipps_dispatch(self.ipps_config_obj)
        if self.dispatch_obj is None:
            raise RuntimeError("Failed to create IppsPricerDispatch object. Check your JAR file and classpath.")
        
    def create_input_claim(self, claim:Claim, drg_output:MsdrgOutput=None):
        claim_object = self.ipps_claim_data_class()
        provider_data = self.inpatient_prov_data()
        self.pricing_request = self.ipps_price_request()

        #@TODO All these fields need to be added to Claim object
        claim_object.setReviewCode("00")
        demo_codes = self.array_list_class()
        claim_object.setDemoCodes(demo_codes)
        claim_object.setLifetimeReserveDays(self.java_integer_class(0))
        claim_object.setMidnightAdjustmentGeolocation("")
        #--------------------------------------------------
        claim_object.setCoveredCharges(self.java_big_decimal_class(claim.total_charges))
        if claim.los < claim.non_covered_days:
            raise ValueError("LOS cannot be less than non-covered days")
        claim_object.setCoveredDays(self.java_integer_class(claim.los - claim.non_covered_days))
        if claim.thru_date is not None:
            claim_object.setDischargeDate(self.py_date_to_java_date(claim.thru_date))
        else:
            raise ValueError("Thru date is required.")
        claim_object.setLengthOfStay(self.java_integer_class(claim.los))
        if claim.billing_provider is not None:
            claim_object.setProviderCcn(claim.billing_provider.other_id)
        
        java_dxs = self.array_list_class()
        if claim.principal_dx is not None:
            java_dxs.add(claim.principal_dx.code)
        if claim.admit_dx is not None:
            java_dxs.add(claim.admit_dx.code)
        for dx in claim.secondary_dxs:
            java_dxs.add(dx.code)
        claim_object.setDiagnosisCodes(java_dxs)

        java_procedures = self.array_list_class()
        for pr in claim.inpatient_pxs:
            java_procedures.add(pr.code)

        ndc_list = self.array_list_class()
        for line in claim.lines:
            if line.ndc != "":
                ndc_list.add(line.ndc)
        claim_object.setNationalDrugCodes(ndc_list)

        cond_codes = self.array_list_class()
        for code in claim.cond_codes:
            cond_codes.add(code)
        claim_object.setConditionCodes(cond_codes)

        if drg_output is not None:
            claim_object.setDiagnosisRelatedGroup(str(drg_output.final_drg_value))
            claim_object.setDiagnosisRelatedGroupSeverity(str(drg_output.final_severity))
        else:
            #@TODO need to add the ability to pass a DRG without a MsdrgOutput object
            raise ValueError("DRG output is required for IPPS pricing.")
        self.pricing_request.setClaimData(claim_object)

        if claim.billing_provider is not None:
            if isinstance(claim.thru_date, datetime):
                date_int = int(claim.thru_date.strftime("%Y%m%d"))
            else:
                date_int = int(claim.thru_date.replace("-", ""))
            ipsf_provider = IPSFProvider()
            ipsf_provider.from_sqlite(self.db, claim.billing_provider, date_int)
        elif claim.servicing_provider is not None:
            if isinstance(claim.thru_date, datetime):
                date_int = int(claim.thru_date.strftime("%Y%m%d"))
            else:
                date_int = int(claim.thru_date.replace("-", ""))
            ipsf_provider = IPSFProvider()
            ipsf_provider.from_sqlite(self.db, claim.servicing_provider, date_int)
        else:
            raise ValueError("Either billing or servicing provider must be provided for IPPS pricing.")
        provider_data.setBedSize(self.java_integer_class(ipsf_provider.bed_size))
        provider_data.setBundleModel1Discount(self.java_big_decimal_class(ipsf_provider.bundle_model_discount))
        provider_data.setCapitalCostToChargeRatio(self.java_big_decimal_class(ipsf_provider.capital_cost_to_charge_ratio))
        provider_data.setOperatingCostToChargeRatio(self.java_big_decimal_class(ipsf_provider.operating_cost_to_charge_ratio))
        provider_data.setCapitalExceptionPaymentRate(self.java_big_decimal_class(ipsf_provider.capital_exception_payment_rate))
        provider_data.setCapitalIndirectMedicalEducationRatio(self.java_big_decimal_class(ipsf_provider.capital_indirect_medical_education_ratio))
        provider_data.setCapitalPpsPaymentCode(ipsf_provider.capital_pps_payment_code)
        provider_data.setCbsaActualGeographicLocation(str(ipsf_provider.cbsa_actual_geographic_location))
        provider_data.setCbsaWageIndexLocation(str(ipsf_provider.cbsa_wi_location))
        provider_data.setCbsaStandardizedAmountLocation(str(ipsf_provider.cbsa_standardized_amount_location))
        provider_data.setEhrReductionIndicator(str(ipsf_provider.ehr_reduction_indicator))
        provider_data.setFederalPpsBlend(str(ipsf_provider.federal_pps_blend))
        provider_data.setHacReductionParticipantIndicator(str(ipsf_provider.hac_reduction_participant_indicator))
        provider_data.setHrrAdjustment(self.java_big_decimal_class(ipsf_provider.hrr_adjustment))
        provider_data.setHrrParticipantIndicator(str(ipsf_provider.hrr_participant_indicator))
        provider_data.setInternsToBedsRatio(self.java_big_decimal_class(ipsf_provider.interns_to_beds_ratio))
        provider_data.setLowVolumeAdjustmentFactor(self.java_big_decimal_class(ipsf_provider.low_volume_adjustment_factor))
        provider_data.setLtchDppIndicator(str(ipsf_provider.ltch_dpp_indicator))
        provider_data.setMedicaidRatio(self.java_big_decimal_class(ipsf_provider.medicaid_ratio))
        provider_data.setNewHospital(str(ipsf_provider.new_hospital))
        provider_data.setOldCapitalHoldHarmlessRate(self.java_big_decimal_class(ipsf_provider.old_capital_hold_harmless_rate))
        provider_data.setPassThroughAmountForAllogenicStemCellAcquisition(self.java_big_decimal_class(ipsf_provider.pass_through_amount_for_allogenic_stem_cell_acquisition))
        provider_data.setPassThroughAmountForCapital(self.java_big_decimal_class(ipsf_provider.pass_through_amount_for_capital))
        provider_data.setPassThroughAmountForDirectMedicalEducation(self.java_big_decimal_class(ipsf_provider.pass_through_amount_for_direct_medical_education))
        provider_data.setPassThroughAmountForSupplyChainCosts(self.java_big_decimal_class(ipsf_provider.pass_through_amount_for_supply_chain))
        provider_data.setPassThroughAmountForOrganAcquisition(self.java_big_decimal_class(ipsf_provider.pass_through_amount_for_organ_acquisition))
        provider_data.setPassThroughTotalAmount(self.java_big_decimal_class(ipsf_provider.pass_through_total_amount))
        provider_data.setPpsFacilitySpecificRate(self.java_big_decimal_class(ipsf_provider.pps_facility_specific_rate))
        provider_data.setSupplementalSecurityIncomeRatio(self.java_big_decimal_class(ipsf_provider.supplemental_security_income_ratio))
        provider_data.setTemporaryReliefIndicator(str(ipsf_provider.temporary_relief_indicator))
        provider_data.setUncompensatedCareAmount(self.java_big_decimal_class(ipsf_provider.uncompensated_care_amount))
        provider_data.setVbpAdjustment(self.java_big_decimal_class(ipsf_provider.vbp_adjustment))
        provider_data.setVbpParticipantIndicator(str(ipsf_provider.vpb_participant_indicator))
        provider_data.setStateCode(ipsf_provider.state_code)
        provider_data.setCountyCode(ipsf_provider.county_code)
        provider_data.setSpecialWageIndex(self.java_big_decimal_class(ipsf_provider.special_wage_index))
        provider_data.setProviderType(ipsf_provider.provider_type)
        provider_data.setHospitalQualityIndicator(ipsf_provider.hosp_quality_indicator)
        provider_data.setSpecialPaymentIndicator(ipsf_provider.special_payment_indicator)
        provider_data.setMedicarePerformanceAdjustment(self.java_big_decimal_class(ipsf_provider.medicare_performance_adjustment))
        provider_data.setWaiverIndicator(ipsf_provider.waiver_indicator)
        provider_data.setCostOfLivingAdjustment(self.java_big_decimal_class(ipsf_provider.cost_of_living_adjustment))
        provider_data.setEffectiveDate(self.py_date_to_java_date(ipsf_provider.effective_date))
        provider_data.setTerminationDate(self.py_date_to_java_date(ipsf_provider.termination_date))
        provider_data.setFiscalYearBeginDate(self.py_date_to_java_date(ipsf_provider.fiscal_year_begin_date))
        self.pricing_request.setProviderData(provider_data)
        return
    
    def process(self, claim:Claim, drg_output:MsdrgOutput=None):
        """
        Process the claim and return the IPPS pricing response.
        
        :param claim: Claim object to process.
        :param drg_output: MsdrgOutput object containing DRG information.
        :return: IppsClaimPricingResponse object.
        """
        if not isinstance(claim, Claim):
            raise ValueError("claim must be an instance of Claim")
        
        self.create_input_claim(claim, drg_output)
        self.pricing_response = self.dispatch_obj.process(self.pricing_request)
        ipps_output = IppsOutput()
        ipps_output.from_java(self.pricing_response)
        return ipps_output