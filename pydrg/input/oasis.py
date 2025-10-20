from typing import Optional
from pydantic import BaseModel


class OasisAssessment(BaseModel):
    fall_risk: Optional[int] = 0
    weight_loss: Optional[int] = 0
    multiple_hospital_stays: Optional[int] = 0
    multiple_ed_visits: Optional[int] = 0
    mental_behavior_risk: Optional[int] = 0
    compliance_risk: Optional[int] = 0
    five_or_more_meds: Optional[int] = 0
    exhaustion: Optional[int] = 0
    other_risk: Optional[int] = 0
    none_of_above: Optional[int] = 0
    grooming: Optional[str] = "00"
    dress_upper: Optional[str] = "00"
    dress_lower: Optional[str] = "00"
    bathing: Optional[str] = "00"
    toileting: Optional[str] = "00"
    transferring: Optional[str] = "00"
    ambulation: Optional[str] = "00"
