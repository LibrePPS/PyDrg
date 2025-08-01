import jpype
from pricers.url_loader import UrlLoader
import os
from datetime import datetime
from input.claim import Claim
from msdrg.msdrg_output import MsdrgOutput
from pricers.ipsf import IPSFProvider
import sqlite3


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

    def pricer_setup(self):
        self.ipps_config_obj = self.ipps_price_config()
        self.csv_ingest_obj = self.ipps_csv_ingest_class()
        self.ipps_config_obj.setCsvIngestionConfiguration(self.csv_ingest_obj)

        #Get today's year
        today = datetime.now()
        year = today.year
        supported_years = self.array_list_class()
        while year >= today.year - 4:
            supported_years.add(jpype.JInt(year))
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
        provider_data.setCbsaActualGeographicLocation(ipsf_provider.cbsa_actual_geographic_location)
        provider_data.setCbsaWageIndexLocation(ipsf_provider.cbsa_wi_location)
        provider_data.setCbsaStandardizedAmountLocation(ipsf_provider.cbsa_standardized_amount_location)
        provider_data.setEhrReductionIndicator(ipsf_provider.ehr_reduction_indicator)
        provider_data.setFederalPpsBlend(ipsf_provider.federal_pps_blend)
        provider_data.setHacReductionParticipantIndicator(ipsf_provider.hac_reduction_participant_indicator)
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
        print(self.pricing_response.toString())
            
        return