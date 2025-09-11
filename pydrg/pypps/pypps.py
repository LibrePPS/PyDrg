import logging
import os
from typing import Optional
import jpype
from contextlib import ExitStack
from threading import RLock
import atexit

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
    # Class-level locks and tracking for thread safety
    _jvm_lock = RLock()  # Thread-safe JVM operations
    _jvm_started = False  # Track if we started the JVM
    _active_instances = set()  # Track active instances for cleanup
    
    def __init__(
        self,
        build_jar_dirs: bool = True,
        jar_path: str = "./jars",
        db_path: str = "./data/pypps.db",
        build_db: bool = False,
        log_level: int = logging.INFO,
        extra_classpaths: list[str] = [],
        auto_cleanup: bool = True,
    ):
        # Store configuration
        self.extra_classpaths = extra_classpaths or []
        self.jar_path = jar_path
        self.db_path = db_path
        self.auto_cleanup = auto_cleanup
        self.build_jar_dirs = build_jar_dirs
        self.build_db = build_db
        
        # Initialize resource management
        self._exit_stack = ExitStack()
        self._initialized = False
        
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
        
        # Initialize logger first
        self.logger = logging.getLogger("Pypps")
        self.logger.setLevel(log_level)
        
        # Setup directories
        self._ensure_directories()
        
        # Setup databases with resource management
        self._setup_databases()
        
        # Setup JVM with thread safety
        self._setup_jvm()
        
        # Track active instances for cleanup
        Pypps._active_instances.add(self)
        
        # Register automatic cleanup
        if auto_cleanup:
            atexit.register(self.cleanup)

    def __enter__(self):
        """Context manager entry"""
        if not self._initialized:
            self.setup_clients()
            self._initialized = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with proper cleanup"""
        self.cleanup()
        return False  # Don't suppress exceptions

    def _ensure_directories(self):
        """Ensure required directories exist"""
        if not os.path.exists(self.jar_path):
            os.makedirs(self.jar_path)
        if not os.path.exists(os.path.dirname(self.db_path)):
            os.makedirs(os.path.dirname(self.db_path))

    def _setup_jvm(self):
        """Thread-safe JVM initialization"""
        with Pypps._jvm_lock:
            if not jpype.isJVMStarted():
                try:
                    classpath = [f"{self.jar_path}/*", *self.extra_classpaths]
                    jpype.startJVM(classpath=classpath)
                    Pypps._jvm_started = True
                    self.logger.info("JVM started successfully")
                    
                    # Register JVM shutdown with exit stack
                    self._exit_stack.callback(self._shutdown_jvm)
                except Exception as e:
                    self.logger.error(f"Failed to start JVM: {e}")
                    raise RuntimeError(f"JVM startup failed: {e}") from e
            else:
                self.logger.debug("JVM already started")

    def _shutdown_jvm(self):
        """Thread-safe JVM shutdown"""
        with Pypps._jvm_lock:
            if jpype.isJVMStarted() and Pypps._jvm_started:
                try:
                    jpype.shutdownJVM()
                    Pypps._jvm_started = False
                    self.logger.info("JVM shutdown successfully")
                except Exception as e:
                    self.logger.warning(f"Error shutting down JVM: {e}")

    def _setup_databases(self):
        """Setup databases with proper resource management"""
        try:
            # Create database instances and register cleanup
            self.opsf_db = self._exit_stack.enter_context(
                OPSFDatabase(self.db_path)
            )
            self.ipsf_db = self._exit_stack.enter_context(
                IPSFDatabase(self.db_path)
            )
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
        
        # Setup zip code loader
        flat_data_path = os.path.abspath(zipCL_loader.__file__)
        if flat_data_path is None:
            self.logger.warning("Could not find flat_data_path for zip code loader")
        else:
            flat_data_path = os.path.dirname(flat_data_path)
            flat_data_path = os.path.join(flat_data_path, "zipCL-data")
            if os.path.exists(flat_data_path):
                self.logger.info(f"Loading zip code data from {flat_data_path}")
                zipCL_loader.load_records(flat_data_path, self.db_path)
            else:
                self.logger.warning(f"Zip code data files does not exist: {flat_data_path}")

        # Setup CMS downloader if requested
        if self.build_jar_dirs:
            self.cms_downloader = CMSDownloader(
                jars_dir=self.jar_path, log_level=self.logger.level
            )
            self.cms_downloader.build_jar_environment(False)

    def _validate_databases(self):
        """Validate that required database tables exist"""
        try:
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
        except Exception as e:
            self.logger.warning(f"Database validation failed: {e}")

    def cleanup(self):
        """Comprehensive cleanup of all resources"""
        if hasattr(self, '_exit_stack'):
            try:
                self._exit_stack.close()
                self.logger.info("Resources cleaned up successfully")
            except Exception as e:
                self.logger.warning(f"Error during cleanup: {e}")
            finally:
                # Remove from active instances
                Pypps._active_instances.discard(self)

    @classmethod
    def cleanup_all_instances(cls):
        """Fallback nuclear cleanup for all active instances"""
        instances = list(cls._active_instances)
        for instance in instances:
            try:
                instance.cleanup()
            except Exception as e:
                logging.getLogger("Pypps").warning(f"Error cleaning up instance: {e}")

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
        """Deprecated: Use cleanup() method or context manager pattern instead"""
        import warnings
        warnings.warn(
            "shutdown() is deprecated. Use cleanup() method or context manager pattern instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self.cleanup()
