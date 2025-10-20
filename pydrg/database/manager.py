import logging
import os
from typing import Literal
from contextlib import ExitStack
from sqlalchemy import inspect, create_engine

from pydrg.pricers.opsf import OPSFDatabase
from pydrg.pricers.ipsf import IPSFDatabase
from pydrg.converter import ICDConverter
import pydrg.helpers.zipCL_loader as zipCL_loader


class DatabaseManager:
    def __init__(
        self,
        db_path: str,
        db_backend: Literal["sqlite", "postgresql"] = "sqlite",
        build_db: bool = False,
        log_level: int = logging.INFO,
    ):
        self.db_path = db_path
        self.db_backend = db_backend
        self.build_db = build_db
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        self._exit_stack = ExitStack()
        self.engine = None
        self.opsf_db = None
        self.ipsf_db = None
        self.icd10_converter = None

    def __enter__(self):
        self.setup_databases()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._exit_stack.close()

    def setup_databases(self):
        """Setup databases with proper resource management"""
        try:
            # Create database instances and register cleanup
            self.opsf_db = self._exit_stack.enter_context(
                OPSFDatabase(self.db_path, self.db_backend)
            )
            self.ipsf_db = self._exit_stack.enter_context(
                IPSFDatabase(self.db_path, self.db_backend)
            )
            self.engine = self.opsf_db.engine
            self.icd10_converter = ICDConverter(self.ipsf_db.engine)

            if self.build_db:
                self._build_databases()
            else:
                self._validate_databases()

        except Exception as e:
            self.logger.error(f"Database setup failed: {e}")
            raise RuntimeError(f"Database initialization failed: {e}") from e

    def _build_databases(self):
        """Build databases if requested"""
        self.opsf_db.to_sqlite()
        self.ipsf_db.to_sqlite()
        self.icd10_converter.download_icd_conversion_file()
        flat_data_path = os.path.abspath(zipCL_loader.__file__)
        if flat_data_path is None or flat_data_path == "":
            flat_data_path = os.getenv("ZIP_CL_PATH", "")
        # Setup zip code loader
        if flat_data_path is None or flat_data_path == "":
            self.logger.warning("Could not find flat_data_path for zip code loader")
        else:
            flat_data_path = os.path.dirname(flat_data_path)
            flat_data_path = os.path.join(flat_data_path, "zipCL-data")
            if os.path.exists(flat_data_path):
                self.logger.info(f"Loading zip code data from {flat_data_path}")
                zipCL_loader.load_records(flat_data_path, self.opsf_db.engine)
            else:
                self.logger.warning(
                    f"Zip code data files does not exist: {flat_data_path}"
                )

    def _validate_databases(self):
        """Validate that required database tables exist"""
        try:
            opsf_exists = False
            ipsf_exists = False
            # Use inspectors so this works across sqlite, postgres, etc.
            try:
                opsf_inspector = inspect(self.opsf_db.engine)
                opsf_exists = "opsf" in opsf_inspector.get_table_names()
            except Exception as e:  # pragma: no cover - defensive
                self.logger.debug(f"Inspector failed for OPSF DB: {e}")
            try:
                ipsf_inspector = inspect(self.ipsf_db.engine)
                ipsf_exists = "ipsf" in ipsf_inspector.get_table_names()
            except Exception as e:  # pragma: no cover
                self.logger.debug(f"Inspector failed for IPSF DB: {e}")

            if not opsf_exists:
                self.logger.warning(
                    "OPSF table does not exist. Please run build_db=True to create the database."
                )
            if not ipsf_exists:
                self.logger.warning(
                    "IPSF table does not exist. Please run build_db=True to create the database."
                )
        except Exception as e:
            self.logger.warning(f"Database validation failed: {e}")

    def get_engine(self):
        if not self.engine:
            self.engine = create_engine(f"{self.db_backend}:///{self.db_path}")
        return self.engine
