import sys

import pendulum
from airflow.sdk import dag, task


PROJECT_ROOT = "/opt/project"

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@dag(
    dag_id="met_eireann_ingestion",
    schedule="10 * * * *",
    start_date=pendulum.datetime(2026, 9, 25, tz="Europe/Dublin"),
    catchup=False,
    max_active_runs=1,
    tags=["dublin-mobility", "ingestion", "weather", "met-eireann"],
)
def met_eireann_ingestion():

    @task
    def ingest_met_eireann():
        import os

        os.chdir(PROJECT_ROOT)

        from src.ingestion.met_eireann import main

        main()

    ingest_met_eireann()


met_eireann_ingestion()
