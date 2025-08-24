import os
from datetime import datetime
import pytest

from pydrg.helpers import claim_example, json_claim_example, opps_claim_example
from pydrg.input import LineItem, ValueCode
from pydrg.pypps import Pypps


def project_root_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def jars_dir():
    return os.path.join(project_root_dir(), "jars")


def pricers_dir():
    return os.path.join(jars_dir(), "pricers")


def _file_exists(dir_path, name_substring):
    if not os.path.exists(dir_path):
        return False
    try:
        for f in os.listdir(dir_path):
            if f.endswith(".jar") and name_substring in f:
                return True
    except Exception:
        return False
    return False


def base_jars_present():
    d = jars_dir()
    # Require core runtime deps and at least one of the main components
    required_substrings = [
        "gfc-base-api",
        "protobuf-java",
        "slf4j-",
    ]
    return all(_file_exists(d, s) for s in required_substrings)


def pricer_available(name_substring):
    return _file_exists(pricers_dir(), name_substring)


@pytest.fixture(scope="module")
def pypps_or_skip():
    if not base_jars_present():
        pytest.skip(
            "Required runtime JARs not found in ./jars. Populate real CMS jars to run integration tests."
        )

    jar_path = jars_dir()
    db_path = os.path.join(project_root_dir(), "data", "pypps.db")

    pypps = Pypps(
        build_jar_dirs=False, jar_path=jar_path, db_path=db_path, build_db=False
    )
    pypps.setup_clients()
    try:
        yield pypps
    finally:
        pypps.shutdown()


def test_mce_process_example_claim(pypps_or_skip):
    claim = claim_example()
    output = pypps_or_skip.mce_client.process(claim)
    assert hasattr(output, "model_dump"), "MCE output should be a pydantic model"


def test_msdrg_process_json_claim(pypps_or_skip):
    claim = json_claim_example()
    output = pypps_or_skip.drg_client.process(claim)
    # Basic invariants
    assert hasattr(output, "model_dump"), "MS-DRG output should be a pydantic model"


def test_ioce_process_opps_claim(pypps_or_skip):
    claim = opps_claim_example()
    output = pypps_or_skip.ioce_client.process(claim)
    assert hasattr(output, "model_dump"), "IOCE output should be a pydantic model"


def test_ipps_pricer_if_available(pypps_or_skip):
    if not pricer_available("ipps-pricer"):
        pytest.skip("IPPS pricer jar not present in ./jars/pricers")
    if pypps_or_skip.ipps_client is None:
        pytest.skip("IPPS client not initialized")

    claim = claim_example()
    drg_output = pypps_or_skip.drg_client.process(claim)
    output = pypps_or_skip.ipps_client.process(claim, drg_output)
    assert hasattr(output, "model_dump")


def test_opps_pricer_if_available(pypps_or_skip):
    if not pricer_available("opps-pricer"):
        pytest.skip("OPPS pricer jar not present in ./jars/pricers")
    if pypps_or_skip.opps_client is None:
        pytest.skip("OPPS client not initialized")

    claim = opps_claim_example()
    ioce_output = pypps_or_skip.ioce_client.process(claim)
    output = pypps_or_skip.opps_client.process(claim, ioce_output)
    assert hasattr(output, "model_dump")


def test_ipf_pricer_if_available(pypps_or_skip):
    if not pricer_available("ipf-pricer"):
        pytest.skip("IPF pricer jar not present in ./jars/pricers")
    if pypps_or_skip.ipf_client is None:
        pytest.skip("IPF client not initialized")

    claim = claim_example()
    drg_output = pypps_or_skip.drg_client.process(claim)
    output = pypps_or_skip.ipf_client.process(claim, drg_output)
    assert hasattr(output, "model_dump")


def test_ltch_pricer_if_available(pypps_or_skip):
    if not pricer_available("ltch-pricer"):
        pytest.skip("LTCH pricer jar not present in ./jars/pricers")
    if pypps_or_skip.ltch_client is None:
        pytest.skip("LTCH client not initialized")

    claim = claim_example()
    # Example parity: LTCH requires special provider id in example
    claim.billing_provider.other_id = "012006"
    drg_output = pypps_or_skip.drg_client.process(claim)
    output = pypps_or_skip.ltch_client.process(claim, drg_output)
    assert hasattr(output, "model_dump")


def test_hospice_pricer_if_available(pypps_or_skip):
    if not pricer_available("hospice-pricer"):
        pytest.skip("Hospice pricer jar not present in ./jars/pricers")
    if pypps_or_skip.hospice_client is None:
        pytest.skip("Hospice client not initialized")

    claim = claim_example()
    claim.bill_type = "812"
    claim.patient_status = "40"
    claim.value_codes.append(ValueCode(code="61", amount=35300.00))
    claim.value_codes.append(ValueCode(code="G8", amount=35300.00))
    claim.thru_date = datetime(2025, 7, 10)
    claim.los = 10
    claim.lines.append(
        LineItem(
            hcpcs="Q5001",
            revenue_code="0651",
            service_date=datetime(2025, 7, 1),
            units=9,
            charges=10_000.00,
        )
    )
    claim.lines.append(
        LineItem(
            hcpcs="G0299",
            revenue_code="0551",
            service_date=datetime(2025, 7, 1),
            units=3,
            charges=10_000.00,
        )
    )

    output = pypps_or_skip.hospice_client.process(claim)
    assert hasattr(output, "model_dump")


def test_snf_pricer_if_available(pypps_or_skip):
    if not pricer_available("snf-pricer"):
        pytest.skip("SNF pricer jar not present in ./jars/pricers")
    if pypps_or_skip.snf_client is None:
        pytest.skip("SNF client not initialized")

    claim = claim_example()
    claim.admit_date = datetime(2025, 1, 1)
    claim.from_date = datetime(2025, 1, 1)
    claim.thru_date = datetime(2025, 1, 20)
    claim.los = 20
    claim.bill_type = "327"
    claim.patient_status = "01"
    claim.principal_dx.code = "B20"
    claim.secondary_dxs[0].code = "C50911"
    claim.lines.clear()
    claim.lines.append(LineItem())
    claim.lines[0].revenue_code = "0022"
    claim.lines[0].hcpcs = "ABAC1"
    claim.lines[0].service_date = datetime(2025, 1, 1)
    claim.lines[0].units = 20
    output = pypps_or_skip.snf_client.process(claim)
    assert hasattr(output, "model_dump")
