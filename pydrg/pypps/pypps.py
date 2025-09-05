import logging
import os
from typing import Optional
import jpype

from pydrg.helpers.cms_downloader import CMSDownloader
from pydrg.ioce.ioce_client import IoceClient
from pydrg.hhag.hhag_client import HhagClient
from pydrg.mce.mce_client import MceClient
from pydrg.msdrg.drg_client import DrgClient
from pydrg.pricers.hospice import HospiceClient
from pydrg.pricers.ipf import IpfClient
from pydrg.pricers.ipps import IppsClient
from pydrg.pricers.snf import SnfClient
from pydrg.pricers.ipsf import IPSFDatabase
from pydrg.pricers.ltch import LtchClient
from pydrg.pricers.hha import HhaClient
from pydrg.pricers.irf import IrfClient
from pydrg.pricers.esrd import EsrdClient
from pydrg.pricers.fqhc import FqhcClient
from pydrg.pricers.opps import OppsClient
from pydrg.pricers.opsf import OPSFDatabase
from pydrg.converter import ICDConverter
from pydrg.irfg.irfg_client import IrfgClient
import pydrg.helpers.zipCL_loader as zipCL_loader

PRICERS = {
    "Esrd": "esrd-pricer",
    "Fqhc": "fqhc-pricer",
    "Hha": "hha-pricer",
    "Hospice": "hospice-pricer",
    "Ipf": "ipf-pricer",
    "Ipps": "ipps-pricer",
    "Irf": "irf-pricer",
    "Ltch": "ltch-pricer",
    "Opps": "opps-pricer",
    "Snf": "snf-pricer",
}


class Pypps:
    def __init__(
        self,
        build_jar_dirs: bool = True,
        jar_path: str = "./jars",
        db_path: str = "./data/pypps.db",
        build_db: bool = False,
        log_level: int = logging.INFO,
        extra_classpaths: list[str] = [],
    ):
        if not os.path.exists(jar_path):
            os.makedirs(jar_path)
        if not os.path.exists(os.path.dirname(db_path)):
            os.makedirs(os.path.dirname(db_path))
        # Pricer Clients @TODO: Add more pricer clients as needed
        self.ipps_client: Optional[IppsClient] = None
        self.opps_client: Optional[OppsClient] = None
        self.ipf_client: Optional[IpfClient] = None
        self.ltch_client: Optional[LtchClient] = None
        self.irf_client: Optional[IrfClient] = None
        self.hospice_client: Optional[HospiceClient] = None
        self.snf_client: Optional[SnfClient] = None
        self.hha_client: Optional[HhaClient] = None
        self.esrd_client: Optional[EsrdClient] = None
        self.fqhc_client: Optional[FqhcClient] = None 
        self.irfg_client: Optional[IrfgClient] = None
        # End of Pricer Clients
        self.jar_path = jar_path
        self.db_path = db_path
        # -----------------Database stuff, these all share the same SQLAlchemy engine
        self.opsf_db = OPSFDatabase(db_path)
        self.ipsf_db = IPSFDatabase(db_path)
        self.icd10_converter = ICDConverter(self.ipsf_db.engine)
        # ----------------------------------------------------------------------------
        self.logger = logging.getLogger("Pypps")
        self.logger.setLevel(log_level)
        if build_db:
            self.opsf_db.to_sqlite()
            self.ipsf_db.to_sqlite()
            self.icd10_converter.download_icd_conversion_file()
            flat_data_path = os.path.abspath(zipCL_loader.__file__)
            if flat_data_path is None:
                self.logger.warning("Could not find flat_data_path for zip code loader")
            else:
                # remote filename from flat_data_path
                flat_data_path = os.path.dirname(flat_data_path)
                flat_data_path = os.path.join(flat_data_path, "zipCL-data")
                if os.path.exists(flat_data_path):
                    self.logger.info(f"Loading zip code data from {flat_data_path}")
                    zipCL_loader.load_records(flat_data_path, db_path)
                else:
                    self.logger.warning(
                        f"Zip code data files does not exist: {flat_data_path}"
                    )
        else:
            # check if ipsf and opsf tables exist
            with (
                self.opsf_db.engine.connect() as opsf_connection,
                self.ipsf_db.engine.connect() as ipsf_connection,
            ):
                rs = opsf_connection.exec_driver_sql(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='opsf'"
                )
                if not rs.fetchone():
                    self.logger.warning(
                        "OPSF table does not exist. Please run build_db=True to create the database."
                    )
                rs = ipsf_connection.exec_driver_sql(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='ipsf'"
                )
                if not rs.fetchone():
                    self.logger.warning(
                        "IPSF table does not exist. Please run build_db=True to create the database."
                    )
        if build_jar_dirs:
            self.cms_downloader = CMSDownloader(
                jars_dir=jar_path, log_level=self.logger.level
            )
            self.cms_downloader.build_jar_environment(False)
        if not jpype.isJVMStarted():
            jpype.startJVM(classpath=[jar_path + "/*", *extra_classpaths])

    def update_opsf_db(self):
        """Update the OPSF database with the latest data."""
        self.opsf_db.to_sqlite(create_table=False)

    def update_ipsf_db(self):
        """Update the IPSF database with the latest data."""
        self.ipsf_db.to_sqlite(create_table=False)

    def setup_clients(self):
        """Initialize the CMS clients."""
        self.drg_client = DrgClient()
        self.mce_client = MceClient()
        self.ioce_client = IoceClient()
        self.hhag_client = HhagClient()
        self.irfg_client = IrfgClient()
        # check for pricer sub directory
        if os.path.exists(os.path.join(self.jar_path, "pricers")):
            self.pricers_path = os.path.abspath(os.path.join(self.jar_path, "pricers"))
            self.pricer_jars = [
                os.path.join(self.pricers_path, f)
                for f in os.listdir(self.pricers_path)
                if f.endswith(".jar")
            ]
        if self.pricer_jars:
            self.setup_pricers()

    def setup_pricers(self):
        # check if pricer jars exist by looking for value from PRICERS dictionary in file names of pricer_jars
        for pricer, jar_name in PRICERS.items():
            if any(jar_name in jar for jar in self.pricer_jars):
                try:
                    jar_path = os.path.abspath(
                        next(jar for jar in self.pricer_jars if jar_name in jar)
                    )
                    setattr(
                        self,
                        f"{pricer.lower()}_client",
                        globals()[f"{pricer}Client"](
                            jar_path, self.opsf_db.engine, self.logger
                        ),
                    )
                except KeyError:
                    self.logger.warning(
                        f"Client for {pricer} not found. This is a warning only, a client for {pricer} may not be implemented yet."
                    )
            else:
                self.logger.warning(
                    f"{pricer} pricer JAR not found in {self.pricers_path}. Please ensure it is downloaded."
                )

    def shutdown(self):
        if jpype.isJVMStarted():
            jpype.shutdownJVM()
        self.opsf_db.close()
        self.ipsf_db.close()
