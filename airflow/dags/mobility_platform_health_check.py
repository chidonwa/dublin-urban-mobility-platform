from datetime import datetime

from airflow.sdk import dag, task


@dag(
    dag_id="mobility_platform_health_check",
    schedule=None,
    start_date=datetime(2026, 9, 24),
    catchup=False,
    tags=["dublin-mobility", "health-check"],
)
def mobility_platform_health_check():

    @task
    def check_platform():
        print("Dublin Urban Mobility Platform")
        print("Airflow orchestration is working.")
        print("Platform health check passed.")

        return {
            "platform": "dublin-urban-mobility-platform",
            "status": "healthy",
        }

    check_platform()


mobility_platform_health_check()
