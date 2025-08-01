from enum import Enum
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator

class PoaType(Enum):
    Y = "Y"
    N = "N"
    W = "W"  # Clinically unable to determine a time of admission
    U = "U"  # Insufficient documentation to determine if present on admission
    ONE = "1"  # Exempt from POA reporting/Unreported/Not used
    E = "E"  # Exempt from POA reporting/Unreported/Not used
    BLANK = ""  # Exempt from POA reporting/Unreported/Not used
    INVALID = "INVALID"  # Invalid

class Address(BaseModel):
    address1: str = ""
    address2: str = ""
    city: str = ""
    state: str = ""
    zip: str = ""
    country: str = ""
    phone: str = ""
    fax: str = ""
    additional_data: Dict[str, Any] = Field(default_factory=dict)

class Patient(BaseModel):
    patient_id: str = ""
    first_name: str = ""
    last_name: str = ""
    middle_name: str = ""
    date_of_birth: Optional[datetime] = None
    medical_record_number: str = ""
    address: Address = Field(default_factory=Address)
    additional_data: Dict[str, Any] = Field(default_factory=dict)
    age: int = 0
    age_days_admit: int = 0
    age_days_discharge: int = 0
    sex: Optional[str] = None

class Provider(BaseModel):
    npi: str = ""
    other_id: str = ""
    facility_name: str = ""
    first_name: str = ""
    last_name: str = ""
    contract_id: int = 0
    address: Address = Field(default_factory=Address)
    additional_data: Dict[str, Any] = Field(default_factory=dict)

class Claim(BaseModel):
    claimid: str = ""
    from_date: Optional[datetime] = None
    thru_date: Optional[datetime] = None
    los: int = 0
    bill_type: str = ""
    patient_status: str = ""
    total_charges: float = 0.0
    cond_codes: List[str] = Field(default_factory=list)
    value_codes: List["ValueCode"] = Field(default_factory=list)
    occurrence_codes: List["OccurrenceCode"] = Field(default_factory=list)
    span_codes: List["SpanCode"] = Field(default_factory=list)
    receipt_date: Optional[datetime] = None
    rfvdx: List[str] = Field(default_factory=list)
    secondary_dxs: List["DiagnosisCode"] = Field(default_factory=list)
    principal_dx: Optional["DiagnosisCode"] = None
    admit_dx: Optional["DiagnosisCode"] = None
    inpatient_pxs: List["ProcedureCode"] = Field(default_factory=list)
    lines: List["LineItem"] = Field(default_factory=list)
    non_covered_days: int = 0
    billing_provider: Optional[Provider] = None
    servicing_provider: Optional[Provider] = None
    patient: Patient = Field(default_factory=Patient)
    additional_data: Dict[str, Any] = Field(default_factory=dict)
    map_flag: bool = False
    admit_date: Optional[datetime] = None
    admission_source: str = ""

class ValueCode(BaseModel):
    code: str = ""
    amount: float = 0.0

class ProcedureCode(BaseModel):
    code: str = ""
    modifier: str = ""
    date: Optional[datetime] = None
    additional_data: Dict[str, Any] = Field(default_factory=dict)

class OccurrenceCode(BaseModel):
    code: str = ""
    date: Optional[datetime] = None

class SpanCode(BaseModel):
    code: str = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class DxType(Enum):
    UNKNOWN = 0
    PRIMARY = 1
    SECONDARY = 2

class DiagnosisCode(BaseModel):
    code: str = ""
    poa: PoaType = PoaType.BLANK
    dx_type: DxType = DxType.UNKNOWN
    
    @field_validator('poa', mode='before')
    @classmethod
    def validate_poa(cls, v):
        if isinstance(v, str):
            for poa_type in PoaType:
                if poa_type.value == v:
                    return poa_type
            return PoaType.BLANK
        elif isinstance(v, PoaType):
            return v
        else:
            return PoaType.BLANK
    
    @field_validator('dx_type', mode='before')
    @classmethod
    def validate_dx_type(cls, v):
        if isinstance(v, str):
            try:
                return DxType[v.upper()]
            except KeyError:
                try:
                    return DxType(int(v))
                except (ValueError, KeyError):
                    return DxType.UNKNOWN
        elif isinstance(v, int):
            try:
                return DxType(v)
            except ValueError:
                return DxType.UNKNOWN
        elif isinstance(v, DxType):
            return v
        else:
            return DxType.UNKNOWN

class LineItem(BaseModel):
    service_date: Optional[datetime] = None
    revenue_code: str = ""
    hcpcs: str = ""
    modifiers: List[str] = Field(default_factory=list)
    units: int = 0
    charges: float = 0.0
    ndc: str = ""
    ndc_units: float = 0.0
    pos: str = ""
    servicing_provider: Provider = Field(default_factory=Provider)