import os
from datetime import datetime, timedelta

from pydrg.helpers import claim_example, json_claim_example, opps_claim_example
from pydrg.input import (
    LineItem,
    ValueCode,
    Provider,
    DiagnosisCode,
    PoaType,
    OccurrenceCode,
    OasisAssessment,
    IrfPai,
)
from pydrg.pypps import Pypps

if __name__ == "__main__":
    jar_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "jars"))
    db_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "data", "pypps.db")
    )
    pypps = Pypps(
        build_jar_dirs=True, jar_path=jar_path, db_path=db_path, build_db=True
    )  # <--- Set build_db=True to create the database if it does not exist
    pypps.setup_clients()

    test_claim_1 = claim_example()
    test_claim_2 = json_claim_example()
    opps_claim = opps_claim_example()
