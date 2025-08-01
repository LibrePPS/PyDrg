import jpype
from typing import List, Optional
from pydantic import BaseModel, Field

class OppsProcessingInformation(BaseModel):
    """Processing information from IOCE output"""
    claim_id: str = ""
    return_code: int = 0
    lines_processed: int = 0
    internal_version: int = 0
    version: str = ""
    time_started: int = 0
    time_ended: int = 0
    debug_flag: str = ""
    comment_data: str = ""
    
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

class OppsOutputDiagnosisCode(BaseModel):
    """Output for diagnosis codes with associated edits"""
    diagnosis: str = ""
    present_on_admission: str = ""
    edit_list: List[str] = Field(default_factory=list)
    
    def from_java(self, java_obj):
        if java_obj is not None:
            self.diagnosis = str(java_obj.getDiagnosis()) if java_obj.getDiagnosis() else ""
            self.present_on_admission = str(java_obj.getPresentOnAdmission()) if java_obj.getPresentOnAdmission() else ""
            
            self.edit_list = []
            if hasattr(java_obj, 'getEditList') and java_obj.getEditList():
                for edit in java_obj.getEditList():
                    self.edit_list.append(str(edit))
        return self

class OppsOutputHcpcsModifier(BaseModel):
    """Output for HCPCS modifiers with associated edits"""
    hcpcs_modifier: str = ""
    edit_list: List[str] = Field(default_factory=list)
    
    def from_java(self, java_obj):
        if java_obj is not None:
            self.hcpcs_modifier = str(java_obj.getHcpcsModifier()) if java_obj.getHcpcsModifier() else ""
            
            self.edit_list = []
            if hasattr(java_obj, 'getEditList') and java_obj.getEditList():
                for edit in java_obj.getEditList():
                    self.edit_list.append(str(edit))
        return self

class OppsOutputValueCode(BaseModel):
    """Output for value codes"""
    code: str = ""
    value: str = ""
    
    def from_java(self, java_obj):
        if java_obj is not None:
            self.code = str(java_obj.getCode()) if java_obj.getCode() else ""
            self.value = str(java_obj.getValue()) if java_obj.getValue() else ""
        return self

class OppsOutputLineItem(BaseModel):
    """Output for line items with all OPPS processing results"""
    service_date: str = ""
    revenue_code: str = ""
    hcpcs: str = ""
    units_input: str = ""
    charge: str = ""
    action_flag_input: str = ""
    
    action_flag_output: str = ""
    rejection_denial_flag: str = ""
    payment_method_flag: str = ""
    hcpcs_apc: str = ""
    payment_apc: str = ""
    units_output: str = ""
    status_indicator: str = ""
    payment_indicator: str = ""
    packaging_flag: str = ""
    payment_adjustment_flag01: str = ""
    payment_adjustment_flag02: str = ""
    discounting_formula: str = ""
    composite_adjustment_flag: str = ""
    
    hcpcs_modifier_input_list: List[OppsOutputHcpcsModifier] = Field(default_factory=list)
    hcpcs_modifier_output_list: List[OppsOutputHcpcsModifier] = Field(default_factory=list)
    
    hcpcs_edit_list: List[str] = Field(default_factory=list)
    revenue_edit_list: List[str] = Field(default_factory=list)
    service_date_edit_list: List[str] = Field(default_factory=list)
    
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
            
            self.hcpcs_modifier_input_list = []  # Clear before populating
            if hasattr(java_obj, 'getHcpcsModifierInputList') and java_obj.getHcpcsModifierInputList():
                for modifier in java_obj.getHcpcsModifierInputList():
                    self.hcpcs_modifier_input_list.append(OppsOutputHcpcsModifier().from_java(modifier))
            
            self.hcpcs_modifier_output_list = []  # Clear before populating
            if hasattr(java_obj, 'getHcpcsModifierOutputList') and java_obj.getHcpcsModifierOutputList():
                for modifier in java_obj.getHcpcsModifierOutputList():
                    self.hcpcs_modifier_output_list.append(OppsOutputHcpcsModifier().from_java(modifier))
            
            self.hcpcs_edit_list = []  # Clear before populating
            if hasattr(java_obj, 'getHcpcsEditList') and java_obj.getHcpcsEditList():
                for edit in java_obj.getHcpcsEditList():
                    self.hcpcs_edit_list.append(str(edit))
            
            self.revenue_edit_list = []  # Clear before populating
            if hasattr(java_obj, 'getRevenueEditList') and java_obj.getRevenueEditList():
                for edit in java_obj.getRevenueEditList():
                    self.revenue_edit_list.append(str(edit))
            
            self.service_date_edit_list = []  # Clear before populating
            if hasattr(java_obj, 'getServiceDateEditList') and java_obj.getServiceDateEditList():
                for edit in java_obj.getServiceDateEditList():
                    self.service_date_edit_list.append(str(edit))
        
        return self

