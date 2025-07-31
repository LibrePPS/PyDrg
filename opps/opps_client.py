import jpype
import json
from datetime import datetime
from typing import List
from input.claim import Claim, DiagnosisCode, ProcedureCode, PoaType, ValueCode, LineItem
from opps.opps_output import OppsOutput

class OppsClient:
    """Client for processing claims through the IOCE (Integrated Outpatient Code Editor) software"""
    
    def __init__(self):
        if not jpype.isJVMStarted():
            raise RuntimeError("JVM is not started. Please start the JVM before using OppsClient.")
        self.load_java_classes()
    
    def load_java_classes(self):
        """Load all required Java classes and components"""
        try:
            # Main component classes
            self.ioce_component_class = jpype.JClass("gov.cms.oce.IoceComponent")
            self.ioce_claim_class = jpype.JClass("gov.cms.oce.IoceClaim")
            
            # External model classes
            self.oce_claim_factory_class = jpype.JClass("gov.cms.oce.model.external.OceClaimFactory")
            self.oce_claim_class = jpype.JClass("gov.cms.oce.model.external.OceClaim")
            self.oce_line_item_class = jpype.JClass("gov.cms.oce.model.external.OceLineItem")
            self.oce_diagnosis_code_class = jpype.JClass("gov.cms.oce.model.external.OceDiagnosisCode")
            self.oce_hcpcs_modifier_class = jpype.JClass("gov.cms.oce.model.external.OceHcpcsModifier")
            self.oce_value_code_class = jpype.JClass("gov.cms.oce.model.external.OceValueCode")
            self.oce_processing_info_class = jpype.JClass("gov.cms.oce.model.external.OceProcessingInformation")
            
            # Initialize factory and component
            self.factory = self.oce_claim_factory_class.getInstance()
            self.ioce_component = self.ioce_component_class()
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OPPS Java classes: {e}")
    
    def format_date(self, date_input):
        """Convert date to YYYYMMDD format required by IOCE"""
        if date_input is None:
            return ""
        
        if isinstance(date_input, str):
            # Assume input is in YYYY-MM-DD format
            try:
                date_obj = datetime.strptime(date_input, "%Y-%m-%d")
                return date_obj.strftime("%Y%m%d")
            except ValueError:
                # Try to parse as YYYYMMDD already
                if len(date_input) == 8 and date_input.isdigit():
                    return date_input
                raise ValueError(f"Invalid date format: {date_input}")
        elif isinstance(date_input, datetime):
            return date_input.strftime("%Y%m%d")
        else:
            raise ValueError(f"Unsupported date type: {type(date_input)}")
    
    def format_age(self, age):
        """Format age as 3-digit string"""
        if age is None:
            return "000"
        return f"{int(age):03d}"
    
    def format_sex(self, sex):
        """Format sex as required by IOCE (0=unknown, 1=male, 2=female)"""
        if sex is None:
            return "0"
        sex_str = str(sex).upper()
        if sex_str.startswith("M"):
            return "1"
        elif sex_str.startswith("F"):
            return "2"
        else:
            return "0"
    
    def create_diagnosis_code(self, dx_code):
        """Create Java OceDiagnosisCode from Python DiagnosisCode"""
        if dx_code is None:
            return None
        
        # Remove periods from diagnosis codes
        clean_code = dx_code.code.replace(".", "")
        
        # Convert POA to string
        poa_str = "U"  # Default to "U" (unknown)
        if dx_code.poa == PoaType.Y:
            poa_str = "Y"
        elif dx_code.poa == PoaType.N:
            poa_str = "N"
        elif dx_code.poa == PoaType.W:
            poa_str = "W"
        elif dx_code.poa == PoaType.U:
            poa_str = "U"
        
        return self.factory.createDiagnosisCode(clean_code, poa_str)
    
    def create_hcpcs_modifier(self, modifier_str):
        """Create Java OceHcpcsModifier from string"""
        if modifier_str is None or modifier_str == "":
            return None
        return self.factory.createHcpcsModifier(str(modifier_str))
    
    def create_value_code(self, value_code):
        """Create Java OceValueCode from Python ValueCode"""
        if value_code is None:
            return None
        
        # Format amount as 9-character string with leading zeros
        amount_str = f"{int(value_code.amount * 100):09d}"  # Convert to cents
        return self.factory.createValueCode(value_code.code, amount_str)
    
    def create_line_item(self, line_item):
        """Create Java OceLineItem from Python LineItem"""
        if line_item is None:
            return None
        
        java_line = self.factory.createLineItem()
        
        # Set basic line item fields
        if line_item.service_date:
            java_line.setServiceDate(self.format_date(line_item.service_date))
        
        if line_item.revenue_code:
            java_line.setRevenueCode(str(line_item.revenue_code))
        
        if line_item.hcpcs:
            java_line.setHcpcs(str(line_item.hcpcs))
        
        # Add HCPCS modifiers
        if line_item.modifiers:
            for modifier in line_item.modifiers:
                if modifier:
                    java_line.addHcpcsModifierInput(str(modifier))
        
        # Set units (9-digit string)
        if line_item.units > 0:
            java_line.setUnitsInput(f"{int(line_item.units):09d}")
        else:
            java_line.setUnitsInput("000000001")  # Default to 1
        
        # Set charge (10-digit string with 2 decimal places)
        if line_item.charges > 0:
            charge_str = f"{line_item.charges:.2f}"
            java_line.setCharge(charge_str)
        
        # Set action flag (optional, payer-only field)
        # Default to "0" if not specified
        java_line.setActionFlagInput("0")
        
        return java_line
    
    def create_oce_claim(self, claim):
        """Create Java OceClaim from Python Claim"""
        # Create the claim object
        oce_claim = self.factory.createClaim()
        
        # Set claim identifier
        if claim.claimid:
            oce_claim.setClaimId(str(claim.claimid))
        else:
            oce_claim.setClaimId("DEFAULT_CLAIM_ID")
        
        # Set patient demographics
        if claim.patient:
            oce_claim.setAge(self.format_age(claim.patient.age))
            oce_claim.setSex(self.format_sex(claim.patient.sex))
        else:
            oce_claim.setAge("065")  # Default age
            oce_claim.setSex("0")    # Unknown sex
        
        # Set dates
        if claim.from_date:
            oce_claim.setDateStarted(self.format_date(claim.from_date))
        if claim.thru_date:
            oce_claim.setDateEnded(self.format_date(claim.thru_date))
        if hasattr(claim, 'receipt_date') and claim.receipt_date:
            oce_claim.setReceiptDate(self.format_date(claim.receipt_date))
        
        # Set bill type (3-character)
        if claim.bill_type:
            bill_type_str = str(claim.bill_type).ljust(3, '0')[:3]  # Pad or truncate to 3 chars
            oce_claim.setBillType(bill_type_str)
        else:
            oce_claim.setBillType("131")  # Default outpatient bill type
        
        # Set patient discharge status (2-character)
        if claim.patient_status:
            status_str = str(claim.patient_status).zfill(2)[:2]  # Pad with zeros or truncate
            oce_claim.setPatientStatus(status_str)
        else:
            oce_claim.setPatientStatus("01")  # Default
        
        # Set OPPS flag (1=OPPS, 2=Non-OPPS)
        # For OPPS processing, we default to "1"
        oce_claim.setOppsFlag("1")
        
        # Set provider identifiers
        if claim.billing_provider and claim.billing_provider.npi:
            npi_str = str(claim.billing_provider.npi)[:13]  # Truncate to 13 chars
            oce_claim.setNationalProviderId(npi_str)
        
        # Set CMS certification number (6-character)
        # This might come from provider other_id or additional_data
        if claim.billing_provider and claim.billing_provider.other_id:
            cert_num = str(claim.billing_provider.other_id)[:6]
            oce_claim.setCmsCertificationNumber(cert_num)
        else:
            oce_claim.setCmsCertificationNumber("123456")  # Default
        
        # Add occurrence codes
        if hasattr(claim, 'occurrence_codes') and claim.occurrence_codes:
            for occ_code in claim.occurrence_codes:
                if occ_code and occ_code.code:
                    oce_claim.addOccurrenceCodeInput(str(occ_code.code))
        
        # Add condition codes
        if hasattr(claim, 'cond_codes') and claim.cond_codes:
            for cond_code in claim.cond_codes:
                if cond_code:
                    oce_claim.addConditionCodeInput(str(cond_code))
        
        # Add value codes
        if hasattr(claim, 'value_codes') and claim.value_codes:
            for value_code in claim.value_codes:
                if value_code:
                    java_value_code = self.create_value_code(value_code)
                    if java_value_code:
                        oce_claim.addValueCodeInput(java_value_code)
        
        # Set principal diagnosis
        if claim.principal_dx:
            java_principal_dx = self.create_diagnosis_code(claim.principal_dx)
            if java_principal_dx:
                oce_claim.setPrincipalDiagnosisCode(java_principal_dx)
        
        # Add reason for visit diagnosis (typically same as principal for outpatient)
        if claim.principal_dx:
            java_rfv_dx = self.create_diagnosis_code(claim.principal_dx)
            if java_rfv_dx:
                oce_claim.addReasonForVisitDiagnosisCode(java_rfv_dx)
        
        # Add secondary diagnoses
        if claim.secondary_dxs:
            for secondary_dx in claim.secondary_dxs:
                if secondary_dx:
                    java_secondary_dx = self.create_diagnosis_code(secondary_dx)
                    if java_secondary_dx:
                        oce_claim.addSecondaryDiagnosisCode(java_secondary_dx)
        
        # Add line items
        if claim.lines:
            for line in claim.lines:
                if line:
                    java_line = self.create_line_item(line)
                    if java_line:
                        oce_claim.addLineItem(java_line)
        
        return oce_claim
    
    def process(self, claim):
        """Process a claim through IOCE and return OppsOutput"""
        try:
            # Create Java OceClaim from Python claim
            oce_claim = self.create_oce_claim(claim)
            
            # Create IoceClaim wrapper
            ioce_claim = self.ioce_claim_class(oce_claim)
            
            # Process the claim
            self.ioce_component.process(ioce_claim)
            
            # Get the processed model back
            processed_model = ioce_claim.getModel()
            
            # Extract output
            opps_output = OppsOutput()
            opps_output.from_java(processed_model)
            
            return opps_output
            
        except Exception as e:
            raise RuntimeError(f"Error processing OPPS claim {claim.claimid}: {e}")
    
    def batch_load_claims(self, file_path: str):
        """Load claims from a JSON lines file"""
        list_of_claims = []
        with open(file_path, 'r') as file:
            for line in file:
                try:
                    claim = Claim.from_json(json.loads(line))
                    list_of_claims.append(claim)
                except Exception as e:
                    print(f"Error loading claim: {e}")
        return list_of_claims
    
    def batch_process(self, claims: List[Claim], output_file_path: str):
        """Process a list of claims and write results to file"""
        with open(output_file_path, 'w') as f:
            for claim in claims:
                try:
                    result = self.process(claim)
                    f.write(json.dumps(result.to_json(), indent=2) + '\n')
                except Exception as e:
                    print(f"Error processing claim {claim.claimid}: {e}")
    
    def batch_process_with_stats(self, claims: List[Claim], output_file_path: str):
        """
        Batch process a list of claims with progress bar and statistics.
        Returns dictionary with processing statistics.
        """
        import time
        from collections import Counter
        
        start_time = time.time()
        stats = {
            'total_claims': len(claims),
            'successful_claims': 0,
            'failed_claims': 0,
            'processing_times': [],
            'errors': [],
            'return_code_distribution': Counter(),
            'claim_disposition_distribution': Counter(),
            'avg_processing_time': 0,
            'total_processing_time': 0,
            'fastest_claim': {'time': float('inf'), 'id': None},
            'slowest_claim': {'time': 0, 'id': None}
        }
        
        with open(output_file_path, 'w') as f:
            for claim in claims:
                claim_start = time.time()
                try:
                    result = self.process(claim)
                    claim_time = time.time() - claim_start
                    
                    f.write(json.dumps(result.to_json(), indent=2) + '\n')
                    
                    stats['successful_claims'] += 1
                    stats['processing_times'].append(claim_time)
                    
                    if claim_time < stats['fastest_claim']['time']:
                        stats['fastest_claim'] = {'time': claim_time, 'id': claim.claimid}
                    if claim_time > stats['slowest_claim']['time']:
                        stats['slowest_claim'] = {'time': claim_time, 'id': claim.claimid}
                    
                    # Collect statistics
                    if result.processing_information.return_code:
                        stats['return_code_distribution'][result.processing_information.return_code] += 1
                    if result.claim_disposition:
                        stats['claim_disposition_distribution'][result.claim_disposition] += 1
                        
                except Exception as e:
                    claim_time = time.time() - claim_start
                    stats['failed_claims'] += 1
                    stats['processing_times'].append(claim_time)
                    stats['errors'].append({
                        'claim_id': claim.claimid,
                        'error': str(e),
                        'processing_time': claim_time
                    })
                    print(f"Error processing claim {claim.claimid}: {e}")
        
        end_time = time.time()
        stats['total_processing_time'] = end_time - start_time
        if stats['processing_times']:
            stats['avg_processing_time'] = sum(stats['processing_times']) / len(stats['processing_times'])

        return stats
    
    def get_descriptions(self, claim, result):
        """
        Get human-readable descriptions for codes and values in the result.
        This uses the IOCE component's description methods.
        """
        descriptions = {}
        
        try:
            internal_version = result.processing_information.internal_version
            
            # Get return code description
            if result.processing_information.return_code:
                return_code_desc = self.ioce_component.getLatestErrorDescription(
                    str(result.processing_information.return_code)
                )
                descriptions['return_code'] = str(return_code_desc) if return_code_desc else ""
            
            # Get claim processed flag description
            if result.claim_processed_flag:
                claim_flag_desc = self.ioce_component.getClaimProcessedFlagDescription(
                    result.claim_processed_flag, internal_version
                )
                descriptions['claim_processed_flag'] = str(claim_flag_desc) if claim_flag_desc else ""
            
            # Get disposition descriptions
            if result.claim_disposition:
                claim_disp_desc = self.ioce_component.getClaimDispositionDescription(
                    "1", internal_version
                )
                descriptions['claim_disposition'] = str(claim_disp_desc) if claim_disp_desc else ""
            
            # Get line item descriptions
            for i, line in enumerate(result.line_item_list):
                line_desc = {}
                
                if line.hcpcs:
                    hcpcs_desc = self.ioce_component.getHcpcsDescription(
                        line.hcpcs, internal_version
                    )
                    line_desc['hcpcs'] = str(hcpcs_desc) if hcpcs_desc else ""
                
                if line.hcpcs_apc:
                    apc_desc = self.ioce_component.getApcDescription(
                        line.hcpcs_apc, internal_version
                    )
                    line_desc['hcpcs_apc'] = str(apc_desc) if apc_desc else ""
                
                if line.payment_apc:
                    payment_apc_desc = self.ioce_component.getApcDescription(
                        line.payment_apc, internal_version
                    )
                    line_desc['payment_apc'] = str(payment_apc_desc) if payment_apc_desc else ""
                
                if line.status_indicator:
                    status_desc = self.ioce_component.getStatusIndicatorDescription(
                        line.status_indicator, internal_version
                    )
                    line_desc['status_indicator'] = str(status_desc) if status_desc else ""
                
                descriptions[f'line_{i}'] = line_desc
            
            # Get diagnosis descriptions
            if result.principal_diagnosis_code.diagnosis:
                principal_desc = self.ioce_component.getDiagnosisDescription(
                    result.principal_diagnosis_code.diagnosis, internal_version
                )
                descriptions['principal_diagnosis'] = str(principal_desc) if principal_desc else ""
            
        except Exception as e:
            print(f"Warning: Could not retrieve some descriptions: {e}")
        
        return descriptions
