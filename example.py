import os
from datetime import datetime
from pydrg.pypps.pypps import Pypps
from pydrg.input.claim import ValueCode, LineItem
from pydrg.helpers.test_examples import json_claim_example, claim_example, opps_claim_example

if __name__ == "__main__":
    jar_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "jars"))
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "pypps.db"))
    pypps = Pypps(build_jar_dirs=True, jar_path=jar_path, db_path=db_path, build_db=False) #<--- Set build_db=True to create the database if it does not exist
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
    if pypps.ltch_client is not None:
        print("=== LTCH Pricer Example ===")
        test_claim_1.billing_provider.other_id = "012006"
        ltch_output = pypps.ltch_client.process(test_claim_1, drg_output)
        print(ltch_output.model_dump_json(indent=2))
        print("=== End of LTCH Pricer Example ===")
    if pypps.hospice_client is not None:
        print("=== Hospice Pricer Example ===")
        hospice_claim = claim_example()
        hospice_claim.bill_type = "812"
        hospice_claim.patient_status = "40"
        hospice_claim.value_codes.append(ValueCode(code="61", amount=35300.00))
        hospice_claim.value_codes.append(ValueCode(code="G8", amount=35300.00))
        hospice_claim.thru_date = datetime(2025,7,10)
        hospice_claim.los = 10
        hospice_claim.lines.append(LineItem(
            hcpcs="Q5001",
            revenue_code="0651",
            service_date= datetime(2025,7,1),
            units=9,
            charges=10_000.00
        ))
        hospice_claim.lines.append(LineItem(
            hcpcs="G0299",
            revenue_code="0551",
            service_date = datetime(2025,7,1),
            units=3,
            charges=10_000.00
        ))
        hospice_output = pypps.hospice_client.process(hospice_claim)
        print(hospice_output.model_dump_json(indent=2))
        print("=== End of Hospice Pricer Example ===")