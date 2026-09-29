import os
import subprocess

import pendulum
from airflow.sdk import dag, task


DBT_IMAGE = "dublin-mobility-dbt:1.0"
AIRFLOW_CONTAINER = os.environ.get("HOSTNAME")

def get_host_mount_path(container_path):
    result = subprocess.run(
        [
            "docker",
            "inspect",
            AIRFLOW_CONTAINER,
            "--format",
            "{{range .Mounts}}{{if eq .Destination \""
            + container_path
            + "\"}}{{.Source}}{{end}}{{end}}",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    path = result.stdout.strip()

    if not path:
        raise RuntimeError(
            f"Could not determine host mount path for {container_path}"
        )

    return path


@dag(
    dag_id="dbt_transformation",
    schedule="20 * * * *",
    start_date=pendulum.datetime(2026, 9, 28, tz="Europe/Dublin"),
    catchup=False,
    max_active_runs=1,
    tags=["dublin-mobility", "dbt", "transformation"],
)
def dbt_transformation():

    @task
    def run_dbt_build():
        project_path = get_host_mount_path(
            "/opt/project/mobility_analytics"
        )
        profile_path = get_host_mount_path(
            "/opt/airflow/dbt"
        )

        required_env = [
            "DB_PORT",
            "DB_USER",
            "DB_PASSWORD",
            "DB_NAME",
        ]

        for variable in required_env:
            if not os.environ.get(variable):
                raise RuntimeError(
                    f"Required environment variable {variable} is missing"
                )

        command = [
            "docker",
            "run",
            "--rm",
            "-e",
            "DB_HOST=host.docker.internal",
        ]

        for variable in required_env:
            command.extend(["-e", variable])

        command.extend(
            [
                "-v",
                f"{project_path}:/opt/project/mobility_analytics",
                "-v",
                f"{profile_path}:/root/.dbt:ro",
                DBT_IMAGE,
                "dbt",
                "build",
            ]
        )

        subprocess.run(command, check=True)

    run_dbt_build()


dbt_transformation()
