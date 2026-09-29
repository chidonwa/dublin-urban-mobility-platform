import sys

import pendulum
from airflow.sdk import dag, task


PROJECT_ROOT = "/opt/project"

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@dag(
    dag_id="nta_gtfs_ingestion",
    schedule="0 3 * * 0",
    start_date=pendulum.datetime(2026, 9, 25, tz="Europe/Dublin"),
    catchup=False,
    max_active_runs=1,
    tags=["dublin-mobility", "ingestion", "nta", "gtfs", "static"],
)
def nta_gtfs_ingestion():

    @task
    def ingest_nta_gtfs():
        import os

        os.chdir(PROJECT_ROOT)

        from src.ingestion.nta_gtfs import main

        main()

    ingest_nta_gtfs()


nta_gtfs_ingestion()
