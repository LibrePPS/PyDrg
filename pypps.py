from input.claim import Claim
from ioce.ioce_client import IoceClient
from mce.mce_client import MceClient
from msdrg.drg_client import DrgClient
from pricers.ipps import IppsClient
from pricers.opps import OppsClient
from pricers.ipf import IpfClient
from pricers.ipsf import IPSFDatabase
from pricers.opsf import OPSFDatabase
import jpype
import os
from helpers.cms_downloader import CMSDownloader
from helpers.test_examples import json_claim_example, claim_example, opps_claim_example
import logging



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
    def __init__(self, build_jar_dirs: bool = True, jar_path:str = "./jars", db_path: str = "./data/pypps.db", 
                 build_db: bool = False):
        if not os.path.exists(jar_path):
            os.makedirs(jar_path)
        if not os.path.exists(db_path):
            os.makedirs(os.path.dirname(db_path))
        #Pricer Clients @TODO: Add more pricer clients as needed
        self.ipps_client = None
        self.opps_client = None
        self.ipf_client = None
        # End of Pricer Clients
        self.jar_path = jar_path
        self.db_path = db_path
        self.opsf_db = OPSFDatabase(db_path)
        self.ipsf_db = IPSFDatabase(db_path)
        self.logger = logging.getLogger("Pypps")
        self.logger.setLevel(logging.INFO)
        if build_db:
            self.opsf_db.to_sqlite()
            self.ipsf_db.to_sqlite()
        else:
            #check if ipsf and opsf tables exist
            self.opsf_db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='opsf'")
            if not self.opsf_db.cursor.fetchone():
                self.logger.warning("OPSF table does not exist. Please run build_db=True to create the database.")
            self.ipsf_db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ipsf'")
            if not self.ipsf_db.cursor.fetchone():
                self.logger.warning("IPSF table does not exist. Please run build_db=True to create the database.")
        if build_jar_dirs:
            self.cms_downloader = CMSDownloader(jars_dir=jar_path, log_level=self.logger.level)
            self.cms_downloader.build_jar_environment(False)
        if not jpype.isJVMStarted():
            jpype.startJVM(classpath=jar_path + "/*")

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
        #check for pricer sub directory
        if os.path.exists(os.path.join(self.jar_path, "pricers")):
            self.pricers_path = os.path.abspath(os.path.join(self.jar_path, "pricers"))
            self.pricer_jars = [os.path.join(self.pricers_path, f) for f in os.listdir(self.pricers_path) if f.endswith('.jar')]
        if self.pricer_jars:
            self.setup_pricers()

    def setup_pricers(self):
        #check if pricer jars exist by looking for value from PRICERS dictionary in file names of pricer_jars
        for pricer, jar_name in PRICERS.items():
            if any(jar_name in jar for jar in self.pricer_jars):
                try:
                    jar_path = os.path.abspath(next(jar for jar in self.pricer_jars if jar_name in jar))
                    setattr(self, f"{pricer.lower()}_client", globals()[f"{pricer}Client"](jar_path, self.opsf_db.connection))
                except KeyError:
                    self.logger.warning(f"Client for {pricer} not found. This is a warning only, a client for {pricer} may not be implemented yet.")
            else:
                self.logger.warning(f"{pricer} pricer JAR not found in {self.pricers_path}. Please ensure it is downloaded.")

    def shutdown(self):
        if jpype.isJVMStarted():
            jpype.shutdownJVM()
        self.opsf_db.close()
        self.ipsf_db.close()

if __name__ == "__main__":
    # Example usage
    pypps = Pypps(build_jar_dirs=True, jar_path="./jars", db_path="./data/pypps.db", build_db=False) #<--- Set build_db=True to create the database if it does not exist
    pypps.setup_clients()
    
    test_claim_1 = claim_example()
    test_claim_2 = json_claim_example()
    opps_claim = opps_claim_example()

    print("=== MCE Claim Example ===")
    mce_output = pypps.mce_client.process(test_claim_1)
    print(mce_output.model_dump_json(indent=2))
    print("=== End of MCE Claim Example ===")

    print("=== MS-DRG Claim Example ===")
    drg_output = pypps.drg_client.process(test_claim_2)
    print(drg_output.model_dump_json(indent=2))
    print("=== End of MS-DRG Claim Example ===")

    print("=== IOCE Claim Example ===")
    ioce_output = pypps.ioce_client.process(opps_claim)
    print(ioce_output.model_dump_json(indent=2))
    print("=== End of IOCE Claim Example ===")

    # Example of using a pricer client
    if pypps.ipps_client is not None:
        print("=== IPPS Pricer Example ===")
        ipps_output = pypps.ipps_client.process(test_claim_1, drg_output)
        print(ipps_output.model_dump_json(indent=2))
        print("=== End of IPPS Pricer Example ===")
    if pypps.opps_client is not None:
        print("=== OPPS Pricer Example ===")
        opps_output = pypps.opps_client.process(opps_claim, ioce_output)
        print(opps_output.model_dump_json(indent=2))
        print("=== End of OPPS Pricer Example ===")
    if pypps.ipf_client is not None:
        print("=== IPF Pricer Example ===")
        ipf_output = pypps.ipf_client.process(test_claim_1, drg_output)
        print(ipf_output.model_dump_json(indent=2))
        print("=== End of IPF Pricer Example ===")