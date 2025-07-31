import jpype

class OppsProcessingInformation:
    """Processing information from IOCE output"""
    def __init__(self):
        self.claim_id = ""
        self.return_code = 0
        self.lines_processed = 0
        self.internal_version = 0
        self.version = ""
        self.time_started = 0
        self.time_ended = 0
        self.debug_flag = ""
        self.comment_data = ""
    
    def from_java(self, java_obj):
        if java_obj is not None:
            self.claim_id = str(java_obj.getClaimId()) if java_obj.getClaimId() else ""
            self.return_code = java_obj.getReturnCode() if java_obj.getReturnCode() else 0
            self.lines_processed = java_obj.getLinesProcessed() if java_obj.getLinesProcessed() else 0
            self.internal_version = java_obj.getInternalVersion() if hasattr(java_obj, 'getInternalVersion') else 0
            self.version = str(java_obj.getVersion()) if java_obj.getVersion() else ""
            self.time_started = java_obj.getTimeStarted() if java_obj.getTimeStarted() else 0
            self.time_ended = java_obj.getTimeEnded() if java_obj.getTimeEnded() else 0
            self.debug_flag = str(java_obj.getDebugFlag()) if java_obj.getDebugFlag() else ""
            self.comment_data = str(java_obj.getCommentData()) if java_obj.getCommentData() else ""
        return self
    
    def to_json(self):
        return {
            "claim_id": self.claim_id,
            "return_code": self.return_code,
            "lines_processed": self.lines_processed,
            "internal_version": self.internal_version,
            "version": self.version,
            "time_started": self.time_started,
            "time_ended": self.time_ended,
            "debug_flag": self.debug_flag,
            "comment_data": self.comment_data
        }

class OppsOutputDiagnosisCode:
    """Output for diagnosis codes with associated edits"""
    def __init__(self):
        self.diagnosis = ""
        self.present_on_admission = ""
        self.edit_list = []
    
    def from_java(self, java_obj):
        if java_obj is not None:
            self.diagnosis = str(java_obj.getDiagnosis()) if java_obj.getDiagnosis() else ""
            self.present_on_admission = str(java_obj.getPresentOnAdmission()) if java_obj.getPresentOnAdmission() else ""
            
            self.edit_list = []
            if hasattr(java_obj, 'getEditList') and java_obj.getEditList():
                for edit in java_obj.getEditList():
                    self.edit_list.append(str(edit))
        return self
    
    def to_json(self):
        return {
            "diagnosis": self.diagnosis,
            "present_on_admission": self.present_on_admission,
            "edit_list": self.edit_list
        }

class OppsOutputHcpcsModifier:
    """Output for HCPCS modifiers with associated edits"""
    def __init__(self):
        self.hcpcs_modifier = ""
        self.edit_list = []
    
    def from_java(self, java_obj):
        if java_obj is not None:
            self.hcpcs_modifier = str(java_obj.getHcpcsModifier()) if java_obj.getHcpcsModifier() else ""
            
            self.edit_list = []
            if hasattr(java_obj, 'getEditList') and java_obj.getEditList():
                for edit in java_obj.getEditList():
                    self.edit_list.append(str(edit))
        return self
    
    def to_json(self):
        return {
            "hcpcs_modifier": self.hcpcs_modifier,
            "edit_list": self.edit_list
        }

class OppsOutputValueCode:
    """Output for value codes"""
    def __init__(self):
        self.code = ""
        self.value = ""
    
    def from_java(self, java_obj):
        if java_obj is not None:
            self.code = str(java_obj.getCode()) if java_obj.getCode() else ""
            self.value = str(java_obj.getValue()) if java_obj.getValue() else ""
        return self
    
    def to_json(self):
        return {
            "code": self.code,
            "value": self.value
        }

