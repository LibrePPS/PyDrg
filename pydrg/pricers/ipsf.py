import os
import sqlalchemy
import requests
from pydantic import BaseModel

from pydrg.input.claim import Provider

IPSF_URL = "https://pds.mps.cms.gov/fiss/v2/inpatient/export?fromDate=2023-01-01&toDate=2030-12-31"

DATATYPES = {
    "provider_ccn": {"type": "TEXT", "position": 0},
    "effective_date": {"type": "INT", "position": 1},
    "fiscal_year_begin_date": {"type": "INT", "position": 2},
    "export_date": {"type": "INT", "position": 3},
    "termination_date": {"type": "INT", "position": 4},
    "waiver_indicator": {"type": "TEXT", "position": 5},
    "intermediary_number": {"type": "TEXT", "position": 6},
    "provider_type": {"type": "TEXT", "position": 7},
    "census_division": {"type": "TEXT", "position": 8},
    "msa_actual_geographic_location": {"type": "TEXT", "position": 9},
    "msa_wage_index_location": {"type": "TEXT", "position": 10},
    "msa_standardized_amount_location": {"type": "TEXT", "position": 11},
    "sole_community_or_medicare_dependent_hospital_base_year": {
        "type": "TEXT",
        "position": 12,
    },
    "change_code_for_lugar_reclassification": {"type": "TEXT", "position": 13},
    "temporary_relief_indicator": {"type": "TEXT", "position": 14},
    "federal_pps_blend": {"type": "TEXT", "position": 15},
    "state_code": {"type": "TEXT", "position": 16},
    "pps_facility_specific_rate": {"type": "REAL", "position": 17},
    "cost_of_living_adjustment": {"type": "REAL", "position": 18},
    "interns_to_beds_ratio": {"type": "REAL", "position": 19},
    "bed_size": {"type": "INT", "position": 20},
    "operating_cost_to_charge_ratio": {"type": "REAL", "position": 21},
    "case_mix_index": {"type": "REAL", "position": 22},
    "supplemental_security_income_ratio": {"type": "REAL", "position": 23},
    "medicaid_ratio": {"type": "REAL", "position": 24},
    "special_provider_update_factor": {"type": "REAL", "position": 25},
    "operating_dsh": {"type": "REAL", "position": 26},
    "fiscal_year_end_date": {"type": "INT", "position": 27},
    "special_payment_indicator": {"type": "TEXT", "position": 28},
    "hosp_quality_indicator": {"type": "TEXT", "position": 29},
    "cbsa_actual_geographic_location": {"type": "TEXT", "position": 30},
    "cbsa_wi_location": {"type": "TEXT", "position": 31},
    "cbsa_standardized_amount_location": {"type": "TEXT", "position": 32},
    "special_wage_index": {"type": "REAL", "position": 33},
    "pass_through_amount_for_capital": {"type": "REAL", "position": 34},
    "pass_through_amount_for_direct_medical_education": {
        "type": "REAL",
        "position": 35,
    },
    "pass_through_amount_for_organ_acquisition": {"type": "REAL", "position": 36},
    "pass_through_total_amount": {"type": "REAL", "position": 37},
    "capital_pps_payment_code": {"type": "TEXT", "position": 38},
    "hospital_specific_capital_rate": {"type": "REAL", "position": 39},
    "old_capital_hold_harmless_rate": {"type": "REAL", "position": 40},
    "old_capital_hold_harmless_rate_effective_date": {"type": "TEXT", "position": 41},
    "capital_cost_to_charge_ratio": {"type": "REAL", "position": 42},
    "new_hospital": {"type": "TEXT", "position": 43},
    "capital_indirect_medical_education_ratio": {"type": "REAL", "position": 44},
    "capital_exception_payment_rate": {"type": "REAL", "position": 45},
    "vpb_participant_indicator": {"type": "TEXT", "position": 46},
    "vbp_adjustment": {"type": "REAL", "position": 47},
    "hrr_participant_indicator": {"type": "INT", "position": 48},
    "hrr_adjustment": {"type": "REAL", "position": 49},
    "bundle_model_discount": {"type": "REAL", "position": 50},
    "hac_reduction_participant_indicator": {"type": "TEXT", "position": 51},
    "uncompensated_care_amount": {"type": "REAL", "position": 52},
    "ehr_reduction_indicator": {"type": "TEXT", "position": 53},
    "low_volume_adjustment_factor": {"type": "REAL", "position": 54},
    "county_code": {"type": "TEXT", "position": 55},
    "medicare_performance_adjustment": {"type": "REAL", "position": 56},
    "ltch_dpp_indicator": {"type": "TEXT", "position": 57},
    "supplemental_wage_index": {"type": "REAL", "position": 58},
    "supplemental_wage_index_indicator": {"type": "TEXT", "position": 59},
    "change_code_wage_index_reclassification": {"type": "TEXT", "position": 60},
    "national_provider_identifier": {"type": "TEXT", "position": 61},
    "pass_through_amount_for_allogenic_stem_cell_acquisition": {
        "type": "REAL",
        "position": 62,
    },
    "pps_blend_year_indicator": {"type": "TEXT", "position": 63},
    "last_updated": {"type": "TEXT", "position": 64},
    "pass_through_amount_for_direct_graduate_medical_education": {
        "type": "REAL",
        "position": 65,
    },
    "pass_through_amount_for_kidney_acquisition": {"type": "REAL", "position": 66},
    "pass_through_amount_for_supply_chain": {"type": "REAL", "position": 67},
}


class IPSFDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")

    def close(self):
        if self.engine:
            self.engine.dispose()

    def create_table(self):
        columns = ", ".join(
            [f"{name} {info['type']}" for name, info in DATATYPES.items()]
        )
        create_table_sql = f"CREATE TABLE IF NOT EXISTS ipsf ({columns})"
        with self.engine.connect() as connection:
            connection.exec_driver_sql(create_table_sql)
            # Create Index on provider_ccn, national_provider_identifier, and effective_date
            connection.exec_driver_sql(
                "CREATE INDEX IF NOT EXISTS idx_provider_ccn ON ipsf(provider_ccn, effective_date)"
            )
            connection.exec_driver_sql(
                "CREATE INDEX IF NOT EXISTS idx_national_provider_identifier ON ipsf(national_provider_identifier, effective_date)"
            )

    def download(self, url, download_dir: str = "./"):
        """
        Downloads a file from a URL and extracts it if it's a zip file.

        Args:
            url: The URL of the file to download.
        """
        try:
            if not os.path.exists(download_dir):
                print(
                    f"Download directory {download_dir} does not exist, attempting to create"
                )
                os.makedirs(download_dir, exist_ok=True)
            response = requests.get(url, stream=True)
            response.raise_for_status()

            filename = os.path.join(download_dir, "ipsf_data.csv")
            with open(filename, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Downloaded {filename}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url}: {e}")

    def to_sqlite(self, create_table=True):
        """
        Converts the downloaded IPSF data to SQLite format.
        """
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file {self.db_path} does not exist.")

        if create_table:
            self.create_table()
        else:
            with self.engine.connect() as connection:
                rs = connection.exec_driver_sql(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='ipsf'"
                )
                if not rs.fetchone():
                    raise ValueError(
                        "IPSF table does not exist. Please run build_db=True to create the database."
                    )
                # truncate the table if it exists
                connection.exec_driver_sql("DELETE FROM ipsf")
                connection.commit()
                self.download(IPSF_URL, download_dir=os.path.dirname(self.db_path))
                query = "INSERT INTO ipsf VALUES ("
                # Batch through the data and insert 1000 rows at a time
                with open(
                    os.path.join(os.path.dirname(self.db_path), "ipsf_data.csv"), "r"
                ) as file:
                    file.readline()  # Skip header line
                    for line in file:
                        values = line.strip().split(",")
                        if len(values) != len(DATATYPES):
                            print(
                                f"Skipping line with incorrect number of values: {line.strip()}"
                            )
                            continue
                        placeholders = ", ".join(["?"] * len(values))
                        query += placeholders + ")"
                        connection.exec_driver_sql(query, values)
                        query = "INSERT INTO ipsf VALUES ("
                        if connection.connection.cursor().rowcount % 1000 == 0:
                            connection.commit()
                # Commit any remaining rows
                connection.commit()


