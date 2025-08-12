import os
import sqlite3
from typing import Optional

import requests
from pydantic import BaseModel

from pydrg.input.claim import Provider

OPSF_URL = "https://pds.mps.cms.gov/fiss/v2/outpatient/export?fromDate=2023-01-01&toDate=2030-12-31"

DATATYPES = {
    "provider_ccn": {"type": "TEXT", "position": 0},
    "effective_date": {"type": "INT", "position": 1},
    "national_provider_identifier": {"type": "TEXT", "position": 2},
    "fiscal_year_begin_date": {"type": "INT", "position": 3},
    "export_date": {"type": "INT", "position": 4},
    "termination_date": {"type": "INT", "position": 5},
    "waiver_indicator": {"type": "TEXT", "position": 6},
    "intermediary_number": {"type": "TEXT", "position": 7},
    "provider_type": {"type": "TEXT", "position": 8},
    "special_locality_indicator": {"type": "TEXT", "position": 9},
    "change_code_wage_index_reclassification": {"type": "TEXT", "position": 10},
    "msa_actual_geographic_location": {"type": "TEXT", "position": 11},
    "msa_wage_index_location": {"type": "TEXT", "position": 12},
    "cost_of_living_adjustment": {"type": "REAL", "position": 13},
    "state_code": {"type": "TEXT", "position": 14},
    "tops_indicator": {"type": "TEXT", "position": 15},
    "hospital_quality_indicator": {"type": "TEXT", "position": 16},
    "operating_cost_to_charge_ratio": {"type": "REAL", "position": 17},
    "cbsa_actual_geographic_location": {"type": "TEXT", "position": 18},
    "cbsa_wage_index_location": {"type": "TEXT", "position": 19},
    "special_wage_index": {"type": "REAL", "position": 20},
    "special_payment_indicator": {"type": "TEXT", "position": 21},
    "esrd_children_quality_indicator": {"type": "TEXT", "position": 22},
    "device_cost_to_charge_ratio": {"type": "REAL", "position": 23},
    "county_code": {"type": "TEXT", "position": 24},
    "payment_cbsa": {"type": "TEXT", "position": 25},
    "payment_model_adjustment": {"type": "REAL", "position": 26},
    "medicare_performance_adjustment": {"type": "REAL", "position": 27},
    "supplemental_wage_index_indicator": {"type": "TEXT", "position": 28},
    "supplemental_wage_index": {"type": "REAL", "position": 29},
    "last_updated": {"type": "DATE", "position": 30},
    "carrier_code": {"type": "TEXT", "position": 31},
    "locality_code": {"type": "TEXT", "position": 32},
}


class OPSFDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection: sqlite3.Connection = sqlite3.connect(db_path)
        self.cursor: sqlite3.Cursor = self.connection.cursor()

    def close(self):
        if self.connection:
            self.connection.close()

    def create_table(self):
        columns = ", ".join(
            [f"{key} {value['type']}" for key, value in DATATYPES.items()]
        )
        create_table_sql = f"CREATE TABLE IF NOT EXISTS opsf ({columns})"
        self.cursor.execute(create_table_sql)
        self.connection.commit()
        # Create index on provider_ccn and effective_date for faster lookups
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_opsf_provider_effective ON opsf (provider_ccn, effective_date)"
        )
        # Create index on national_provider_identifier for faster lookups
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_opsf_npi ON opsf (national_provider_identifier, effective_date)"
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
                os.mkdir(download_dir)
            response = requests.get(url, stream=True)
            response.raise_for_status()

            filename = os.path.join(download_dir, "opsf_data.csv")
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
            # Check if the table already exists
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='opsf'"
            )
            if not self.cursor.fetchone():
                raise ValueError(
                    "Table 'opsf' does not exist. Please run create_table=True to create the database."
                )
            # Truncate the table if it exists
            self.cursor.execute("DELETE FROM opsf")
            self.connection.commit()

        self.download(OPSF_URL, download_dir=os.path.dirname(self.db_path))
        query = "INSERT INTO opsf VALUES ("
        # Batch through the data and insert 1000 rows at a time
        with open(
            os.path.join(os.path.dirname(self.db_path), "opsf_data.csv"), "r"
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
                self.cursor.execute(query, values)
                query = "INSERT INTO opsf VALUES ("
                if self.cursor.rowcount % 1000 == 0:
                    self.connection.commit()
        # Commit any remaining rows
        if self.cursor.rowcount % 1000 != 0:
            self.connection.commit()


class OPSFProvider(BaseModel):
    provider_ccn: Optional[str] = None
    effective_date: Optional[int] = None
    national_provider_identifier: Optional[str] = None
    fiscal_year_begin_date: Optional[int] = None
    export_date: Optional[int] = None
    termination_date: Optional[int] = None
    waiver_indicator: Optional[str] = None
    intermediary_number: Optional[str] = None
    provider_type: Optional[str] = None
    special_locality_indicator: Optional[str] = None
    change_code_wage_index_reclassification: Optional[str] = None
    msa_actual_geographic_location: Optional[str] = None
    msa_wage_index_location: Optional[str] = None
    cost_of_living_adjustment: Optional[float] = None
    state_code: Optional[str] = None
    tops_indicator: Optional[str] = None
    hospital_quality_indicator: Optional[str] = None
    operating_cost_to_charge_ratio: Optional[float] = None
    cbsa_actual_geographic_location: Optional[str] = None
    cbsa_wage_index_location: Optional[str] = None
    special_wage_index: Optional[float] = None
    special_payment_indicator: Optional[str] = None
    esrd_children_quality_indicator: Optional[str] = None
    device_cost_to_charge_ratio: Optional[float] = None
    county_code: Optional[str] = None
    payment_cbsa: Optional[str] = None
    payment_model_adjustment: Optional[float] = None
    medicare_performance_adjustment: Optional[float] = None
    supplemental_wage_index_indicator: Optional[str] = None
    supplemental_wage_index: Optional[float] = None
    last_updated: Optional[str] = None  # Date in YYYY-MM-DD format
    carrier_code: Optional[str] = None
    locality_code: Optional[str] = None

    def from_sqlite(self, conn, provider: Provider, date_int: int):
        if provider.other_id:
            lookup_query = "SELECT * FROM opsf WHERE provider_ccn = ? AND effective_date <= ? ORDER BY effective_date DESC LIMIT 1"
            lookup_value = provider.other_id
        elif provider.npi:
            lookup_query = "SELECT * FROM opsf WHERE national_provider_identifier = ? AND effective_date <= ? ORDER BY effective_date DESC LIMIT 1"
            lookup_value = provider.npi
        else:
            raise ValueError(
                "Provider must have either an NPI or other_id set to lookup IPSF data."
            )
        cursor = conn.cursor()
        cursor.execute(lookup_query, (lookup_value, date_int))
        row = cursor.fetchone()
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
            return
        else:
            raise ValueError(
                f"No OPSF data found for provider {provider.other_id or provider.npi} on date {date_int}."
            )
