"""
PHASE 6: ORCHESTRATION
------------------------
This is an Airflow DAG (Directed Acyclic Graph) - a definition of
"which scripts run, in what order, on what schedule."

Our pipeline has 5 steps that must run in this exact order:
  extract -> transform -> validate -> load -> dbt_run

If validate.py fails (data quality check fails), Airflow will
automatically STOP the pipeline and NOT run load.py - this is
exactly the kind of safety behavior interviewers ask about when
they say "tell me about a time you handled bad data."

Schedule: runs once per day at 06:00 UTC. Change schedule_interval
below to "@hourly" while testing if you want faster feedback.
"""

from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    "owner": "shiwani",
    "retries": 1,
}

with DAG(
    dag_id="crypto_pipeline",
    default_args=default_args,
    description="Extract, transform, validate, and load crypto market data",
    schedule_interval="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["portfolio-project", "etl"],
) as dag:

    extract = BashOperator(
        task_id="extract",
        bash_command="python /opt/airflow/scripts/extract.py",
    )

    transform = BashOperator(
        task_id="transform",
        bash_command="python /opt/airflow/scripts/transform.py",
    )

    validate = BashOperator(
        task_id="validate",
        bash_command="python /opt/airflow/scripts/validate.py",
    )

    load = BashOperator(
        task_id="load",
        bash_command="python /opt/airflow/scripts/load.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt_crypto && dbt run --profiles-dir /opt/airflow/dbt_crypto",
    )

    # Pipeline order: each step only runs if the previous one succeeds
    extract >> transform >> validate >> load >> dbt_run
