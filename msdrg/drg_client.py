import jpype, json
from datetime import datetime
from input.claim import Claim, DiagnosisCode, ProcedureCode, PoaType
from msdrg.msdrg_output import MsdrgOutput, MsdrgOutputDxCode, MsdrgOutputPrCode
from datetime import datetime
from enum import Enum
from typing import List

MSDRG_VSTART = "400"

class MsdrgAffectDrgOptionFlag(Enum):
    COMPUTE = "COMPUTE"
    DO_NOT_COMPUTE = "DO_NOT_COMPUTE"

class MarkingLogicTieBreaker(Enum):
    CLINICAL_SIGNIFICANCE = "CLINICAL_SIGNIFICANCE"
    CODE_ORDER = "CODE_ORDER"

class MsdrgHospitalStatusOptionFlag(Enum):
    NON_EXEMPT = "NON_EXEMPT"
    EXEMPT = "EXEMPT"
    UNKNOWN = "UNKNOWN"

class DrgClient:
    def __init__(self):
        if not jpype.isJVMStarted():
            raise RuntimeError("JVM is not started")
        self.load_enums()
        self.load_input_classes()
        self.load_drg_groupers()

    def load_enums(self):
        #Get enumeration values needed for DRG Runtime options
        try:
            self.logic_tiebreaker = jpype.JClass("gov.agency.msdrg.model.v2.enumeration.MarkingLogicTieBreaker")
            self.affect_drg_option = jpype.JClass("gov.agency.msdrg.model.v2.enumeration.MsdrgAffectDrgOptionFlag")
            self.drg_status = jpype.JClass("gov.agency.msdrg.model.v2.enumeration.MsdrgDischargeStatus")
            self.hospital_status = jpype.JClass("gov.agency.msdrg.model.v2.enumeration.MsdrgHospitalStatusOptionFlag")
            self.sex = jpype.JClass("gov.agency.msdrg.model.v2.enumeration.MsdrgSex")
            self.poa_values = jpype.JClass("com.mmm.his.cer.foundation.model.GfcPoa")
            self.msdrg_grouping_impact = jpype.JClass("gov.agency.msdrg.model.v2.enumeration.MsdrgGroupingImpact")
            self.poa_error_code = jpype.JClass("gov.agency.msdrg.model.v2.enumeration.MsdrgPoaErrorCode")
            self.msdrg_severity_flag = jpype.JClass("gov.agency.msdrg.model.v2.enumeration.MsdrgCodeSeverityFlag")
            self.msdrg_hac_status = jpype.JClass("gov.agency.msdrg.model.v2.enumeration.MsdrgHacStatus")

        except Exception as e:
            raise RuntimeError(f"Failed to initialize enumerations: {e}")
    
    def load_input_classes(self):
        try:
            self.drg_claim_class = jpype.JClass("gov.agency.msdrg.model.v2.transfer.MsdrgClaim")
            self.drg_input_class = jpype.JClass("gov.agency.msdrg.model.v2.transfer.input.MsdrgInput")
            self.drg_dx_class = jpype.JClass("gov.agency.msdrg.model.v2.transfer.input.MsdrgInputDxCode")
            self.drg_px_class = jpype.JClass("gov.agency.msdrg.model.v2.transfer.input.MsdrgInputPrCode")
            self.array_list_class = jpype.JClass("java.util.ArrayList")
            self.runtime_options_class = jpype.JClass("gov.agency.msdrg.model.v2.RuntimeOptions")
            self.drg_options_class = jpype.JClass("gov.agency.msdrg.model.v2.MsdrgRuntimeOption")
            self.msdrg_option_flags_class = jpype.JClass("gov.agency.msdrg.model.v2.MsdrgOption")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize input classes: {e}")

    def increment_version(self, version):
        """
        If version ends with "1", increment the version by 9.
        If version ends with "0", increment the version by 1.
        """
        if version.endswith("1"):
            return str(int(version) + 9)
        elif version.endswith("0"):
            return str(int(version) + 1)
        return version
    
    def load_drg_groupers(self):
        end_version = self.determine_end_version()
        curr_version = MSDRG_VSTART
        #Initialize the DRG Runtime options Java object
        try:
            self.runtime_options = jpype.JClass("gov.agency.msdrg.model.v2.RuntimeOptions")()
            self.drg_options = jpype.JClass("gov.agency.msdrg.model.v2.MsdrgRuntimeOption")()
            self.msdrg_option_flags = jpype.JClass("gov.agency.msdrg.model.v2.MsdrgOption")
        except:
            raise RuntimeError("Failed to initialize RuntimeOptions")

        #Set the 3 enum values on the RuntimeOptions object
        #default to non-exempt hospital status
        self.runtime_options.setPoaReportingExempt(self.hospital_status.NON_EXEMPT)
        self.runtime_options.setComputeAffectDrg(self.affect_drg_option.COMPUTE)
        self.runtime_options.setMarkingLogicTieBreaker(self.logic_tiebreaker.CLINICAL_SIGNIFICANCE)

        self.drg_options.put(self.msdrg_option_flags.RUNTIME_OPTION_FLAGS, self.runtime_options)

        self.drg_versions = {}
        while int(curr_version) <= int(end_version):
            try:
                drg_component = jpype.JClass(f"gov.agency.msdrg.v{curr_version}.MsdrgComponent")
                self.drg_versions[curr_version] = drg_component(self.drg_options)
                print(f"Loaded DRG version: {curr_version}")
            except Exception as e:
                print(f"Failed to load DRG version {curr_version}: {e}")
                curr_version = self.increment_version(curr_version)
                continue
            curr_version = self.increment_version(curr_version)

    def reconfigure(self, drg_version:str, hospital_status: MsdrgHospitalStatusOptionFlag, affect_drg: MsdrgAffectDrgOptionFlag, logic_tiebreaker: MarkingLogicTieBreaker):
        """
        Reconfigure the DRG client with new options.
        """
        if not isinstance(hospital_status, MsdrgHospitalStatusOptionFlag):
            raise ValueError("Invalid hospital status option")
        if not isinstance(affect_drg, MsdrgAffectDrgOptionFlag):
            raise ValueError("Invalid affect DRG option")
        if not isinstance(logic_tiebreaker, MarkingLogicTieBreaker):
            raise ValueError("Invalid logic tie breaker option")

        runtime_options = self.runtime_options_class()
        match hospital_status:
            case MsdrgHospitalStatusOptionFlag.NON_EXEMPT:
                runtime_options.setPoaReportingExempt(self.hospital_status.NON_EXEMPT)
            case MsdrgHospitalStatusOptionFlag.EXEMPT:
                runtime_options.setPoaReportingExempt(self.hospital_status.EXEMPT)
            case MsdrgHospitalStatusOptionFlag.UNKNOWN:
                runtime_options.setPoaReportingExempt(self.hospital_status.UNKNOWN)
        match affect_drg:
            case MsdrgAffectDrgOptionFlag.COMPUTE:
                runtime_options.setComputeAffectDrg(self.affect_drg_option.COMPUTE)
            case MsdrgAffectDrgOptionFlag.DO_NOT_COMPUTE:
                runtime_options.setComputeAffectDrg(self.affect_drg_option.DO_NOT_COMPUTE)
        match logic_tiebreaker:
            case MarkingLogicTieBreaker.CLINICAL_SIGNIFICANCE:
                runtime_options.setMarkingLogicTieBreaker(self.logic_tiebreaker.CLINICAL_SIGNIFICANCE)
            case MarkingLogicTieBreaker.CODE_ORDER:
                runtime_options.setMarkingLogicTieBreaker(self.logic_tiebreaker.CODE_ORDER)
        if drg_version not in self.drg_versions:
            raise ValueError(f"DRG version {drg_version} is not loaded")
        drg_component = self.drg_versions[drg_version]
        msdrg_runtime_option = self.drg_options_class()
        msdrg_runtime_option.put(self.msdrg_option_flags_class.RUNTIME_OPTION_FLAGS, runtime_options)
        drg_component.reconfigure(msdrg_runtime_option)
        return drg_component

    def determine_end_version(self):
        """
        Max DRG version will be based on the current date
         Step 1.) Version = Year - 1983
         Step 2.) if month is October or later, then add 1 to version, and convert to string that ends with "0"
         Step 3.) if before October, but after March, then convert to string and end with "1"
         Step 4.) if before April, then subtract 1 from version, and convert to string that ends with "0"
         example date: 2025-07-30
         2025 - 1983 = 42
         Month is after March but before October, so we end with "1"
         Version = "421"
        """
        current_year = datetime.now().year
        version = current_year - 1983
        
        if datetime.now().month >= 10:
            version += 1
            return f"{version}0"
        elif datetime.now().month > 3:
            return f"{version}1"
        else:
            version -= 1
            return f"{version}0"
        
    def determine_drg_version(self, date: datetime):
        """
        Determine the DRG version based on the date provided.
        """
        if not isinstance(date, datetime):
            raise ValueError("Date must be a datetime object")
        
        year = date.year - 1983
        if date.month >= 10:
            return f"{year + 1}0"
        elif date.month > 3:
            return f"{year}1"
        else:
            return f"{year - 1}0"
    
    def calculate_age_in_days(self, claim: Claim):
        """
        Calculate the age of the patient in days based on the claim's from_date and patient's date_of_birth.
        """
        if claim.patient.date_of_birth is None:
            return 0
        if isinstance(claim.from_date, str):
            from_date = datetime.strptime(claim.from_date, "%Y-%m-%d")
        elif isinstance(claim.from_date, datetime):
            from_date = claim.from_date
        else:
            raise ValueError("Invalid date format for claim.from_date")
        
        if type(claim.patient.date_of_birth) is str:
            dob = datetime.strptime(claim.patient.date_of_birth, "%Y-%m-%d")
        elif type(claim.patient.date_of_birth) is datetime:
            dob = claim.patient.date_of_birth
        else:
            raise ValueError("Invalid date format for patient.date_of_birth")
        age_in_days = (from_date - dob).days
        return age_in_days if age_in_days > 0 else 0
    
    def create_drg_input(self, claim: Claim):
        input = self.drg_input_class.builder()
        # Set Patient Age
        if claim.patient is not None:
            if claim.patient.age > 0:
                input.withAgeInYears(claim.patient.age)
            elif claim.patient.age == 0 and claim.patient.date_of_birth is not None:
                input.withAgeInYears(0)
                age_in_days = self.calculate_age_in_days(claim)
                input.withAgeInDays(age_in_days)
            else:
                raise ValueError("Patient age or date of birth must be provided")       
        # Set Sex
        if claim.patient.sex is not None:
            if str(claim.patient.sex).upper().startswith("M"):
                input.withSex(self.sex.MALE)
            elif str(claim.patient.sex).upper().startswith("F"):
                input.withSex(self.sex.FEMALE)
            else:
                input.withSex(self.sex.UNKNOWN)
        
        # Set Discharge Status
        if claim.patient_status is not None:
            # try to convert to integer
            try:
                discharge_status = int(claim.patient_status)
                input.withDischargeStatus(self.drg_status.getEnumFromInt(discharge_status))
            except ValueError:
                raise ValueError(f"Invalid patient status: {claim.patient_status}")
        else:
            input.withDischargeStatus(self.drg_status.HOME_SELFCARE_ROUTINE)

        if claim.admit_dx:
            input.withAdmissionDiagnosisCode(
                self.drg_dx_class(claim.admit_dx.code.replace(".", ""), self.poa_values.Y))

        if claim.principal_dx:
            input.withPrincipalDiagnosisCode(
                self.drg_dx_class(claim.principal_dx.code.replace(".", ""), self.poa_values.Y))
        else:
            raise ValueError("Principal diagnosis must be provided")    

        java_dxs = self.array_list_class()
        for dx in claim.secondary_dxs:
            if dx:
                if isinstance(dx, DiagnosisCode):
                    if dx.poa == PoaType.Y:
                        poa_value = self.poa_values.Y
                    elif dx.poa == PoaType.N:
                        poa_value = self.poa_values.N
                    elif dx.poa == PoaType.U:
                        poa_value = self.poa_values.U
                    elif dx.poa == PoaType.W:
                        poa_value = self.poa_values.W
                    java_dxs.add(self.drg_dx_class(dx.code.replace(".", ""), poa_value))
                else:
                    raise ValueError("Secondary diagnosis must be a DiagnosisCode object")
        if len(java_dxs) > 0:
            input.withSecondaryDiagnosisCodes(java_dxs)

        java_pxs = self.array_list_class()
        for px in claim.inpatient_pxs:
            if isinstance(px, ProcedureCode):
                java_pxs.add(self.drg_px_class(px.code))
            else:
                raise ValueError("Inpatient procedure codes must be ProcedureCode objects")
        if len(java_pxs) > 0:
            input.withProcedureCodes(java_pxs)
        return input.build()
        
    def extract_msdrg_output(self, java_drg_output):
        """
        Extract all data from the Java MsdrgOutput object and populate a Python MsdrgOutput object.
        """
        output = MsdrgOutput()
        
        try:
            # Grouper Information
            output.grouper_flags.from_java(java_drg_output.getGrouperFlags())
            output.initial_grc = str(java_drg_output.getInitialGrc().name())
            output.final_grc = str(java_drg_output.getFinalGrc().name())

            # Initial Grouping Results
            initial_mdc = java_drg_output.getInitialMdc()
            if initial_mdc is not None:
                output.initial_mdc_value = str(initial_mdc.getValue())
                output.initial_mdc_description = str(initial_mdc.getDescription())
                
            initial_drg = java_drg_output.getInitialDrg()
            if initial_drg is not None:
                output.initial_drg_value = str(initial_drg.getValue())
                output.initial_drg_description = str(initial_drg.getDescription())
                
            initial_base_drg = java_drg_output.getInitialBaseDrg()
            if initial_base_drg is not None:
                output.initial_base_drg_value = str(initial_base_drg.getValue())
                output.initial_base_drg_description = str(initial_base_drg.getDescription())
                
            # output.initial_med_surg_type = java_drg_output.getInitialMedSurgType()
            output.initial_severity = str(java_drg_output.getInitialSeverity().name())
            output.initial_drg_sdx_severity = str(java_drg_output.getInitialDrgSdxSeverity().name())

            # Final Grouping Results
            final_mdc = java_drg_output.getFinalMdc()
            if final_mdc is not None:
                output.final_mdc_value = str(final_mdc.getValue())
                output.final_mdc_description = str(final_mdc.getDescription())
                
            final_drg = java_drg_output.getFinalDrg()
            if final_drg is not None:
                output.final_drg_value = str(final_drg.getValue())
                output.final_drg_description = str(final_drg.getDescription())
                
            final_base_drg = java_drg_output.getFinalBaseDrg()
            if final_base_drg is not None:
                output.final_base_drg_value = str(final_base_drg.getValue())
                output.final_base_drg_description = str(final_base_drg.getDescription())
                
            # output.final_med_surg_type = java_drg_output.getFinalMedSurgType()
            output.final_severity = str(java_drg_output.getFinalSeverity().name())
            output.final_drg_sdx_severity = str(java_drg_output.getFinalDrgSdxSeverity().name())

            # HAC Information
            output.hac_status = str(java_drg_output.getHacStatus().name())
            output.num_hac_categories_satisfied = java_drg_output.getNumHacCategoriesSatisfied()
            
            # Diagnosis and Procedure Output
            output.principal_dx_output.from_java(java_drg_output.getPdxOutput())
            
            # Secondary diagnosis outputs
            sdx_outputs = java_drg_output.getSdxOutput()
            if sdx_outputs is not None:
                for sdx_output in sdx_outputs:
                    output.secondary_dx_outputs.append(MsdrgOutputDxCode().from_java(sdx_output))
            
            # Procedure outputs
            proc_outputs = java_drg_output.getProcOutput()
            if proc_outputs is not None:
                for proc_output in proc_outputs:
                    output.procedure_outputs.append(MsdrgOutputPrCode().from_java(proc_output))
                    
        except Exception as e:
            print(f"Warning: Could not extract some output fields: {e}")
            
        return output
        
    def process(self, claim: Claim, drg_version=None, hospital_status: MsdrgHospitalStatusOptionFlag = MsdrgHospitalStatusOptionFlag.NON_EXEMPT, affect_drg: MsdrgAffectDrgOptionFlag = MsdrgAffectDrgOptionFlag.COMPUTE, logic_tiebreaker: MarkingLogicTieBreaker = MarkingLogicTieBreaker.CLINICAL_SIGNIFICANCE):
        if drg_version is None:
            """Determine the DRG version based on the claim date"""
            if type(claim.thru_date) is str:
                claim_date = datetime.strptime(claim.thru_date, "%Y-%m-%d")
            elif type(claim.thru_date) is datetime:
                claim_date = claim.thru_date
            else:
                raise ValueError("Invalid date format for claim.thru_date")
            drg_version = self.determine_drg_version(claim_date)
        if drg_version not in self.drg_versions:
            raise ValueError(f"DRG version {drg_version} is not loaded")
        drg_component = self.reconfigure(drg_version, hospital_status, affect_drg, logic_tiebreaker)
        drg_input = self.create_drg_input(claim)
        drg_claim = self.drg_claim_class(drg_input)
        drg_component.process(drg_claim)
        drg_output = drg_claim.getOutput()
        if drg_output.isPresent() == 0:
            raise RuntimeError("DRG output is not present")
        drg_result = drg_output.get()
        
        return self.extract_msdrg_output(drg_result)
    
    def batch_load_claims(self, file_path: str):
        list_of_claims = []
        with open(file_path, 'r') as file:
            for line in file:
                try:
                    claim = Claim.from_json(json.loads(line))
                    list_of_claims.append(claim)
                except Exception as e:
                    print(f"Error loading claim: {e}")
        return list_of_claims
    
    def batch_process(self, claims: List[Claim], output_file_path: str, drg_version=None, hospital_status: MsdrgHospitalStatusOptionFlag = MsdrgHospitalStatusOptionFlag.NON_EXEMPT, affect_drg: MsdrgAffectDrgOptionFlag = MsdrgAffectDrgOptionFlag.COMPUTE, logic_tiebreaker: MarkingLogicTieBreaker = MarkingLogicTieBreaker.CLINICAL_SIGNIFICANCE):
        with open(output_file_path, 'w') as f:
            for claim in claims:
                try:
                    result = self.process(claim, drg_version, hospital_status, affect_drg, logic_tiebreaker)
                    f.write(json.dumps(result.to_json(), indent=2) + '\n')
                except Exception as e:
                    print(f"Error processing claim {claim.claimid}: {e}")

    def batch_process_with_stats(self, claims: List[Claim], output_file_path: str, drg_version=None, hospital_status: MsdrgHospitalStatusOptionFlag = MsdrgHospitalStatusOptionFlag.NON_EXEMPT, affect_drg: MsdrgAffectDrgOptionFlag = MsdrgAffectDrgOptionFlag.COMPUTE, logic_tiebreaker: MarkingLogicTieBreaker = MarkingLogicTieBreaker.CLINICAL_SIGNIFICANCE):
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
            'drg_distribution': Counter(),
            'mdc_distribution': Counter(),
            'severity_distribution': Counter(),
            'hac_status_distribution': Counter(),
            'avg_processing_time': 0,
            'total_processing_time': 0,
            'fastest_claim': {'time': float('inf'), 'id': None},
            'slowest_claim': {'time': 0, 'id': None}
        }
        
        with open(output_file_path, 'w') as f:
            for claim in claims:
                claim_start = time.time()
                try:
                    result = self.process(claim, drg_version, hospital_status, affect_drg, logic_tiebreaker)
                    claim_time = time.time() - claim_start
                    
                    f.write(json.dumps(result.to_json(), indent=2) + '\n')
                    
                    stats['successful_claims'] += 1
                    stats['processing_times'].append(claim_time)
                    
                    if claim_time < stats['fastest_claim']['time']:
                        stats['fastest_claim'] = {'time': claim_time, 'id': claim.claimid}
                    if claim_time > stats['slowest_claim']['time']:
                        stats['slowest_claim'] = {'time': claim_time, 'id': claim.claimid}
                    
                    if result.final_drg_value:
                        stats['drg_distribution'][result.final_drg_value] += 1
                    if result.final_mdc_value:
                        stats['mdc_distribution'][result.final_mdc_value] += 1
                    if result.final_severity:
                        stats['severity_distribution'][result.final_severity] += 1
                    if result.hac_status:
                        stats['hac_status_distribution'][result.hac_status] += 1
                        
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