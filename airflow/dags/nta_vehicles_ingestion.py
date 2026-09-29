import sys

import pendulum
from airflow.sdk import dag, task


PROJECT_ROOT = "/opt/project"

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@dag(
    dag_id="nta_vehicles_ingestion",
    schedule="*/5 * * * *",
    start_date=pendulum.datetime(2026, 9, 25, tz="Europe/Dublin"),
    catchup=False,
    max_active_runs=1,
    tags=["dublin-mobility", "ingestion", "nta", "realtime"],
)
def nta_vehicles_ingestion():

    @task
    def ingest_nta_vehicles():
        import os

        os.chdir(PROJECT_ROOT)

        from src.ingestion.nta_vehicles import main

        main()

    ingest_nta_vehicles()


nta_vehicles_ingestion()
