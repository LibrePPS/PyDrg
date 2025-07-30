from enum import Enum
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

class PoaType(Enum):
    Y = "Y"
    N = "N"
    W = "W"  # Clinically unable to determine a time of admission
    U = "U"  # Insufficient documentation to determine if present on admission
    ONE = "1"  # Exempt from POA reporting/Unreported/Not used
    E = "E"  # Exempt from POA reporting/Unreported/Not used
    BLANK = ""  # Exempt from POA reporting/Unreported/Not used
    INVALID = "INVALID"  # Invalid

class Address:
    def __init__(self, address1="", address2="", city="", state="", zip="", country="", phone="", fax="", additional_data=None):
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.zip = zip
        self.country = country
        self.phone = phone
        self.fax = fax
        self.additional_data = additional_data if additional_data is not None else {}
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Address':
        return cls(
            address1=data.get('address1', ''),
            address2=data.get('address2', ''),
            city=data.get('city', ''),
            state=data.get('state', ''),
            zip=data.get('zip', ''),
            country=data.get('country', ''),
            phone=data.get('phone', ''),
            fax=data.get('fax', ''),
            additional_data=data.get('additional_data', {})
        )
    
    def to_json(self) -> Dict[str, Any]:
        return {
            'address1': self.address1,
            'address2': self.address2,
            'city': self.city,
            'state': self.state,
            'zip': self.zip,
            'country': self.country,
            'phone': self.phone,
            'fax': self.fax,
            'additional_data': self.additional_data
        }

