class MsdrgOutput:
    def __init__(self):
        self.grouper_flags = None
        self.initial_grc = None
        self.final_grc = None
        self.initial_mdc_value = None
        self.initial_mdc_description = None
        self.initial_drg_value = None
        self.initial_drg_description = None
        self.initial_base_drg_value = None
        self.initial_base_drg_description = None
        self.initial_med_surg_type = None
        self.initial_severity = None
        self.initial_drg_sdx_severity = None
        self.final_mdc_value = None
        self.final_mdc_description = None
        self.final_drg_value = None
        self.final_drg_description = None
        self.final_base_drg_value = None
        self.final_base_drg_description = None
        self.final_med_surg_type = None
        self.final_severity = None
        self.final_drg_sdx_severity = None
        self.hac_status = None
        self.num_hac_categories_satisfied = None
        self.principal_dx_output = None
        self.secondary_dx_outputs = []
        self.procedure_outputs = []
        
    def __str__(self):
        return f"MsdrgOutput(final_drg={self.final_drg_value}, final_mdc={self.final_mdc_value}, final_severity={self.final_severity})"
    
    def __repr__(self):
        return self.__str__()