class OppsOutputLineItem:
    """Output for line items with all OPPS processing results"""
    def __init__(self):
        self.service_date = ""
        self.revenue_code = ""
        self.hcpcs = ""
        self.units_input = ""
        self.charge = ""
        self.action_flag_input = ""
        
        self.action_flag_output = ""
        self.rejection_denial_flag = ""
        self.payment_method_flag = ""
        self.hcpcs_apc = ""
        self.payment_apc = ""
        self.units_output = ""
        self.status_indicator = ""
        self.payment_indicator = ""
        self.packaging_flag = ""
        self.payment_adjustment_flag01 = ""
        self.payment_adjustment_flag02 = ""
        self.discounting_formula = ""
        self.composite_adjustment_flag = ""
        
        self.hcpcs_modifier_input_list = []
        self.hcpcs_modifier_output_list = []
        
        self.hcpcs_edit_list = []
        self.revenue_edit_list = []
        self.service_date_edit_list = []
    
    def from_java(self, java_obj):
        if java_obj is not None:
            self.service_date = str(java_obj.getServiceDate()) if java_obj.getServiceDate() else ""
            self.revenue_code = str(java_obj.getRevenueCode()) if java_obj.getRevenueCode() else ""
            self.hcpcs = str(java_obj.getHcpcs()) if java_obj.getHcpcs() else ""
            self.units_input = str(java_obj.getUnitsInput()) if java_obj.getUnitsInput() else ""
            self.charge = str(java_obj.getCharge()) if java_obj.getCharge() else ""
            self.action_flag_input = str(java_obj.getActionFlagInput()) if java_obj.getActionFlagInput() else ""
            
            self.action_flag_output = str(java_obj.getActionFlagOutput()) if java_obj.getActionFlagOutput() else ""
            self.rejection_denial_flag = str(java_obj.getRejectionDenialFlag()) if java_obj.getRejectionDenialFlag() else ""
            self.payment_method_flag = str(java_obj.getPaymentMethodFlag()) if java_obj.getPaymentMethodFlag() else ""
            self.hcpcs_apc = str(java_obj.getHcpcsApc()) if java_obj.getHcpcsApc() else ""
            self.payment_apc = str(java_obj.getPaymentApc()) if java_obj.getPaymentApc() else ""
            self.units_output = str(java_obj.getUnitsOutput()) if java_obj.getUnitsOutput() else ""
            self.status_indicator = str(java_obj.getStatusIndicator()) if java_obj.getStatusIndicator() else ""
            self.payment_indicator = str(java_obj.getPaymentIndicator()) if java_obj.getPaymentIndicator() else ""
            self.packaging_flag = str(java_obj.getPackagingFlag()) if java_obj.getPackagingFlag() else ""
            self.payment_adjustment_flag01 = str(java_obj.getPaymentAdjustmentFlag01()) if java_obj.getPaymentAdjustmentFlag01() else ""
            self.payment_adjustment_flag02 = str(java_obj.getPaymentAdjustmentFlag02()) if java_obj.getPaymentAdjustmentFlag02() else ""
            self.discounting_formula = str(java_obj.getDiscountingFormula()) if java_obj.getDiscountingFormula() else ""
            self.composite_adjustment_flag = str(java_obj.getCompositeAdjustmentFlag()) if java_obj.getCompositeAdjustmentFlag() else ""
            
            self.hcpcs_modifier_input_list = []
            if hasattr(java_obj, 'getHcpcsModifierInputList') and java_obj.getHcpcsModifierInputList():
                for modifier in java_obj.getHcpcsModifierInputList():
                    self.hcpcs_modifier_input_list.append(OppsOutputHcpcsModifier().from_java(modifier))
            
            self.hcpcs_modifier_output_list = []
            if hasattr(java_obj, 'getHcpcsModifierOutputList') and java_obj.getHcpcsModifierOutputList():
                for modifier in java_obj.getHcpcsModifierOutputList():
                    self.hcpcs_modifier_output_list.append(OppsOutputHcpcsModifier().from_java(modifier))
            
            self.hcpcs_edit_list = []
            if hasattr(java_obj, 'getHcpcsEditList') and java_obj.getHcpcsEditList():
                for edit in java_obj.getHcpcsEditList():
                    self.hcpcs_edit_list.append(str(edit))
            
            self.revenue_edit_list = []
            if hasattr(java_obj, 'getRevenueEditList') and java_obj.getRevenueEditList():
                for edit in java_obj.getRevenueEditList():
                    self.revenue_edit_list.append(str(edit))
            
            self.service_date_edit_list = []
            if hasattr(java_obj, 'getServiceDateEditList') and java_obj.getServiceDateEditList():
                for edit in java_obj.getServiceDateEditList():
                    self.service_date_edit_list.append(str(edit))
        
        return self
    
    def to_json(self):
        return {
            "service_date": self.service_date,
            "revenue_code": self.revenue_code,
            "hcpcs": self.hcpcs,
            "units_input": self.units_input,
            "charge": self.charge,
            "action_flag_input": self.action_flag_input,
            "action_flag_output": self.action_flag_output,
            "rejection_denial_flag": self.rejection_denial_flag,
            "payment_method_flag": self.payment_method_flag,
            "hcpcs_apc": self.hcpcs_apc,
            "payment_apc": self.payment_apc,
            "units_output": self.units_output,
            "status_indicator": self.status_indicator,
            "payment_indicator": self.payment_indicator,
            "packaging_flag": self.packaging_flag,
            "payment_adjustment_flag01": self.payment_adjustment_flag01,
            "payment_adjustment_flag02": self.payment_adjustment_flag02,
            "discounting_formula": self.discounting_formula,
            "composite_adjustment_flag": self.composite_adjustment_flag,
            "hcpcs_modifier_input_list": [mod.to_json() for mod in self.hcpcs_modifier_input_list],
            "hcpcs_modifier_output_list": [mod.to_json() for mod in self.hcpcs_modifier_output_list],
            "hcpcs_edit_list": self.hcpcs_edit_list,
            "revenue_edit_list": self.revenue_edit_list,
            "service_date_edit_list": self.service_date_edit_list
        }

