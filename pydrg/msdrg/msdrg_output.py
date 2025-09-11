from typing import List, Optional

from pydantic import BaseModel, Field
from pydrg.converter.icd_converter import ICD10ConvertOutput


class MsdrgHac(BaseModel):
    hac_number: Optional[int] = None
    hac_status: Optional[str] = None
    hac_list: Optional[str] = None

    def from_java(self, java_obj):
        self.hac_number = java_obj.getHacNumber()
        self.hac_status = str(java_obj.getHacStatus().name())
        self.hac_list = str(java_obj.getHacList())
        return self


class MsdrgOutputDxCode(BaseModel):
    grouping_impact: Optional[str] = None
    final_severity_flag: Optional[str] = None
    initial_severity_flag: Optional[str] = None
    hac_list: List[MsdrgHac] = Field(default_factory=list)
    poa_error_code: Optional[str] = None
    recognized_by_grouper: Optional[bool] = None

    def from_java(self, java_obj):
        self.grouping_impact = str(java_obj.getDiagnosisAffectsDrg().name())
        self.final_severity_flag = str(java_obj.getFinalSeverityUsage().name())
        self.initial_severity_flag = str(java_obj.getInitialSeverityUsage().name())
        hac_list = java_obj.getHacs()
        self.hac_list = []  # Clear the list before populating
        for hac in hac_list:
            hac_obj = MsdrgHac().from_java(hac)
            self.hac_list.append(hac_obj)
        self.poa_error_code = str(java_obj.getPoaErrorCode().name())
        self.recognized_by_grouper = java_obj.isDiagnosisRecognizedByGrouper()
        return self


class MsdrgGrouperFlags(BaseModel):
    admit_dx_grouper_flag: Optional[str] = None
    final_secondary_dx_cc_mcc_flag: Optional[str] = None
    initial_secondary_dx_cc_mcc_flag: Optional[str] = None
    num_hac_categories_satisfied: Optional[int] = None
    hac_status_value: Optional[str] = None

    def from_java(self, java_obj):
        self.admit_dx_grouper_flag = str(java_obj.getAdmitDxGrouperFlag().name())
        self.final_secondary_dx_cc_mcc_flag = str(
            java_obj.getFinalDrgSecondaryDxCcMcc().name()
        )
        self.initial_secondary_dx_cc_mcc_flag = str(
            java_obj.getInitialDrgSecondaryDxCcMcc().name()
        )
        self.num_hac_categories_satisfied = java_obj.getNumHacCategoriesSatisfied()
        self.hac_status_value = str(java_obj.getHacStatusValue().name())
        return self


class MsdrgOutputPrCode(BaseModel):
    grouping_impact: Optional[str] = None
    is_or_procedure: Optional[bool] = None
    recognized_by_grouper: Optional[bool] = None
    hac_usage: List[MsdrgHac] = Field(default_factory=list)

    def from_java(self, java_obj):
        self.grouping_impact = str(java_obj.getProcedureAffectsDrg().name())
        self.is_or_procedure = java_obj.isProcedureIsOperatingRoomProcedure()
        self.recognized_by_grouper = java_obj.isProcedureRecognizedByGrouper()
        hac_usage = java_obj.getHacUsage()
        self.hac_usage = []  # Clear the list before populating
        if hac_usage:
            for hac in hac_usage:
                hac_obj = MsdrgHac().from_java(hac)
                self.hac_usage.append(hac_obj)
        return self


class MsdrgOutput(BaseModel):
    claim_id: str = ""
    drg_version: str = ""
    grouper_flags: MsdrgGrouperFlags = Field(default_factory=MsdrgGrouperFlags)
    initial_grc: str = ""
    final_grc: str = ""
    initial_mdc_value: str = ""
    initial_mdc_description: str = ""
    initial_drg_value: str = ""
    initial_drg_description: str = ""
    initial_base_drg_value: str = ""
    initial_base_drg_description: str = ""
    initial_med_surg_type: str = ""
    initial_severity: str = ""
    initial_drg_sdx_severity: str = ""
    final_mdc_value: str = ""
    final_mdc_description: str = ""
    final_drg_value: str = ""
    final_drg_description: str = ""
    final_base_drg_value: str = ""
    final_base_drg_description: str = ""
    final_med_surg_type: str = ""
    final_severity: str = ""
    final_drg_sdx_severity: str = ""
    hac_status: str = ""
    num_hac_categories_satisfied: int = 0
    principal_dx_output: MsdrgOutputDxCode = Field(default_factory=MsdrgOutputDxCode)
    secondary_dx_outputs: List[MsdrgOutputDxCode] = Field(default_factory=list)
    procedure_outputs: List[MsdrgOutputPrCode] = Field(default_factory=list)
    icd10_conversion_output: Optional[ICD10ConvertOutput] = None

    def __str__(self):
        return f"MsdrgOutput(final_drg={self.final_drg_value}, final_mdc={self.final_mdc_value}, final_severity={self.final_severity})"

    def __repr__(self):
        return self.__str__()
