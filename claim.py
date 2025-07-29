from enum import Enum

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

class ValueCode:
    def __init__(self, code="", amount=0.0):
        self.code = code
        self.amount = amount

class ProcedureCode:
    def __init__(self, code="", modifier="", date=None, additional_data=None):
        self.code = code
        self.modifier = modifier
        self.date = date
        self.additional_data = additional_data if additional_data is not None else {}

class OccurrenceCode:
    def __init__(self, code="", date=None):
        self.code = code
        self.date = date

class SpanCode:
    def __init__(self, code="", start_date=None, end_date=None):
        self.code = code
        self.start_date = start_date
        self.end_date = end_date

class DiagnosisCode:
    def __init__(self, code="", poa="", dx_type=None):
        self.code = code
        self.poa = poa
        self.dx_type = dx_type

class DxType(Enum):
    UNKNOWN = 0
    PRIMARY = 1
    SECONDARY = 2

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

