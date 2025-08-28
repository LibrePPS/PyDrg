import os
from datetime import datetime

from pydrg.helpers import claim_example, json_claim_example, opps_claim_example
from pydrg.input import (
    LineItem,
    ValueCode,
    Provider,
    DiagnosisCode,
    PoaType,
    OccurrenceCode,
)
from pydrg.pypps import Pypps

if __name__ == "__main__":
    jar_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "jars"))
    db_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "data", "pypps.db")
    )
    pypps = Pypps(
        build_jar_dirs=True, jar_path=jar_path, db_path=db_path, build_db=False
    )  # <--- Set build_db=True to create the database if it does not exist
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
        if test_claim_1.billing_provider is None:
            test_claim_1.billing_provider = Provider()
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
        hospice_claim.thru_date = datetime(2025, 7, 10)
        hospice_claim.los = 10
        hospice_claim.lines.append(
            LineItem(
                hcpcs="Q5001",
                revenue_code="0651",
                service_date=datetime(2025, 7, 1),
                units=9,
                charges=10_000.00,
            )
        )
        hospice_claim.lines.append(
            LineItem(
                hcpcs="G0299",
                revenue_code="0551",
                service_date=datetime(2025, 7, 1),
                units=3,
                charges=10_000.00,
            )
        )
        hospice_output = pypps.hospice_client.process(hospice_claim)
        print(hospice_output.model_dump_json(indent=2))
        print("=== End of Hospice Pricer Example ===")
        print("=== HHA Pricer Example ===")
        if pypps.hha_client is not None:
            claim = claim_example()
            claim.patient.age = 65
            claim.patient.address.zip = "35300"
            claim.from_date = datetime(2025, 1, 1)
            claim.admit_date = datetime(2025, 1, 1)
            claim.thru_date = datetime(2025, 1, 30)
            claim.bill_type = "329"
            claim.los = 30
            claim.principal_dx.code = "I10"
            claim.principal_dx.poa = PoaType.Y
            claim.secondary_dxs.append(DiagnosisCode(code="C50911", poa=PoaType.Y))
            claim.billing_provider.other_id = "047127"
            claim.lines.append(
                LineItem(
                    service_date=datetime(2025, 1, 30), revenue_code="0420", units=20
                )
            )
            claim.lines.append(
                LineItem(
                    service_date=datetime(2025, 1, 29), revenue_code="0430", units=20
                )
            )
            claim.lines.append(
                LineItem(
                    service_date=datetime(2025, 1, 28), revenue_code="0440", units=20
                )
            )
            claim.lines.append(
                LineItem(
                    service_date=datetime(2025, 1, 27), revenue_code="0550", units=20
                )
            )
            claim.occurrence_codes.append(
                OccurrenceCode(code="61", date=datetime(2024, 12, 15))
            )
            claim.additional_data["oasis"] = dict()
            claim.additional_data["oasis"]["fall_risk"] = True
            claim.additional_data["oasis"]["multiple_hospital_stays"] = True
            claim.additional_data["oasis"]["multiple_ed_visits"] = True
            claim.additional_data["oasis"]["mental_behavior_risk"] = False
            claim.additional_data["oasis"]["compliance_risk"] = True
            claim.additional_data["oasis"]["five_or_more_meds"] = True
            claim.additional_data["oasis"]["exhaustion"] = "00"
            claim.additional_data["oasis"]["other_risk"] = False
            claim.additional_data["oasis"]["none_of_above"] = False
            claim.additional_data["oasis"]["weight_loss"] = False
            claim.additional_data["oasis"]["grooming"] = "1"
            claim.additional_data["oasis"]["dress_upper"] = "2"
            claim.additional_data["oasis"]["dress_lower"] = "2"
            claim.additional_data["oasis"]["bathing"] = "0"
            claim.additional_data["oasis"]["toileting"] = "1"
            claim.additional_data["oasis"]["transferring"] = "2"
            claim.additional_data["oasis"]["ambulation"] = "3"
            claim.additional_data["hha"] = dict()
            hhag_output = pypps.hhag_client.process(claim)
            hha_pricer = pypps.hha_client.process(claim, hhag_output)
            print(hha_pricer.model_dump_json(indent=2))
            print("=== End of HHA Pricer Example ===")
