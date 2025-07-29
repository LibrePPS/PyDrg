import jpype
import jpype.imports
from datetime import datetime
import os

MSDRG_VSTART = "400"

class DrgClient:
    def __init__(self):
        if not jpype.isJVMStarted():
            raise RuntimeError("JVM is not started")
        self.load_enums()
        self.load_input_classes()
        self.load_drg_groupers()

    def load_enums(self):
        #Get enumeration values needed for DRG Runtime options
        try:
            self.logic_tiebreaker = jpype.JClass("gov.agency.msdrg.model.v2.enumeration.MarkingLogicTieBreaker")
            self.affect_drg_option = jpype.JClass("gov.agency.msdrg.model.v2.enumeration.MsdrgAffectDrgOptionFlag")
            self.drg_status = jpype.JClass("gov.agency.msdrg.model.v2.enumeration.MsdrgDischargeStatus")
            self.hospital_status = jpype.JClass("gov.agency.msdrg.model.v2.enumeration.MsdrgHospitalStatusOptionFlag")
            self.sex = jpype.JClass("gov.agency.msdrg.model.v2.enumeration.MsdrgSex")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize enumerations: {e}")
    
    def load_input_classes(self):
        try:
            self.drg_claim_class = jpype.JClass("gov.agency.msdrg.model.v2.transfer.MsdrgClaim")
            self.drg_input_class = jpype.JClass("gov.agency.msdrg.model.v2.transfer.input.MsdrgInput")
            self.drg_dx_class = jpype.JClass("gov.agency.msdrg.model.v2.transfer.input.MsdrgInputDxCode")
            self.drg_px_class = jpype.JClass("gov.agency.msdrg.model.v2.transfer.input.MsdrgInputPrCode")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize input classes: {e}")

    def increment_version(self, version):
        """
        If version ends with "1", increment the version by 9.
        If version ends with "0", increment the version by 1.
        """
        if version.endswith("1"):
            return str(int(version) + 9)
        elif version.endswith("0"):
            return str(int(version) + 1)
        return version
    
    def load_drg_groupers(self):
        end_version = self.determine_end_version()
        curr_version = MSDRG_VSTART
        #Initialize the DRG Runtime options Java object
        try:
            self.runtime_options = jpype.JClass("gov.agency.msdrg.model.v2.RuntimeOptions")()
            self.drg_options = jpype.JClass("gov.agency.msdrg.model.v2.MsdrgRuntimeOption")()
            self.msdrg_option_flags = jpype.JClass("gov.agency.msdrg.model.v2.MsdrgOption")
        except:
            raise RuntimeError("Failed to initialize RuntimeOptions")

        #Set the 3 enum values on the RuntimeOptions object
        #default to non-exempt hospital status
        self.runtime_options.setPoaReportingExempt(self.hospital_status.NON_EXEMPT)
        self.runtime_options.setComputeAffectDrg(self.affect_drg_option.COMPUTE)
        self.runtime_options.setMarkingLogicTieBreaker(self.logic_tiebreaker.CLINICAL_SIGNIFICANCE)

        self.drg_options.put(self.msdrg_option_flags.RUNTIME_OPTION_FLAGS, self.runtime_options)

        self.drg_versions = {}
        while int(curr_version) <= int(end_version):
            try:
                drg_component = jpype.JClass(f"gov.agency.msdrg.v{curr_version}.MsdrgComponent")
                self.drg_versions[curr_version] = drg_component(self.drg_options)
                print(f"Loaded DRG version: {curr_version}")
            except Exception as e:
                print(f"Failed to load DRG version {curr_version}: {e}")
                curr_version = self.increment_version(curr_version)
                continue
            curr_version = self.increment_version(curr_version)

    def determine_end_version(self):
        """
        Max DRG version will be based on the current date
         Step 1.) Version = Year - 1983
         Step 2.) if month is October or later, then add 1 to version, and convert to string that ends with "0"
         Step 3.) if before October, but after March, then convert to string and end with "1"
         Step 4.) if before April, then subtract 1 from version, and convert to string that ends with "0"
         example date: 2025-07-30
         2025 - 1983 = 42
         Month is after March but before October, so we end with "1"
         Version = "421"
        """
        current_year = datetime.now().year
        version = current_year - 1983
        
        if datetime.now().month >= 10:
            version += 1
            return f"{version}0"
        elif datetime.now().month > 3:
            return f"{version}1"
        else:
            version -= 1
            return f"{version}0"
        

if __name__ == "__main__":
    jar_path = os.environ.get("MSDRG_JAR_PATH", "path/to/msdrg.jar")
    jpype.startJVM(classpath=jar_path)
    drg_client = DrgClient()
