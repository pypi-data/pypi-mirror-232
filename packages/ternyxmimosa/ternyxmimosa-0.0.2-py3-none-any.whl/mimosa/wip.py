"""Sample dlt pipeline.

Loads data from European Gas data REST API.

Loads data incrementally into DuckDB.
"""
from datetime import date  # F401

from mimosa.pipelines import GEI

pipeline = GEI(destination="motherduck")
reporting_update = False

run_this = False
if run_this:
    pipeline.run_landing_pipeline(
        gas_date=date(2021, 6, 1),  # still from 2019-01-01 to 2019-09-01
        to_gas_date=date(2021, 6, 23),
        reporting_update=reporting_update,
    )

pipeline.run_landing_pipeline()
reporting_update = True

if not reporting_update:
    pipeline.run_reporting_pipeline()
