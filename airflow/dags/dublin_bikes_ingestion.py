import sys

from airflow.sdk import dag, task
import pendulum


PROJECT_ROOT = "/opt/project"

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@dag(
    dag_id="dublin_bikes_ingestion",
    schedule="*/15 * * * *",
    start_date=pendulum.datetime(2026, 9, 25, tz="Europe/Dublin"),
    catchup=False,
    max_active_runs=1,
    tags=["dublin-mobility", "ingestion", "dublin-bikes"],
)
def dublin_bikes_ingestion():

    @task
    def ingest_dublin_bikes():
        import os

        os.chdir(PROJECT_ROOT)

        from src.ingestion.dublin_bikes import main

        main()

    ingest_dublin_bikes()


dublin_bikes_ingestion()
