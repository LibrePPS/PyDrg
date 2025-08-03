from msdrg.drg_client import DrgClient
from mce.mce_client import MceClient
from ioce.ioce_client import IoceClient
import jpype
import os
from input.claim import Claim, DiagnosisCode, ProcedureCode, PoaType, LineItem, ValueCode,Provider
from pricers.ipps import IppsClient
from pricers.ipsf import IPSFDatabase

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
    claim.billing_provider = Provider()
    claim.billing_provider.other_id = "010001"
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
            "dx_type": 1
        },
        "admit_dx": {
            "code": "A021", 
            "poa": "Y",
            "dx_type": 1
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
    
    return Claim.model_validate(claim_json)

if __name__ == "__main__":
    jar_path = os.environ.get("MSDRG_JAR_PATH", "jars/*")
    jpype.startJVM(classpath="jars/*")
    drg_client = DrgClient()
    mce_client = MceClient()
    ioce_client = IoceClient()

    print("=== Claim Example ===")
    claim1 = claim_example()
    output1 = drg_client.process(claim1)
    #This will trip a duplicate of Dx Edit in the MCE
    claim1.secondary_dxs[0].code = "A021"
    #This will trigger a Age Conflict in the MCE
    claim1.secondary_dxs.append(DiagnosisCode(code="Z059", poa=PoaType.Y))
    output1_mce = mce_client.process(claim1)
    print(output1.model_dump_json(indent=2))
    print("=== MCE Output Example ===")
    print(output1_mce.model_dump_json(indent=2))

    print("=== JSON Claim Example ===")
    claim2 = json_claim_example()
    output2 = drg_client.process(claim2)
    print(output2.model_dump_json(indent=2))

    print("=== OPPS Claim Example ===")
    opps_claim = opps_claim_example()
    opps_output = ioce_client.process(opps_claim)
    print(opps_output.model_dump_json(indent=2))
    
    # Get descriptions for OPPS output
    print("=== OPPS Descriptions ===")
    descriptions = ioce_client.get_descriptions(opps_claim, opps_output)
    print(descriptions)

    # IPPS Pricer Example
    db_path = "./ipsf_data.db"
    ipsf_db = IPSFDatabase(db_path)
    #ipsf_db.to_sqlite() #<-- This only needs to be run once to create the database
    print("=== IPPS Pricer Example ===")
    ipps_client = IppsClient("/home/jjw07006/Deveolpment/pydrg/jars/ipps-pricer-application-2.10.0.jar", ipsf_db.connection)
    ipps_claim = claim_example()
    drg_output = drg_client.process(ipps_claim)
    ipps_output = ipps_client.process(ipps_claim, drg_output)
    print(ipps_output.model_dump_json(indent=2))