class OppsOutput:
    """Main OPPS output class containing all processing results"""
    def __init__(self):
        self.processing_information = OppsProcessingInformation()
        
        self.version = ""
        self.claim_processed_flag = ""
        self.apc_return_buffer_flag = ""
        self.nopps_bill_flag = ""
        
        self.claim_disposition = ""
        self.claim_rejection_disposition = ""
        self.claim_denial_disposition = ""
        self.claim_return_to_provider_disposition = ""
        self.claim_suspension_disposition = ""
        self.line_rejection_disposition = ""
        self.line_denial_disposition = ""

        self.claim_rejection_edit_list = []
        self.claim_denial_edit_list = []
        self.claim_return_to_provider_edit_list = []
        self.claim_suspension_edit_list = []
        self.line_rejection_edit_list = []
        self.line_denial_edit_list = []
        
        self.condition_code_output_list = []
        self.value_code_output_list = []
        
        self.principal_diagnosis_code = OppsOutputDiagnosisCode()
        self.reason_for_visit_diagnosis_code_list = []
        self.secondary_diagnosis_code_list = []
        
        self.line_item_list = []
    
    def from_java(self, java_claim):
        """Extract all output data from the processed Java OceClaim object"""
        if java_claim is None:
            return self
        
        try:
            if hasattr(java_claim, 'getProcessingInformation') and java_claim.getProcessingInformation():
                self.processing_information.from_java(java_claim.getProcessingInformation())
            
            self.version = str(java_claim.getVersion()) if java_claim.getVersion() else ""
            self.claim_processed_flag = str(java_claim.getClaimProcessedFlag()) if java_claim.getClaimProcessedFlag() else ""
            self.apc_return_buffer_flag = str(java_claim.getApcReturnBufferFlag()) if java_claim.getApcReturnBufferFlag() else ""
            self.nopps_bill_flag = str(java_claim.getNoppsBillFlag()) if java_claim.getNoppsBillFlag() else ""
            
            self.claim_disposition = str(java_claim.getClaimDisposition()) if java_claim.getClaimDisposition() else ""
            self.claim_rejection_disposition = str(java_claim.getClaimRejectionDisposition()) if java_claim.getClaimRejectionDisposition() else ""
            self.claim_denial_disposition = str(java_claim.getClaimDenialDisposition()) if java_claim.getClaimDenialDisposition() else ""
            self.claim_return_to_provider_disposition = str(java_claim.getClaimReturnToProviderDisposition()) if java_claim.getClaimReturnToProviderDisposition() else ""
            self.claim_suspension_disposition = str(java_claim.getClaimSuspensionDisposition()) if java_claim.getClaimSuspensionDisposition() else ""
            self.line_rejection_disposition = str(java_claim.getLineRejectionDisposition()) if java_claim.getLineRejectionDisposition() else ""
            self.line_denial_disposition = str(java_claim.getLineDenialDisposition()) if java_claim.getLineDenialDisposition() else ""
            
            self.claim_rejection_edit_list = []
            if hasattr(java_claim, 'getClaimRejectionEditList') and java_claim.getClaimRejectionEditList():
                for edit in java_claim.getClaimRejectionEditList():
                    self.claim_rejection_edit_list.append(str(edit))
            
            self.claim_denial_edit_list = []
            if hasattr(java_claim, 'getClaimDenialEditList') and java_claim.getClaimDenialEditList():
                for edit in java_claim.getClaimDenialEditList():
                    self.claim_denial_edit_list.append(str(edit))
            
            self.claim_return_to_provider_edit_list = []
            if hasattr(java_claim, 'getClaimReturnToProviderEditList') and java_claim.getClaimReturnToProviderEditList():
                for edit in java_claim.getClaimReturnToProviderEditList():
                    self.claim_return_to_provider_edit_list.append(str(edit))
            
            self.claim_suspension_edit_list = []
            if hasattr(java_claim, 'getClaimSuspensionEditList') and java_claim.getClaimSuspensionEditList():
                for edit in java_claim.getClaimSuspensionEditList():
                    self.claim_suspension_edit_list.append(str(edit))
            
            self.line_rejection_edit_list = []
            if hasattr(java_claim, 'getLineRejectionEditList') and java_claim.getLineRejectionEditList():
                for edit in java_claim.getLineRejectionEditList():
                    self.line_rejection_edit_list.append(str(edit))
            
            self.line_denial_edit_list = []
            if hasattr(java_claim, 'getLineDenialEditList') and java_claim.getLineDenialEditList():
                for edit in java_claim.getLineDenialEditList():
                    self.line_denial_edit_list.append(str(edit))
            
            self.condition_code_output_list = []
            if hasattr(java_claim, 'getConditionCodeOutputList') and java_claim.getConditionCodeOutputList():
                for code in java_claim.getConditionCodeOutputList():
                    self.condition_code_output_list.append(str(code))
            
            self.value_code_output_list = []
            if hasattr(java_claim, 'getValueCodeOutputList') and java_claim.getValueCodeOutputList():
                for value_code in java_claim.getValueCodeOutputList():
                    self.value_code_output_list.append(OppsOutputValueCode().from_java(value_code))
            
            if hasattr(java_claim, 'getPrincipalDiagnosisCode') and java_claim.getPrincipalDiagnosisCode():
                self.principal_diagnosis_code.from_java(java_claim.getPrincipalDiagnosisCode())
            
            self.reason_for_visit_diagnosis_code_list = []
            if hasattr(java_claim, 'getReasonForVisitDiagnosisCodeList') and java_claim.getReasonForVisitDiagnosisCodeList():
                for dx in java_claim.getReasonForVisitDiagnosisCodeList():
                    self.reason_for_visit_diagnosis_code_list.append(OppsOutputDiagnosisCode().from_java(dx))
            
            self.secondary_diagnosis_code_list = []
            if hasattr(java_claim, 'getSecondaryDiagnosisCodeList') and java_claim.getSecondaryDiagnosisCodeList():
                for dx in java_claim.getSecondaryDiagnosisCodeList():
                    self.secondary_diagnosis_code_list.append(OppsOutputDiagnosisCode().from_java(dx))
            
            self.line_item_list = []
            if hasattr(java_claim, 'getLineItemList') and java_claim.getLineItemList():
                for line in java_claim.getLineItemList():
                    self.line_item_list.append(OppsOutputLineItem().from_java(line))
        
        except Exception as e:
            print(f"Warning: Could not extract some OPPS output fields: {e}")
        
        return self
    
    def to_json(self):
        return {
            "processing_information": self.processing_information.to_json(),
            "version": self.version,
            "claim_processed_flag": self.claim_processed_flag,
            "apc_return_buffer_flag": self.apc_return_buffer_flag,
            "nopps_bill_flag": self.nopps_bill_flag,
            "claim_disposition": self.claim_disposition,
            "claim_rejection_disposition": self.claim_rejection_disposition,
            "claim_denial_disposition": self.claim_denial_disposition,
            "claim_return_to_provider_disposition": self.claim_return_to_provider_disposition,
            "claim_suspension_disposition": self.claim_suspension_disposition,
            "line_rejection_disposition": self.line_rejection_disposition,
            "line_denial_disposition": self.line_denial_disposition,
            "claim_rejection_edit_list": self.claim_rejection_edit_list,
            "claim_denial_edit_list": self.claim_denial_edit_list,
            "claim_return_to_provider_edit_list": self.claim_return_to_provider_edit_list,
            "claim_suspension_edit_list": self.claim_suspension_edit_list,
            "line_rejection_edit_list": self.line_rejection_edit_list,
            "line_denial_edit_list": self.line_denial_edit_list,
            "condition_code_output_list": self.condition_code_output_list,
            "value_code_output_list": [vc.to_json() for vc in self.value_code_output_list],
            "principal_diagnosis_code": self.principal_diagnosis_code.to_json(),
            "reason_for_visit_diagnosis_code_list": [dx.to_json() for dx in self.reason_for_visit_diagnosis_code_list],
            "secondary_diagnosis_code_list": [dx.to_json() for dx in self.secondary_diagnosis_code_list],
            "line_item_list": [line.to_json() for line in self.line_item_list]
        }
    
    def __str__(self):
        return f"OppsOutput(return_code={self.processing_information.return_code}, lines_processed={self.processing_information.lines_processed})"
    
    def __repr__(self):
        return self.__str__()
