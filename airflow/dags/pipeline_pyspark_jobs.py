"""
Airflow DAG - PySpark Jobs Orchestration

Runs the 4 PySpark jobs (Bronze -> Silver -> Gold -> Benchmarks)
on the Spark cluster using pyspark from the Airflow container
with master = spark://chu-spark-master:7077.

Jobs are executed as plain Python scripts that create a SparkSession
configured via environment variables for portability.
"""

from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    "owner": "chu-team",
    "depends_on_past": False,
    "start_date": datetime(2025, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="chu_pipeline_pyspark_jobs",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["chu", "pyspark", "cluster"],
) as dag:

    # Shared env for all tasks
    base_env = {
        # Spark master URL (force local for Livrable 2 stability - ignore AIRFLOW_CONN_SPARK_DEFAULT)
        "SPARK_MASTER_URL": "local[*]",
        # Data locations mounted in Airflow and Spark containers
        "DATA_BASE": "/opt/spark-data",
        "DATA_DIR": "/data/DATA_2024",
        # Memory tuning - 8G to leverage available 32G RAM
        "SPARK_DRIVER_MEMORY": "8g",
        "SPARK_EXECUTOR_MEMORY": "8g",
        # Python version alignment for PySpark
        "PYSPARK_PYTHON": "python3",
        "PYSPARK_DRIVER_PYTHON": "python3",
    }

    job_dir = "/opt/spark-apps"

    t_bronze = BashOperator(
        task_id="bronze_extract",
        bash_command=f"python {job_dir}/01_extract_bronze.py",
        env={**base_env, "SPARK_APP_NAME": "CHU - Bronze Extraction"},
    )

    t_silver = BashOperator(
        task_id="silver_transform",
        bash_command=f"python {job_dir}/02_transform_silver.py",
        env={**base_env, "SPARK_APP_NAME": "CHU - Silver Transformation"},
    )

    t_gold = BashOperator(
        task_id="gold_transform",
        bash_command=f"python {job_dir}/03_transform_gold.py",
        env={**base_env, "SPARK_APP_NAME": "CHU - Gold Star Schema"},
    )

    t_bench = BashOperator(
        task_id="benchmarks",
        bash_command=f"python {job_dir}/04_benchmarks.py",
        env={**base_env, "SPARK_APP_NAME": "CHU - Performance Benchmarks"},
    )

    t_bronze >> t_silver >> t_gold >> t_bench
