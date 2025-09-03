from typing import Optional
from pydantic import BaseModel, field_validator


class IrfPai(BaseModel):
    assessment_system: Optional[str] = "IRF-PAI"
    transaction_type: Optional[int] = 1
    impairment_admit_group_code: Optional[str] = None
    # variable names for assessment items taken from Appendix A of CMG Grouper Program Documentation pdf
    eating_self_admsn_cd: Optional[str] = None
    oral_hygne_admsn_cd: Optional[str] = None
    toileting_hygne_admsn_cd: Optional[str] = None
    bathing_hygne_admsn_cd: Optional[str] = None
    upper_body_dressing_cd: Optional[str] = None
    lower_body_dressing_cd: Optional[str] = None
    footwear_dressing_cd: Optional[str] = None
    sit_to_lying_cd: Optional[str] = None
    lying_to_sit_cd: Optional[str] = None
    sit_to_stand_cd: Optional[str] = None
    chair_bed_transfer_cd: Optional[str] = None
    toilet_transfer_cd: Optional[str] = None
    walk_10_feet_cd: Optional[str] = None
    walk_50_feet_cd: Optional[str] = None
    walk_150_feet_cd: Optional[str] = None
    step_1_cd: Optional[str] = None
    urinary_continence_cd: Optional[str] = None
    bowel_continence_cd: Optional[str] = None

    @field_validator("assessment_system")
    def check_assessment_system(cls, v):
        if v != "IRF-PAI":
            raise ValueError("Invalid assessment system")
        return v

    @field_validator("transaction_type")
    def check_transaction_type(cls, v):
        if v not in [1, 2]:
            raise ValueError("Invalid transaction type")
        return v
