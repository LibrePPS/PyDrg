import sqlite3
import os
import requests
from pydantic import BaseModel
from input.claim import Provider

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
    "sole_community_or_medicare_dependent_hospital_base_year": {"type": "TEXT", "position": 12},
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
    "pass_through_amount_for_direct_medical_education": {"type": "REAL", "position": 35},
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
    "pass_through_amount_for_allogenic_stem_cell_acquisition": {"type": "REAL", "position": 62},
    "pps_blend_year_indicator": {"type": "TEXT", "position": 63},
    "last_updated": {"type": "TEXT", "position": 64},
    "pass_through_amount_for_direct_graduate_medical_education": {"type": "REAL", "position": 65},
    "pass_through_amount_for_kidney_acquisition": {"type": "REAL", "position": 66},
    "pass_through_amount_for_supply_chain": {"type": "REAL", "position": 67},
}

class IPSFDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection: sqlite3.Connection = sqlite3.connect(db_path)
        self.cursor: sqlite3.Cursor = self.connection.cursor()

    def close(self):
        if self.connection:
            self.connection.close()

    def create_table(self):
        columns = ", ".join([f"{name} {info['type']}" for name, info in DATATYPES.items()])
        create_table_sql = f"CREATE TABLE IF NOT EXISTS ipsf_data ({columns})"
        self.cursor.execute(create_table_sql)
        self.connection.commit()
        #Create Index on provider_ccn, national_provider_identifier, and effective_date
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_provider_ccn ON ipsf_data(provider_ccn, effective_date)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_national_provider_identifier ON ipsf_data(national_provider_identifier, effective_date)")
    
    def download(self,url, download_dir:str = "./"):
        """
        Downloads a file from a URL and extracts it if it's a zip file.

        Args:
            url: The URL of the file to download.
        """
        try:
            if not os.path.exists(download_dir):
                print(f"Download directory {download_dir} does not exist, attempting to create")
                os.mkdir(download_dir)
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            filename = os.path.join(download_dir, "ipsf_data.csv")
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Downloaded {filename}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url}: {e}")

    def to_sqlite(self):
        """
        Converts the downloaded IPSF data to SQLite format.
        """
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file {self.db_path} does not exist.")
        
        self.create_table()
        self.download(IPSF_URL, download_dir="./")
        query = "INSERT INTO ipsf_data VALUES ("
        #Batch through the data and insert 1000 rows at a time
        with open(os.path.join(os.path.dirname(self.db_path), "ipsf_data.csv"), "r") as file:
            file.readline()  # Skip header line
            for line in file:
                values = line.strip().split(",")
                if len(values) != len(DATATYPES):
                    print(f"Skipping line with incorrect number of values: {line.strip()}")
                    continue
                placeholders = ", ".join(["?"] * len(values))
                query += placeholders + ")"
                self.cursor.execute(query, values)
                query = "INSERT INTO ipsf_data VALUES ("
                if self.cursor.rowcount % 1000 == 0:
                    self.connection.commit()
        # Commit any remaining rows
        if self.cursor.rowcount % 1000 != 0:
            self.connection.commit()
        self.close()
    
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
    capital_indirect_medical_education_ratio: float = 0.0  # Default to 0.0 if not provided in data.
    capital_exception_payment_rate: float = 0.0  # Default to 0.0 if not provided in data.
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
    medicare_performance_adjustment: float = 0.0  # Default to 0.0 if not provided in data.
    ltch_dpp_indicator: str = ""
    supplemental_wage_index: float = 0.0  # Default to 0.0 if not provided in data.
    supplemental_wage_index_indicator: str = ""
    change_code_wage_index_reclassification: str = ""
    national_provider_identifier: str = ""
    pass_through_amount_for_allogenic_stem_cell_acquisition: float = 0.0  # Default to 0.0 if not provided in data.
    pps_blend_year_indicator: str = ""
    last_updated: str = ""
    pass_through_amount_for_direct_graduate_medical_education: float = 0.0  # Default to 0.0 if not provided in data.
    pass_through_amount_for_kidney_acquisition: float = 0.0  # Default to 0.0 if not provided in data.
    pass_through_amount_for_supply_chain: float = 0.0  # Default to 0.0 if not provided in data.

    def from_sqlite(self, conn, provider: Provider, date_int: int):
        if provider.other_id:
            lookup_query = "SELECT * FROM ipsf_data WHERE provider_ccn = ? AND effective_date <= ? ORDER BY effective_date DESC LIMIT 1"
            lookup_value = provider.other_id
        elif provider.npi:
            lookup_query = "SELECT * FROM ipsf_data WHERE national_provider_identifier = ? AND effective_date <= ? ORDER BY effective_date DESC LIMIT 1"
            lookup_value = provider.npi
        else:
            raise ValueError("Provider must have either an NPI or other_id set to lookup IPSF data.")
        cursor = conn.cursor()
        cursor.execute(lookup_query, (lookup_value, date_int))
        row = cursor.fetchone()
        if row:
            for key, value in DATATYPES.items():
                if value['type'] in ['INT', 'REAL']:
                    val = row[value['position']] if row[value['position']] is not None and row[value['position']] != "" else 0
                    setattr(self, key, val)
                else:
                    setattr(self, key, row[value['position']])
            return
        else:
            raise ValueError(f"No IPSF data found for provider {provider.other_id or provider.npi} on date {date_int}.")
