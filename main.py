from drg_client import DrgClient
import jpype
import os
from claim import Claim, DiagnosisCode, PoaType
import json

def claim_example():
    claim = Claim()
    claim.principal_dx = DiagnosisCode(code="A021", poa=PoaType.Y)
    claim.admit_dx = DiagnosisCode(code="A021", poa=PoaType.Y)
    claim.patient_status = "01"
    claim.patient.age = 65
    claim.patient.sex = "M"
    claim.admit_date = "2025-07-01"
    claim.from_date = "2025-07-01"
    claim.thru_date = "2025-07-10"
    claim.los = 9
    claim.secondary_dxs.append(DiagnosisCode(code="I82411", poa=PoaType.N))
    return claim

def json_claim_example():
    # claim_json = {
    #     "from_date": "2025-07-01",
    #     "thru_date": "2025-07-10",
    #     "los": 9,
    #     "patient_status": "01",
    #     "admit_date": "2025-07-01",
    #     "principal_dx": {
    #         "code": "A021",
    #         "poa": "Y",
    #         "dx_type": "PRIMARY"
    #     },
    #     "admit_dx": {
    #         "code": "A021", 
    #         "poa": "Y",
    #         "dx_type": "PRIMARY"
    #     },
    #     "secondary_dxs": [
    #         {
    #             "code": "I82411",
    #             "poa": "N",
    #             "dx_type": "SECONDARY"
    #         }
    #     ],
    #     "patient": {
    #         "age": 65,
    #         "sex": "M"
    #     }
    # }
    claim_json = {"claimid": "CLM002", "from_date": "2024-02-10", "thru_date": "2024-02-13", "los": 3, "patient_status": "01", "admit_date": "2024-02-10", "principal_dx": {"code": "S72.001A", "poa": "Y", "dx_type": "PRIMARY"}, "admit_dx": {"code": "S72.001A", "poa": "Y", "dx_type": "PRIMARY"}, "secondary_dxs": [{"code": "M80.00XA", "poa": "Y", "dx_type": "SECONDARY"}], "inpatient_pxs": [{"code": "0SR9019", "date": "2024-02-10"}], "patient": {"age": 58, "sex": "F"}}
    
    return Claim.from_json(claim_json)

if __name__ == "__main__":
    jar_path = os.environ.get("MSDRG_JAR_PATH", "jars/*")
    jpype.startJVM(classpath=jar_path)
    drg_client = DrgClient()

    print("=== Claim Example ===")
    claim1 = claim_example()
    output1 = drg_client.process(claim1)
    print(json.dumps(output1.to_json(), indent=2))
    print()

    print("=== JSON Claim Example ===")
    claim2 = json_claim_example()
    output2 = drg_client.process(claim2)
    print(json.dumps(output2.to_json(), indent=2))

    print("=== Batch Process with Progress Example ===")
    claims = drg_client.batch_load_claims("example_data/claims.txt")
    outputs = drg_client.batch_process_with_progress(claims)
    for output in outputs:
        print(output)
        print()