class Patient:
    def __init__(self, patient_id="", first_name="", last_name="", middle_name="", date_of_birth=None, medical_record_number="", address=None, additional_data=None, age=0, age_days_admit=0, age_days_discharge=0, sex=None):
        self.patient_id = patient_id
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.date_of_birth = date_of_birth
        self.medical_record_number = medical_record_number
        self.address = address if address is not None else Address()
        self.additional_data = additional_data if additional_data is not None else {}
        self.age = age
        self.age_days_admit = age_days_admit
        self.age_days_discharge = age_days_discharge
        self.sex = sex
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Patient':
        address_data = data.get('address')
        if address_data:
            if isinstance(address_data, dict):
                address = Address.from_json(address_data)
            elif isinstance(address_data, Address):
                address = address_data
            else:
                address = Address()
        else:
            address = Address()
        
        return cls(
            patient_id=data.get('patient_id', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            middle_name=data.get('middle_name', ''),
            date_of_birth=data.get('date_of_birth'),
            medical_record_number=data.get('medical_record_number', ''),
            address=address,
            additional_data=data.get('additional_data', {}),
            age=data.get('age', 0),
            age_days_admit=data.get('age_days_admit', 0),
            age_days_discharge=data.get('age_days_discharge', 0),
            sex=data.get('sex')
        )
    
    def to_json(self) -> Dict[str, Any]:
        return {
            'patient_id': self.patient_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'middle_name': self.middle_name,
            'date_of_birth': self.date_of_birth,
            'medical_record_number': self.medical_record_number,
            'address': self.address.to_json(),
            'additional_data': self.additional_data,
            'age': self.age,
            'age_days_admit': self.age_days_admit,
            'age_days_discharge': self.age_days_discharge,
            'sex': self.sex
        }

class Provider:
    def __init__(self, npi="", other_id="", facility_name="", first_name="", last_name="", contract_id=0, address=None, additional_data=None):
        self.npi = npi
        self.other_id = other_id
        self.facility_name = facility_name
        self.first_name = first_name
        self.last_name = last_name
        self.contract_id = contract_id
        self.address = address if address is not None else Address()
        self.additional_data = additional_data if additional_data is not None else {}
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Provider':
        address_data = data.get('address')
        if address_data:
            if isinstance(address_data, dict):
                address = Address.from_json(address_data)
            elif isinstance(address_data, Address):
                address = address_data
            else:
                address = Address()
        else:
            address = Address()
        
        return cls(
            npi=data.get('npi', ''),
            other_id=data.get('other_id', ''),
            facility_name=data.get('facility_name', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            contract_id=data.get('contract_id', 0),
            address=address,
            additional_data=data.get('additional_data', {})
        )
    
    def to_json(self) -> Dict[str, Any]:
        return {
            'npi': self.npi,
            'other_id': self.other_id,
            'facility_name': self.facility_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'contract_id': self.contract_id,
            'address': self.address.to_json(),
            'additional_data': self.additional_data
        }

class Claim:
    def __init__(self, claimid="", from_date=None, thru_date=None, los=0, bill_type="", patient_status="", total_charges=0.0, demo_codes=None, cond_codes=None, value_codes=None, occurrence_codes=None, span_codes=None, receipt_date=None, rfvdx=None, secondary_dxs=None, principal_dx=None, admit_dx=None, inpatient_pxs=None, lines=None, modules=None, non_covered_days=0, inpatient=None, outpatient=None, billing_provider=None, servicing_provider=None, review_code="", patient=None, additional_data=None, map_flag=False, hha=None, admit_date=None, hospice=None, snf=None, admission_source="", irf=None):
        self.claimid = claimid
        self.from_date = from_date
        self.thru_date = thru_date
        self.los = los
        self.bill_type = bill_type
        self.patient_status = patient_status
        self.total_charges = total_charges
        self.cond_codes = cond_codes if cond_codes is not None else []
        self.value_codes = value_codes if value_codes is not None else []
        self.occurrence_codes = occurrence_codes if occurrence_codes is not None else []
        self.span_codes = span_codes if span_codes is not None else []
        self.receipt_date = receipt_date
        self.rfvdx = rfvdx if rfvdx is not None else []
        self.secondary_dxs = secondary_dxs if secondary_dxs is not None else []
        self.principal_dx = principal_dx
        self.admit_dx = admit_dx
        self.inpatient_pxs = inpatient_pxs if inpatient_pxs is not None else []
        self.lines = lines if lines is not None else []
        self.non_covered_days = non_covered_days
        self.billing_provider = billing_provider
        self.servicing_provider = servicing_provider
        self.patient = patient if patient is not None else Patient()
        self.additional_data = additional_data if additional_data is not None else {}
        self.map_flag = map_flag
        self.admit_date = admit_date
        self.admission_source = admission_source
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Claim':
        patient_data = data.get('patient')
        if patient_data:
            if isinstance(patient_data, dict):
                patient = Patient.from_json(patient_data)
            elif isinstance(patient_data, Patient):
                patient = patient_data
            else:
                patient = Patient()
        else:
            patient = Patient()
        
        billing_provider_data = data.get('billing_provider')
        if billing_provider_data:
            if isinstance(billing_provider_data, dict):
                billing_provider = Provider.from_json(billing_provider_data)
            elif isinstance(billing_provider_data, Provider):
                billing_provider = billing_provider_data
            else:
                billing_provider = None
        else:
            billing_provider = None
            
        servicing_provider_data = data.get('servicing_provider')
        if servicing_provider_data:
            if isinstance(servicing_provider_data, dict):
                servicing_provider = Provider.from_json(servicing_provider_data)
            elif isinstance(servicing_provider_data, Provider):
                servicing_provider = servicing_provider_data
            else:
                servicing_provider = None
        else:
            servicing_provider = None
        
        principal_dx_data = data.get('principal_dx')
        if principal_dx_data:
            if isinstance(principal_dx_data, dict):
                principal_dx = DiagnosisCode.from_json(principal_dx_data)
            elif isinstance(principal_dx_data, DiagnosisCode):
                principal_dx = principal_dx_data
            else:
                principal_dx = None
        else:
            principal_dx = None
            
        admit_dx_data = data.get('admit_dx')
        if admit_dx_data:
            if isinstance(admit_dx_data, dict):
                admit_dx = DiagnosisCode.from_json(admit_dx_data)
            elif isinstance(admit_dx_data, DiagnosisCode):
                admit_dx = admit_dx_data
            else:
                admit_dx = None
        else:
            admit_dx = None
        
        secondary_dxs = []
        secondary_dxs_data = data.get('secondary_dxs', [])
        for dx_data in secondary_dxs_data:
            if isinstance(dx_data, dict):
                secondary_dxs.append(DiagnosisCode.from_json(dx_data))
            elif isinstance(dx_data, DiagnosisCode):
                secondary_dxs.append(dx_data)
                
        inpatient_pxs = []
        inpatient_pxs_data = data.get('inpatient_pxs', [])
        for px_data in inpatient_pxs_data:
            if isinstance(px_data, dict):
                inpatient_pxs.append(ProcedureCode.from_json(px_data))
            elif isinstance(px_data, ProcedureCode):
                inpatient_pxs.append(px_data)
                
        value_codes = []
        value_codes_data = data.get('value_codes', [])
        for vc_data in value_codes_data:
            if isinstance(vc_data, dict):
                value_codes.append(ValueCode.from_json(vc_data))
            elif isinstance(vc_data, ValueCode):
                value_codes.append(vc_data)
                
        occurrence_codes = []
        occurrence_codes_data = data.get('occurrence_codes', [])
        for oc_data in occurrence_codes_data:
            if isinstance(oc_data, dict):
                occurrence_codes.append(OccurrenceCode.from_json(oc_data))
            elif isinstance(oc_data, OccurrenceCode):
                occurrence_codes.append(oc_data)
                
        span_codes = []
        span_codes_data = data.get('span_codes', [])
        for sc_data in span_codes_data:
            if isinstance(sc_data, dict):
                span_codes.append(SpanCode.from_json(sc_data))
            elif isinstance(sc_data, SpanCode):
                span_codes.append(sc_data)
                
        lines = []
        lines_data = data.get('lines', [])
        for line_data in lines_data:
            if isinstance(line_data, dict):
                lines.append(LineItem.from_json(line_data))
            elif isinstance(line_data, LineItem):
                lines.append(line_data)
        
        return cls(
            claimid=data.get('claimid', ''),
            from_date=data.get('from_date'),
            thru_date=data.get('thru_date'),
            los=data.get('los', 0),
            bill_type=data.get('bill_type', ''),
            patient_status=data.get('patient_status', ''),
            total_charges=data.get('total_charges', 0.0),
            cond_codes=data.get('cond_codes', []),
            value_codes=value_codes,
            occurrence_codes=occurrence_codes,
            span_codes=span_codes,
            receipt_date=data.get('receipt_date'),
            rfvdx=data.get('rfvdx', []),
            secondary_dxs=secondary_dxs,
            principal_dx=principal_dx,
            admit_dx=admit_dx,
            inpatient_pxs=inpatient_pxs,
            lines=lines,
            non_covered_days=data.get('non_covered_days', 0),
            billing_provider=billing_provider,
            servicing_provider=servicing_provider,
            patient=patient,
            additional_data=data.get('additional_data', {}),
            map_flag=data.get('map_flag', False),
            admit_date=data.get('admit_date'),
            admission_source=data.get('admission_source', '')
        )
    
    def to_json(self) -> Dict[str, Any]:
        return {
            'claimid': self.claimid,
            'from_date': self.from_date,
            'thru_date': self.thru_date,
            'los': self.los,
            'bill_type': self.bill_type,
            'patient_status': self.patient_status,
            'total_charges': self.total_charges,
            'cond_codes': self.cond_codes,
            'value_codes': [vc.to_json() for vc in self.value_codes],
            'occurrence_codes': [oc.to_json() for oc in self.occurrence_codes],
            'span_codes': [sc.to_json() for sc in self.span_codes],
            'receipt_date': self.receipt_date,
            'rfvdx': self.rfvdx,
            'secondary_dxs': [dx.to_json() for dx in self.secondary_dxs],
            'principal_dx': self.principal_dx.to_json() if self.principal_dx else None,
            'admit_dx': self.admit_dx.to_json() if self.admit_dx else None,
            'inpatient_pxs': [px.to_json() for px in self.inpatient_pxs],
            'lines': [line.to_json() for line in self.lines],
            'non_covered_days': self.non_covered_days,
            'billing_provider': self.billing_provider.to_json() if self.billing_provider else None,
            'servicing_provider': self.servicing_provider.to_json() if self.servicing_provider else None,
            'patient': self.patient.to_json(),
            'additional_data': self.additional_data,
            'map_flag': self.map_flag,
            'admit_date': self.admit_date,
            'admission_source': self.admission_source
        }

class ValueCode:
    def __init__(self, code="", amount=0.0):
        self.code = code
        self.amount = amount
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'ValueCode':
        return cls(
            code=data.get('code', ''),
            amount=data.get('amount', 0.0)
        )
    
    def to_json(self) -> Dict[str, Any]:
        return {
            'code': self.code,
            'amount': self.amount
        }

class ProcedureCode:
    def __init__(self, code="", modifier="", date=None, additional_data=None):
        self.code = code
        self.modifier = modifier
        self.date = date
        self.additional_data = additional_data if additional_data is not None else {}
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'ProcedureCode':
        return cls(
            code=data.get('code', ''),
            modifier=data.get('modifier', ''),
            date=data.get('date'),
            additional_data=data.get('additional_data', {})
        )
    
    def to_json(self) -> Dict[str, Any]:
        return {
            'code': self.code,
            'modifier': self.modifier,
            'date': self.date,
            'additional_data': self.additional_data
        }

class OccurrenceCode:
    def __init__(self, code="", date=None):
        self.code = code
        self.date = date
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'OccurrenceCode':
        return cls(
            code=data.get('code', ''),
            date=data.get('date')
        )
    
    def to_json(self) -> Dict[str, Any]:
        return {
            'code': self.code,
            'date': self.date
        }

class SpanCode:
    def __init__(self, code="", start_date=None, end_date=None):
        self.code = code
        self.start_date = start_date
        self.end_date = end_date
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'SpanCode':
        return cls(
            code=data.get('code', ''),
            start_date=data.get('start_date'),
            end_date=data.get('end_date')
        )
    
    def to_json(self) -> Dict[str, Any]:
        return {
            'code': self.code,
            'start_date': self.start_date,
            'end_date': self.end_date
        }

class DxType(Enum):
    UNKNOWN = 0
    PRIMARY = 1
    SECONDARY = 2

class DiagnosisCode:
    def __init__(self, code="", poa:PoaType=PoaType.BLANK, dx_type:DxType=DxType.UNKNOWN):
        self.code = code
        self.poa = poa
        self.dx_type = dx_type
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'DiagnosisCode':
        poa_value = data.get('poa', PoaType.BLANK)
        if isinstance(poa_value, str):
            poa = next((p for p in PoaType if p.value == poa_value), PoaType.BLANK)
        elif isinstance(poa_value, PoaType):
            poa = poa_value
        else:
            poa = PoaType.BLANK
        
        dx_type_value = data.get('dx_type', DxType.UNKNOWN)
        if isinstance(dx_type_value, str):
            try:
                dx_type = DxType[dx_type_value.upper()]
            except KeyError:
                dx_type = DxType.UNKNOWN
        elif isinstance(dx_type_value, int):
            try:
                dx_type = DxType(dx_type_value)
            except ValueError:
                dx_type = DxType.UNKNOWN
        elif isinstance(dx_type_value, DxType):
            dx_type = dx_type_value
        else:
            dx_type = DxType.UNKNOWN
        
        return cls(
            code=data.get('code', ''),
            poa=poa,
            dx_type=dx_type
        )
    
    def to_json(self) -> Dict[str, Any]:
        return {
            'code': self.code,
            'poa': self.poa.value,
            'dx_type': self.dx_type.name
        }

class LineItem:
    def __init__(self, service_date=None, revenue_code="", hcpcs="", modifiers=None, units=0, charges=0.0, ndc="", ndc_units=0.0, pos="", contractor_bypass=None, contractor_status_indicator="", contractor_apc="", contractor_payment_indicator="", contractor_discounting_formula="", contractor_reject_flag="", contractor_packaging_flag="", contractor_payment_adjust_flag01="", contractor_payment_adjust_flag02="", contractor_payment_method="", act_flag_input="", servicing_provider=None):
        self.service_date = service_date
        self.revenue_code = revenue_code
        self.hcpcs = hcpcs
        self.modifiers = modifiers if modifiers is not None else []
        self.units = units
        self.charges = charges
        self.ndc = ndc
        self.ndc_units = ndc_units
        self.pos = pos
        self.servicing_provider = servicing_provider if servicing_provider is not None else Provider()
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'LineItem':
        provider_data = data.get('servicing_provider')
        if provider_data:
            if isinstance(provider_data, dict):
                provider = Provider.from_json(provider_data)
            elif isinstance(provider_data, Provider):
                provider = provider_data
            else:
                provider = Provider()
        else:
            provider = Provider()
        
        return cls(
            service_date=data.get('service_date'),
            revenue_code=data.get('revenue_code', ''),
            hcpcs=data.get('hcpcs', ''),
            modifiers=data.get('modifiers', []),
            units=data.get('units', 0),
            charges=data.get('charges', 0.0),
            ndc=data.get('ndc', ''),
            ndc_units=data.get('ndc_units', 0.0),
            pos=data.get('pos', ''),
            servicing_provider=provider
        )
    
    def to_json(self) -> Dict[str, Any]:
        return {
            'service_date': self.service_date,
            'revenue_code': self.revenue_code,
            'hcpcs': self.hcpcs,
            'modifiers': self.modifiers,
            'units': self.units,
            'charges': self.charges,
            'ndc': self.ndc,
            'ndc_units': self.ndc_units,
            'pos': self.pos,
            'servicing_provider': self.servicing_provider.to_json()
        }

