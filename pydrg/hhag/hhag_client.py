import jpype
from pydrg.input.claim import Claim
from pydrg.hhag.hhag_output import HhagOutput


class HhagClient:
    def __init__(self):
        if not jpype.isJVMStarted():
            raise RuntimeError(
                "JVM is not started. Please start the JVM before using HhagClient."
            )
        self.load_classes()
        self.load_hhag_grouper()

    def load_classes(self):
        self.hhag_claim_class = jpype.JClass("gov.cms.hh.data.exchange.ClaimContainer")
        self.hhag_dx_class = jpype.JClass("gov.cms.hh.data.exchange.DxContainer")
        self.hhag_grouper_class = jpype.JClass("gov.cms.hh.grouper.GrouperFactory")
        self.hhag_edit_collection_class = jpype.JClass(
            "gov.cms.hh.logic.validation.EditCollection"
        )
        self.hhag_edit_class = jpype.JClass("gov.cms.hh.logic.validation.Edit")
        self.hhag_edit_type_enum = jpype.JClass(
            "gov.cms.hh.data.meta.enumer.EditType_EN"
        )
        self.hhag_edit_severity_enum = jpype.JClass("java.util.logging.Level")
        self.hhag_edit_id_enum = jpype.JClass("gov.cms.hh.data.meta.enumer.EditId_EN")

    def load_hhag_grouper(self):
        self.hhag_grouper_obj = self.hhag_grouper_class(True)

    def create_input_claim(self, claim: Claim) -> jpype.JObject:
        claim_obj = self.hhag_claim_class()
        claim_obj.setClaimId(claim.claimid)

        if claim.from_date is not None:
            if claim.admit_date is not None:
                if claim.admit_date == claim.from_date:
                    claim_obj.setPeriodTiming("1")
                else:
                    claim_obj.setPeriodTiming("2")
            else:
                claim_obj.setPeriodTiming("2")
            claim_obj.setFromDate(claim.from_date.strftime("%Y%m%d"))
        else:
            raise ValueError("Claim 'from_date' is required.")

        if claim.thru_date is not None:
            claim_obj.setThroughDate(claim.thru_date.strftime("%Y%m%d"))
        else:
            raise ValueError("Claim 'thru_date' is required.")

        for code in claim.occurrence_codes:
            if code.code == "61":
                claim_obj.setReferralSource("61")
            elif code.code == "62":
                claim_obj.setReferralSource("62")

        if claim.principal_dx is not None:
            claim_obj.setPdx(claim.principal_dx.code, claim.principal_dx.poa.name)

        for dx in claim.secondary_dxs:
            claim_obj.addSdx(dx.code, dx.poa.name)

        if "oasis" not in claim.additional_data:
            self.set_oasis_defaults(claim_obj)
        else:
            claim_obj.setHospRiskHistoryFalls(
                str(int(claim.additional_data["oasis"].get("fall_risk", "0")))
            )
            claim_obj.setHospRiskWeightLoss(
                str(int(claim.additional_data["oasis"].get("weight_loss", "0")))
            )
            claim_obj.setHospRiskMultiHospital(
                str(
                    int(
                        claim.additional_data["oasis"].get(
                            "multiple_hospital_stays", "0"
                        )
                    )
                )
            )
            claim_obj.setHospRiskMultiEdVisit(
                str(int(claim.additional_data["oasis"].get("multiple_ed_visits", "0")))
            )
            claim_obj.setHospRiskMentalBehavDecl(
                str(
                    int(claim.additional_data["oasis"].get("mental_behavior_risk", "0"))
                )
            )
            claim_obj.setHospRiskCompliance(
                str(int(claim.additional_data["oasis"].get("compliance_risk", "0")))
            )
            claim_obj.setHospRiskFiveMoreMeds(
                str(int(claim.additional_data["oasis"].get("five_or_more_meds", "0")))
            )
            claim_obj.setHospRiskExhaustion(
                str(int(claim.additional_data["oasis"].get("exhaustion", "0")))
            )
            claim_obj.setHospRiskOtherRisk(
                str(int(claim.additional_data["oasis"].get("other_risk", "0")))
            )
            claim_obj.setHospRiskNoneAbove(
                str(int(claim.additional_data["oasis"].get("none_of_above", "0")))
            )
            # ------------------Categories above this line should technically be booleans but we'll allow integers--------------------------------------
            # ------------------Below this line are true strings----------------------------------------------------------------------------------------
            claim_obj.setGrooming(claim.additional_data["oasis"].get("grooming", "00"))
            claim_obj.setDressUpper(
                claim.additional_data["oasis"].get("dress_upper", "00")
            )
            claim_obj.setDressLower(
                claim.additional_data["oasis"].get("dress_lower", "00")
            )
            claim_obj.setBathing(claim.additional_data["oasis"].get("bathing", "00"))
            claim_obj.setToileting(
                claim.additional_data["oasis"].get("toileting", "00")
            )
            claim_obj.setTransferring(
                claim.additional_data["oasis"].get("transferring", "00")
            )
            claim_obj.setAmbulation(
                claim.additional_data["oasis"].get("ambulation", "00")
            )
        return claim_obj

    def set_oasis_defaults(self, claim_obj: jpype.JObject) -> None:
        claim_obj.setHospRiskHistoryFalls("0")
        claim_obj.setHospRiskWeightLoss("0")
        claim_obj.setHospRiskMultiHospital("0")
        claim_obj.setHospRiskMultiEdVisit("0")
        claim_obj.setHospRiskMentalBehavDecl("0")
        claim_obj.setHospRiskCompliance("0")
        claim_obj.setHospRiskFiveMoreMeds("0")
        claim_obj.setHospRiskExhaustion("0")
        claim_obj.setHospRiskOtherRisk("0")
        claim_obj.setHospRiskNoneAbove("1")
        claim_obj.setGrooming("00")
        claim_obj.setDressUpper("00")
        claim_obj.setDressLower("00")
        claim_obj.setBathing("00")
        claim_obj.setToileting("00")
        claim_obj.setTransferring("00")
        claim_obj.setAmbulation("00")

    def process(self, claim: Claim):
        claim_obj = self.create_input_claim(claim)
        self.hhag_grouper_obj.group(claim_obj)
        hhag_output = HhagOutput()
        hhag_output.from_java(claim_obj)
        return hhag_output
