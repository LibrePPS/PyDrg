import jpype

class MsdrgHac:
    def __init__(self):
        self.hac_number = None
        self.hac_status = None
        self.hac_list = None
    def from_java(self, java_obj):
        self.hac_number = java_obj.getHacNumber()
        self.hac_status = str(java_obj.getHacStatus().name())
        self.hac_list = str(java_obj.getHacList())
        return self
    def to_json(self):
        return {
            "hac_number": self.hac_number,
            "hac_status": self.hac_status,
            "hac_list": self.hac_list
        }

class MsdrgOutputDxCode:
    def __init__(self):
        self.grouping_impact = None
        self.final_severity_flag = None
        self.initial_severity_flag = None
        self.hac_list = []
        self.poa_error_code = None
        self.recognized_by_grouper = None
    
    def from_java(self, java_obj):
        self.grouping_impact = str(java_obj.getDiagnosisAffectsDrg().name())
        self.final_severity_flag = str(java_obj.getFinalSeverityUsage().name())
        self.initial_severity_flag = str(java_obj.getInitialSeverityUsage().name())
        hac_list = java_obj.getHacs()
        for hac in hac_list:
            hac_obj = MsdrgHac().from_java(hac)
            self.hac_list.append(hac_obj)
        self.poa_error_code = str(java_obj.getPoaErrorCode().name())
        self.recognized_by_grouper = java_obj.isDiagnosisRecognizedByGrouper()
        return self
    
    def to_json(self):
        return {
            "grouping_impact": self.grouping_impact,
            "final_severity_flag": self.final_severity_flag,
            "initial_severity_flag": self.initial_severity_flag,
            "hac_list": [hac.to_json() for hac in self.hac_list],
            "poa_error_code": self.poa_error_code,
            "recognized_by_grouper": self.recognized_by_grouper
        }

class MsdrgGrouperFlags:
    def __init__(self):
        self.admit_dx_grouper_flag = None
        self.final_secondary_dx_cc_mcc_flag = None
        self.initial_secondary_dx_cc_mcc_flag = None
        self.num_hac_categories_satisfied = None
        self.hac_status_value = None
    
    def from_java(self, java_obj):
        self.admit_dx_grouper_flag = str(java_obj.getAdmitDxGrouperFlag().name())
        self.final_secondary_dx_cc_mcc_flag = str(java_obj.getFinalDrgSecondaryDxCcMcc().name())
        self.initial_secondary_dx_cc_mcc_flag = str(java_obj.getInitialDrgSecondaryDxCcMcc().name())
        self.num_hac_categories_satisfied = java_obj.getNumHacCategoriesSatisfied()
        self.hac_status_value = str(java_obj.getHacStatusValue().name())
        return self
    def to_json(self):
        return {
            "admit_dx_grouper_flag": self.admit_dx_grouper_flag,
            "final_secondary_dx_cc_mcc_flag": self.final_secondary_dx_cc_mcc_flag,
            "initial_secondary_dx_cc_mcc_flag": self.initial_secondary_dx_cc_mcc_flag,
            "num_hac_categories_satisfied": self.num_hac_categories_satisfied,
            "hac_status_value": self.hac_status_value
        }

class MsdrgOutputPrCode:
    def __init__(self):
        self.grouping_impact = None
        self.is_or_procedure = None
        self.recognized_by_grouper = None
        self.hac_usage = []

    def from_java(self, java_obj):
        self.grouping_impact = str(java_obj.getGroupingImpact().name())
        self.is_or_procedure = java_obj.isOrProcedure()
        self.recognized_by_grouper = java_obj.isProcedureRecognizedByGrouper()
        hac_usage = java_obj.getHacUsage()
        if hac_usage:
            for hac in hac_usage:
                hac_obj = MsdrgHac().from_java(hac)
                self.hac_usage.append(hac_obj)
        return self
    def to_json(self):
        return {
            "grouping_impact": self.grouping_impact,
            "is_or_procedure": self.is_or_procedure,
            "recognized_by_grouper": self.recognized_by_grouper,
            "hac_usage": [hac.to_json() for hac in self.hac_usage]
        }

class MsdrgOutput:
    def __init__(self):
        self.grouper_flags = MsdrgGrouperFlags()
        self.initial_grc:str = ""
        self.final_grc:str = ""
        self.initial_mdc_value:str = ""
        self.initial_mdc_description:str = ""
        self.initial_drg_value:str = ""
        self.initial_drg_description:str = ""
        self.initial_base_drg_value:str = ""
        self.initial_base_drg_description:str = ""
        self.initial_med_surg_type:str = ""
        self.initial_severity:str = ""
        self.initial_drg_sdx_severity:str = ""
        self.final_mdc_value:str = ""
        self.final_mdc_description:str = ""
        self.final_drg_value:str = ""
        self.final_drg_description:str = ""
        self.final_base_drg_value:str = ""
        self.final_base_drg_description:str = ""
        self.final_med_surg_type:str = ""
        self.final_severity:str = ""
        self.final_drg_sdx_severity:str = ""
        self.hac_status:str = ""
        self.num_hac_categories_satisfied:int = 0
        self.principal_dx_output = MsdrgOutputDxCode()
        self.secondary_dx_outputs = []
        self.procedure_outputs = []
        
    def __str__(self):
        return f"MsdrgOutput(final_drg={self.final_drg_value}, final_mdc={self.final_mdc_value}, final_severity={self.final_severity})"
    
    def __repr__(self):
        return self.__str__()
    
    def to_json(self):
        return {
            "grouper_flags": self.grouper_flags.to_json(),
            "initial_grc": self.initial_grc,
            "final_grc": self.final_grc,
            "initial_mdc_value": self.initial_mdc_value,
            "initial_mdc_description": self.initial_mdc_description,
            "initial_drg_value": self.initial_drg_value,
            "initial_drg_description": self.initial_drg_description,
            "initial_base_drg_value": self.initial_base_drg_value,
            "initial_base_drg_description": self.initial_base_drg_description,
            "initial_med_surg_type": self.initial_med_surg_type,
            "initial_severity": self.initial_severity,
            "initial_drg_sdx_severity": self.initial_drg_sdx_severity,
            "final_mdc_value": self.final_mdc_value,
            "final_mdc_description": self.final_mdc_description,
            "final_drg_value": self.final_drg_value,
            "final_drg_description": self.final_drg_description,
            "final_base_drg_value": self.final_base_drg_value,
            "final_base_drg_description": self.final_base_drg_description,
            "final_med_surg_type": self.final_med_surg_type,
            "final_severity": self.final_severity,
            "final_drg_sdx_severity": self.final_drg_sdx_severity,
            "hac_status": self.hac_status,
            "num_hac_categories_satisfied": self.num_hac_categories_satisfied,
            "principal_dx_output": self.principal_dx_output.to_json(),
            "secondary_dx_outputs": [sdx.to_json() for sdx in self.secondary_dx_outputs],
            "procedure_outputs": [proc.to_json() for proc in self.procedure_outputs]
        }