class IPSFProvider(BaseModel):
    provider_ccn: str = ""
    effective_date: int = 19000101
    fiscal_year_begin_date: int = 19000101
    export_date: int = 19000101
    termination_date: int = 19000101
    waiver_indicator: str = ""
    intermediary_number: str = ""
    provider_type: str = ""
    census_division: str = ""
    msa_actual_geographic_location: str = ""
    msa_wage_index_location: str = ""
    msa_standardized_amount_location: str = ""
    sole_community_or_medicare_dependent_hospital_base_year: str = ""
    change_code_for_lugar_reclassification: str = ""
    temporary_relief_indicator: str = ""
    federal_pps_blend: str = ""
    state_code: str = ""
    pps_facility_specific_rate: float = 0.0
    cost_of_living_adjustment: float = 0.0
    interns_to_beds_ratio: float = 0.0
    bed_size: int = 0
    operating_cost_to_charge_ratio: float = 0.0
    case_mix_index: float = 0.0
    supplemental_security_income_ratio: float = 0.0
    medicaid_ratio: float = 0.0
    special_provider_update_factor: float = 0.0
    operating_dsh: float = 0.0
    fiscal_year_end_date: int = 19000101
    special_payment_indicator: str = ""
    hosp_quality_indicator: str = ""
    cbsa_actual_geographic_location: str = ""
    cbsa_wi_location: str = ""
    cbsa_standardized_amount_location: str = ""
    special_wage_index: float = 0.0
    pass_through_amount_for_capital: float = 0.0
    pass_through_amount_for_direct_medical_education: float = 0.0
    pass_through_amount_for_organ_acquisition: float = 0.0
    pass_through_total_amount: float = 0.0
    capital_pps_payment_code: str = ""
    hospital_specific_capital_rate: float = 0.0
    old_capital_hold_harmless_rate: float = 0.0
    old_capital_hold_harmless_rate_effective_date: str = ""
    capital_cost_to_charge_ratio: float = 0.0  # Default to 0.0 if not provided in data.
    new_hospital: str = ""
    capital_indirect_medical_education_ratio: float = (
        0.0  # Default to 0.0 if not provided in data.
    )
    capital_exception_payment_rate: float = (
        0.0  # Default to 0.0 if not provided in data.
    )
    vpb_participant_indicator: str = ""
    vbp_adjustment: float = 0.0  # Default to 0.0 if not provided in data.
    hrr_participant_indicator: int = 0  # Default to 0 if not provided in data.
    hrr_adjustment: float = 0.0  # Default to 0.0 if not provided in data.
    bundle_model_discount: float = 0.0  # Default to 0.0 if not provided in data.
    hac_reduction_participant_indicator: str = ""
    uncompensated_care_amount: float = 0.0  # Default to 0.0 if not provided in data.
    ehr_reduction_indicator: str = ""
    low_volume_adjustment_factor: float = 0.0  # Default to 0.0 if not provided in data.
    county_code: str = ""
    medicare_performance_adjustment: float = (
        0.0  # Default to 0.0 if not provided in data.
    )
    ltch_dpp_indicator: str = ""
    supplemental_wage_index: float = 0.0  # Default to 0.0 if not provided in data.
    supplemental_wage_index_indicator: str = ""
    change_code_wage_index_reclassification: str = ""
    national_provider_identifier: str = ""
    pass_through_amount_for_allogenic_stem_cell_acquisition: float = (
        0.0  # Default to 0.0 if not provided in data.
    )
    pps_blend_year_indicator: str = ""
    last_updated: str = ""
    pass_through_amount_for_direct_graduate_medical_education: float = (
        0.0  # Default to 0.0 if not provided in data.
    )
    pass_through_amount_for_kidney_acquisition: float = (
        0.0  # Default to 0.0 if not provided in data.
    )
    pass_through_amount_for_supply_chain: float = (
        0.0  # Default to 0.0 if not provided in data.
    )

    def from_sqlite(self, conn: sqlalchemy.Engine, provider: Provider, date_int: int):
        if provider.other_id:
            lookup_query = "SELECT * FROM ipsf WHERE provider_ccn = ? AND effective_date <= ? ORDER BY effective_date DESC LIMIT 1"
            lookup_value = provider.other_id
        elif provider.npi:
            lookup_query = "SELECT * FROM ipsf WHERE national_provider_identifier = ? AND effective_date <= ? ORDER BY effective_date DESC LIMIT 1"
            lookup_value = provider.npi
        else:
            raise ValueError(
                "Provider must have either an NPI or other_id set to lookup IPSF data."
            )
        with conn.connect() as connection:
            row = connection.exec_driver_sql(lookup_query, (lookup_value, date_int))
            row = row.fetchone()
            if row:
                for key, value in DATATYPES.items():
                    if value["type"] in ["INT", "REAL"]:
                        val = (
                            row[value["position"]]
                            if row[value["position"]] is not None
                            and row[value["position"]] != ""
                            else 0
                        )
                        setattr(self, key, val)
                    else:
                        setattr(self, key, row[value["position"]])
                if self.termination_date == 19000101 or self.termination_date == 0:
                    self.termination_date = 20991231
                # Allow for request level overrides of provider variables
                if "ipsf" in provider.additional_data:
                    if isinstance(provider.additional_data["ipsf"], dict):
                        for key, value in provider.additional_data["ipsf"].items():
                            if hasattr(self, key):
                                setattr(self, key, value)
                return
            else:
                raise ValueError(
                    f"No IPSF data found for provider {provider.other_id or provider.npi} on date {date_int}."
                )

    def set_java_values(self, java_provider, client):
        if not hasattr(client, "java_integer_class") or not hasattr(
            client, "java_big_decimal_class"
        ):
            raise AttributeError(
                "Client must have java_integer_class and java_big_decimal_class attributes."
            )

        java_provider.setBedSize(client.java_integer_class(self.bed_size))
        java_provider.setBundleModel1Discount(
            client.java_big_decimal_class(self.bundle_model_discount)
        )
        java_provider.setCapitalCostToChargeRatio(
            client.java_big_decimal_class(self.capital_cost_to_charge_ratio)
        )
        java_provider.setOperatingCostToChargeRatio(
            client.java_big_decimal_class(self.operating_cost_to_charge_ratio)
        )
        java_provider.setCapitalExceptionPaymentRate(
            client.java_big_decimal_class(self.capital_exception_payment_rate)
        )
        java_provider.setCapitalIndirectMedicalEducationRatio(
            client.java_big_decimal_class(self.capital_indirect_medical_education_ratio)
        )
        java_provider.setCapitalPpsPaymentCode(self.capital_pps_payment_code)
        java_provider.setCbsaActualGeographicLocation(
            str(self.cbsa_actual_geographic_location)
        )
        java_provider.setCbsaWageIndexLocation(str(self.cbsa_wi_location))
        java_provider.setCbsaStandardizedAmountLocation(
            str(self.cbsa_standardized_amount_location)
        )
        java_provider.setEhrReductionIndicator(str(self.ehr_reduction_indicator))
        java_provider.setFederalPpsBlend(str(self.federal_pps_blend))
        java_provider.setHacReductionParticipantIndicator(
            str(self.hac_reduction_participant_indicator)
        )
        java_provider.setHrrAdjustment(
            client.java_big_decimal_class(self.hrr_adjustment)
        )
        java_provider.setHrrParticipantIndicator(str(self.hrr_participant_indicator))
        java_provider.setInternsToBedsRatio(
            client.java_big_decimal_class(self.interns_to_beds_ratio)
        )
        java_provider.setLowVolumeAdjustmentFactor(
            client.java_big_decimal_class(self.low_volume_adjustment_factor)
        )
        java_provider.setLtchDppIndicator(str(self.ltch_dpp_indicator))
        java_provider.setMedicaidRatio(
            client.java_big_decimal_class(self.medicaid_ratio)
        )
        java_provider.setNewHospital(str(self.new_hospital))
        java_provider.setOldCapitalHoldHarmlessRate(
            client.java_big_decimal_class(self.old_capital_hold_harmless_rate)
        )
        java_provider.setPassThroughAmountForAllogenicStemCellAcquisition(
            client.java_big_decimal_class(
                self.pass_through_amount_for_allogenic_stem_cell_acquisition
            )
        )
        java_provider.setPassThroughAmountForCapital(
            client.java_big_decimal_class(self.pass_through_amount_for_capital)
        )
        java_provider.setPassThroughAmountForDirectMedicalEducation(
            client.java_big_decimal_class(
                self.pass_through_amount_for_direct_medical_education
            )
        )
        java_provider.setPassThroughAmountForSupplyChainCosts(
            client.java_big_decimal_class(self.pass_through_amount_for_supply_chain)
        )
        java_provider.setPassThroughAmountForOrganAcquisition(
            client.java_big_decimal_class(
                self.pass_through_amount_for_organ_acquisition
            )
        )
        java_provider.setPassThroughTotalAmount(
            client.java_big_decimal_class(self.pass_through_total_amount)
        )
        java_provider.setPpsFacilitySpecificRate(
            client.java_big_decimal_class(self.pps_facility_specific_rate)
        )
        java_provider.setSupplementalSecurityIncomeRatio(
            client.java_big_decimal_class(self.supplemental_security_income_ratio)
        )
        java_provider.setTemporaryReliefIndicator(str(self.temporary_relief_indicator))
        java_provider.setUncompensatedCareAmount(
            client.java_big_decimal_class(self.uncompensated_care_amount)
        )
        java_provider.setVbpAdjustment(
            client.java_big_decimal_class(self.vbp_adjustment)
        )
        java_provider.setVbpParticipantIndicator(str(self.vpb_participant_indicator))
        java_provider.setStateCode(self.state_code)
        java_provider.setCountyCode(self.county_code)
        java_provider.setSpecialWageIndex(
            client.java_big_decimal_class(self.special_wage_index)
        )
        java_provider.setProviderType(self.provider_type)
        java_provider.setHospitalQualityIndicator(self.hosp_quality_indicator)
        java_provider.setSpecialPaymentIndicator(self.special_payment_indicator)
        java_provider.setMedicarePerformanceAdjustment(
            client.java_big_decimal_class(self.medicare_performance_adjustment)
        )
        java_provider.setWaiverIndicator(self.waiver_indicator)
        java_provider.setCostOfLivingAdjustment(
            client.java_big_decimal_class(self.cost_of_living_adjustment)
        )
        java_provider.setEffectiveDate(client.py_date_to_java_date(self.effective_date))
        java_provider.setTerminationDate(
            client.py_date_to_java_date(self.termination_date)
        )
        java_provider.setFiscalYearBeginDate(
            client.py_date_to_java_date(self.fiscal_year_begin_date)
        )
        java_provider.setProviderCcn(self.provider_ccn)