class OppsOutput(BaseModel):
    """Main OPPS output class containing all processing results"""
    processing_information: OppsProcessingInformation = Field(default_factory=OppsProcessingInformation)
    
    version: str = ""
    claim_processed_flag: str = ""
    apc_return_buffer_flag: str = ""
    nopps_bill_flag: str = ""
    
    claim_disposition: str = ""
    claim_rejection_disposition: str = ""
    claim_denial_disposition: str = ""
    claim_return_to_provider_disposition: str = ""
    claim_suspension_disposition: str = ""
    line_rejection_disposition: str = ""
    line_denial_disposition: str = ""

    claim_rejection_edit_list: List[str] = Field(default_factory=list)
    claim_denial_edit_list: List[str] = Field(default_factory=list)
    claim_return_to_provider_edit_list: List[str] = Field(default_factory=list)
    claim_suspension_edit_list: List[str] = Field(default_factory=list)
    line_rejection_edit_list: List[str] = Field(default_factory=list)
    line_denial_edit_list: List[str] = Field(default_factory=list)
    
    condition_code_output_list: List[str] = Field(default_factory=list)
    value_code_output_list: List[OppsOutputValueCode] = Field(default_factory=list)
    
    principal_diagnosis_code: OppsOutputDiagnosisCode = Field(default_factory=OppsOutputDiagnosisCode)
    reason_for_visit_diagnosis_code_list: List[OppsOutputDiagnosisCode] = Field(default_factory=list)
    secondary_diagnosis_code_list: List[OppsOutputDiagnosisCode] = Field(default_factory=list)
    
    line_item_list: List[OppsOutputLineItem] = Field(default_factory=list)
    
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
            
            self.claim_rejection_edit_list = []  # Clear before populating
            if hasattr(java_claim, 'getClaimRejectionEditList') and java_claim.getClaimRejectionEditList():
                for edit in java_claim.getClaimRejectionEditList():
                    self.claim_rejection_edit_list.append(str(edit))
            
            self.claim_denial_edit_list = []  # Clear before populating
            if hasattr(java_claim, 'getClaimDenialEditList') and java_claim.getClaimDenialEditList():
                for edit in java_claim.getClaimDenialEditList():
                    self.claim_denial_edit_list.append(str(edit))
            
            self.claim_return_to_provider_edit_list = []  # Clear before populating
            if hasattr(java_claim, 'getClaimReturnToProviderEditList') and java_claim.getClaimReturnToProviderEditList():
                for edit in java_claim.getClaimReturnToProviderEditList():
                    self.claim_return_to_provider_edit_list.append(str(edit))
            
            self.claim_suspension_edit_list = []  # Clear before populating
            if hasattr(java_claim, 'getClaimSuspensionEditList') and java_claim.getClaimSuspensionEditList():
                for edit in java_claim.getClaimSuspensionEditList():
                    self.claim_suspension_edit_list.append(str(edit))
            
            self.line_rejection_edit_list = []  # Clear before populating
            if hasattr(java_claim, 'getLineRejectionEditList') and java_claim.getLineRejectionEditList():
                for edit in java_claim.getLineRejectionEditList():
                    self.line_rejection_edit_list.append(str(edit))
            
            self.line_denial_edit_list = []  # Clear before populating
            if hasattr(java_claim, 'getLineDenialEditList') and java_claim.getLineDenialEditList():
                for edit in java_claim.getLineDenialEditList():
                    self.line_denial_edit_list.append(str(edit))
            
            self.condition_code_output_list = []  # Clear before populating
            if hasattr(java_claim, 'getConditionCodeOutputList') and java_claim.getConditionCodeOutputList():
                for code in java_claim.getConditionCodeOutputList():
                    self.condition_code_output_list.append(str(code))
            
            self.value_code_output_list = []  # Clear before populating
            if hasattr(java_claim, 'getValueCodeOutputList') and java_claim.getValueCodeOutputList():
                for value_code in java_claim.getValueCodeOutputList():
                    val_code = OppsOutputValueCode().from_java(value_code)
                    if val_code.code != "" or val_code.value != "":
                        self.value_code_output_list.append(val_code)

            if hasattr(java_claim, 'getPrincipalDiagnosisCode') and java_claim.getPrincipalDiagnosisCode():
                self.principal_diagnosis_code.from_java(java_claim.getPrincipalDiagnosisCode())
            
            self.reason_for_visit_diagnosis_code_list = []  # Clear before populating
            if hasattr(java_claim, 'getReasonForVisitDiagnosisCodeList') and java_claim.getReasonForVisitDiagnosisCodeList():
                for dx in java_claim.getReasonForVisitDiagnosisCodeList():
                    self.reason_for_visit_diagnosis_code_list.append(OppsOutputDiagnosisCode().from_java(dx))
            
            self.secondary_diagnosis_code_list = []  # Clear before populating
            if hasattr(java_claim, 'getSecondaryDiagnosisCodeList') and java_claim.getSecondaryDiagnosisCodeList():
                for dx in java_claim.getSecondaryDiagnosisCodeList():
                    self.secondary_diagnosis_code_list.append(OppsOutputDiagnosisCode().from_java(dx))
            
            self.line_item_list = []  # Clear before populating
            if hasattr(java_claim, 'getLineItemList') and java_claim.getLineItemList():
                for line in java_claim.getLineItemList():
                    self.line_item_list.append(OppsOutputLineItem().from_java(line))
        
        except Exception as e:
            print(f"Warning: Could not extract some OPPS output fields: {e}")
        
        return self
    
    def __str__(self):
        return f"OppsOutput(return_code={self.processing_information.return_code}, lines_processed={self.processing_information.lines_processed})"
    
    def __repr__(self):
        return self.__str__()
