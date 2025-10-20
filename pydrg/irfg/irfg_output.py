from typing import Optional
from pydantic import BaseModel
import jpype


class IrfgOutput(BaseModel):
    claim_id: str = ""
    irf_version: Optional[int] = None
    motor_score: Optional[float] = None
    ric: Optional[int] = None
    cmg_group: Optional[str] = None
    error_code: Optional[int] = None
    error_description: Optional[str] = None

    def from_java(self, java_obj: jpype.JObject):
        if java_obj is None:
            return
        self.irf_version = java_obj.getUsedIrfVersion()
        self.motor_score = float(java_obj.getCalculatedMotorScore())
        self.ric = int(java_obj.getCalculatedRic())
        self.cmg_group = str(java_obj.getCmgGroup())
        self.error_code = int(java_obj.getError())
        error_enum = jpype.JClass("gov.cms.grouper.irf.model.Error")
        java_enum = error_enum.getError(self.error_code)
        self.error_description = str(java_enum.getReason())
