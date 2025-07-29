from drg_client import DrgClient
import jpype
import os
from claim import Claim, DiagnosisCode, ProcedureCode


if __name__ == "__main__":
    jar_path = os.environ.get("MSDRG_JAR_PATH", "path/to/msdrg.jar")
    jpype.startJVM(classpath=jar_path)
    drg_client = DrgClient()

    claim = Claim()
    claim.principal_dx = DiagnosisCode(code="I10", poa="Y")
    claim.patient_status = "01"
    claim.patient.age = 65
    claim.patient.sex = "M"
    claim.admit_date = "2025-07-01"
    claim.from_date = "2025-07-01"
    claim.thru_date = "2025-07-10"
    claim.los = 9
    claim.secondary_dxs.append(DiagnosisCode(code="A000", poa="Y"))
    drg_client.process(claim)