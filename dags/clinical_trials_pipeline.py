from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    "owner": "giorgi",
    "depends_on_past": False,
}


with DAG(
    dag_id="clinical_trials_pipeline",
    default_args=default_args,
    description="Clinical trial ETL pipeline",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["clinical-trials", "etl", "postgres"],
) as dag:

    init_db = BashOperator(
        task_id="init_db",
        bash_command="cd /opt/airflow && python3 -m src.db.init_db",
    )

    load_staging = BashOperator(
        task_id="load_staging",
        bash_command="cd /opt/airflow && python3 -m src.ingestion.load_csv_to_staging",
    )

    transform_core = BashOperator(
        task_id="transform_core",
        bash_command="cd /opt/airflow && python3 -m src.transform.transform_trials",
    )

    run_analytics = BashOperator(
        task_id="run_analytics",
        bash_command="cd /opt/airflow && python3 -m src.analytics.run_analytics",
    )

    init_db >> load_staging >> transform_core >> run_analytics