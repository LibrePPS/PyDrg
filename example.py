import os
from datetime import datetime, timedelta

from pydrg.helpers import claim_example, json_claim_example, opps_claim_example
from pydrg.input import (
    LineItem,
    ValueCode,
    Provider,
    DiagnosisCode,
    PoaType,
    OccurrenceCode,
    OasisAssessment,
    IrfPai,
)
from pydrg.pypps import Pypps

if __name__ == "__main__":
    jar_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "jars"))
    db_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "data", "pypps.db")
    )
    pypps = Pypps(
        build_jar_dirs=True, jar_path=jar_path, db_path=db_path, build_db=True
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
            claim.oasis_assessment = OasisAssessment()
            claim.oasis_assessment.fall_risk = True
            claim.oasis_assessment.multiple_hospital_stays = True
            claim.oasis_assessment.multiple_ed_visits = True
            claim.oasis_assessment.mental_behavior_risk = False
            claim.oasis_assessment.compliance_risk = True
            claim.oasis_assessment.five_or_more_meds = True
            claim.oasis_assessment.exhaustion = False
            claim.oasis_assessment.other_risk = False
            claim.oasis_assessment.none_of_above = False
            claim.oasis_assessment.weight_loss = False
            claim.oasis_assessment.grooming = "1"
            claim.oasis_assessment.dress_upper = "2"
            claim.oasis_assessment.dress_lower = "2"
            claim.oasis_assessment.bathing = "0"
            claim.oasis_assessment.toileting = "1"
            claim.oasis_assessment.transferring = "2"
            claim.oasis_assessment.ambulation = "3"
            hhag_output = pypps.hhag_client.process(claim)
            hha_pricer = pypps.hha_client.process(claim, hhag_output)
            print(hha_pricer.model_dump_json(indent=2))
            print("=== End of HHA Pricer Example ===")

        print("===IRF Grouper ===")
        claim.oasis_assessment = None
        claim.billing_provider.other_id = "013025"
        claim.irf_pai = IrfPai()
        claim.principal_dx.code = "D61.03"
        claim.admit_date = datetime(2025, 1, 1)
        claim.thru_date = datetime(2025, 1, 30)
        claim.patient.date_of_birth = datetime(1970, 1, 1)
        claim.secondary_dxs.clear()
        claim.irf_pai.assessment_system = "IRF-PAI"
        claim.irf_pai.transaction_type = 1
        claim.irf_pai.impairment_admit_group_code = "0012.9   "
        claim.irf_pai.eating_self_admsn_cd = "06"
        claim.irf_pai.oral_hygne_admsn_cd = "06"
        claim.irf_pai.toileting_hygne_admsn_cd = "06"
        claim.irf_pai.bathing_hygne_admsn_cd = "06"
        claim.irf_pai.footwear_dressing_cd = "06"
        claim.irf_pai.chair_bed_transfer_cd = "06"
        claim.irf_pai.toilet_transfer_cd = "06"
        claim.irf_pai.walk_10_feet_cd = "06"
        claim.irf_pai.walk_50_feet_cd = "06"
        claim.irf_pai.walk_150_feet_cd = "06"
        claim.irf_pai.step_1_cd = "06"
        claim.irf_pai.urinary_continence_cd = "0"
        claim.irf_pai.bowel_continence_cd = "0"

        irf_output = pypps.irfg_client.process(claim)
        print(irf_output.model_dump_json(indent=2))
        print("=== End of IRF Grouper ===")
        print("=== IRF Pricer Example ===")
        irf_pricer = pypps.irf_client.process(claim, irf_output)
        print(irf_pricer.model_dump_json(indent=2))
        print("=== End of IRF Pricer Example ===")
        print("=== ESRD Pricer Example ===")
        claim.billing_provider.other_id = "012525"
        claim.irf_pai = None
        claim.cond_codes.clear()
        claim.cond_codes.append("74")
        claim.value_codes.clear()
        claim.value_codes.append(ValueCode(code="QH", amount=5000.00))
        start_date = datetime(2025, 1, 1)
        claim.esrd_initial_date = datetime(2025, 1, 1)
        while start_date < datetime(2025, 1, 26):
            line = LineItem()
            line.revenue_code = "0821"
            line.service_date = start_date
            claim.lines.append(line)
            start_date += timedelta(days=1)
        claim.value_codes.append(ValueCode(code="A8", amount=70.0))
        claim.value_codes.append(ValueCode(code="A9", amount=180.0))
        esrd_output = pypps.esrd_client.process(claim)
        print(esrd_output.model_dump_json(indent=2))
        print("=== End ESRD Pricer Example ===")
