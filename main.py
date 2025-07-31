from msdrg.drg_client import DrgClient
from mce.mce_client import MceClient
from opps.opps_client import OppsClient
import jpype
import os
from input.claim import Claim, DiagnosisCode, ProcedureCode, PoaType, LineItem, ValueCode
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

def opps_claim_example():
    claim = Claim()
    claim.claimid = "OPPS_EXAMPLE_001"
    claim.principal_dx = DiagnosisCode(code="S3215XK", poa=PoaType.U)
    claim.patient_status = "01"
    claim.patient.age = 65
    claim.patient.sex = "M"
    claim.from_date = "2023-01-01"
    claim.thru_date = "2023-01-02"
    claim.bill_type = "131"
    
    claim.secondary_dxs.append(DiagnosisCode(code="S72044D", poa=PoaType.N))
    claim.secondary_dxs.append(DiagnosisCode(code="17210", poa=PoaType.Y))
    claim.cond_codes = ["15", "25"]
    claim.value_codes = [ValueCode(code="59", amount=43.02)]
    
    claim.lines.append(LineItem(
        service_date="2023-01-01",
        revenue_code="9999",
        hcpcs="27279",
        units=1,
        charges=435.00
    ))
    
    claim.lines.append(LineItem(
        service_date="2023-01-01",
        revenue_code="0360",
        hcpcs="29305",
        modifiers=["22", "ZZ"],
        units=1,
        charges=191.78
    ))
    
    claim.lines.append(LineItem(
        service_date="2023-01-01",
        revenue_code="0610",
        hcpcs="72196",
        units=1,
        charges=140.67
    ))
    
    claim.lines.append(LineItem(
        service_date="2023-01-01",
        revenue_code="0610",
        hcpcs="72197",
        units=1,
        charges=600.25
    ))
    
    claim.lines.append(LineItem(
        service_date="2023-01-02",
        revenue_code="0610",
        hcpcs="2010F",
        units=2,
        charges=45.98
    ))
    
    return claim

def json_claim_example():
    claim_json = {
        "from_date": "2025-07-01",
        "thru_date": "2025-07-10",
        "los": 9,
        "patient_status": "01",
        "admit_date": "2025-07-01",
        "principal_dx": {
            "code": "A021",
            "poa": "Y",
            "dx_type": "PRIMARY"
        },
        "admit_dx": {
            "code": "A021", 
            "poa": "Y",
            "dx_type": "PRIMARY"
        },
        "secondary_dxs": [
            {
                "code": "I82411",
                "poa": "N",
                "dx_type": "SECONDARY"
            }
        ],
        "patient": {
            "age": 65,
            "sex": "M"
        }
    }
    
    return Claim.from_json(claim_json)

if __name__ == "__main__":
    jar_path = os.environ.get("MSDRG_JAR_PATH", "jars/*")
    jpype.startJVM(classpath="jars/*")
    drg_client = DrgClient()
    mce_client = MceClient()
    opps_client = OppsClient()

    print("=== Claim Example ===")
    claim1 = claim_example()
    output1 = drg_client.process(claim1)
    #This will trip a duplicate of Dx Edit in the MCE
    claim1.secondary_dxs[0].code = "A021"
    #This will trigger a Age Conflict in the MCE
    claim1.secondary_dxs.append(DiagnosisCode(code="Z059", poa=PoaType.Y))
    output1_mce = mce_client.process(claim1)
    print(json.dumps(output1.to_json(), indent=2))
    print("=== MCE Output Example ===")
    print(json.dumps(output1_mce.to_json(), indent=2))

    print("=== JSON Claim Example ===")
    claim2 = json_claim_example()
    output2 = drg_client.process(claim2)
    print(json.dumps(output2.to_json(), indent=2))

    print("=== OPPS Claim Example ===")
    opps_claim = opps_claim_example()
    opps_output = opps_client.process(opps_claim)
    print(json.dumps(opps_output.to_json(), indent=2))
    
    # Get descriptions for OPPS output
    print("=== OPPS Descriptions ===")
    descriptions = opps_client.get_descriptions(opps_claim, opps_output)
    print(json.dumps(descriptions, indent=2))