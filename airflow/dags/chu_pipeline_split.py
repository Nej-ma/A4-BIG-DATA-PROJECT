"""
Airflow DAG - Split PySpark jobs with TaskGroups

Runs fine-grained tasks for Bronze (Postgres/CSV), Silver (subjects),
Gold (each dimension/fact), and Benchmarks. Enables parallelism and
targeted retries.
"""

from airflow import DAG
from airflow.utils.task_group import TaskGroup
from airflow.operators.bash import BashOperator
from datetime import datetime
import os


DEFAULT_ENV = {
    # Force local master for Livrable 2 (ignore AIRFLOW_CONN_SPARK_DEFAULT)
    "SPARK_MASTER_URL": "local[*]",
    "DATA_BASE": "/opt/spark-data",
    "DATA_DIR": "/data/DATA_2024",
    "SPARK_DRIVER_MEMORY": "8g",
    "SPARK_EXECUTOR_MEMORY": "8g",
    # Python version alignment for PySpark
    "PYSPARK_PYTHON": "python3",
    "PYSPARK_DRIVER_PYTHON": "python3",
}

PG_TABLES = [
    "Patient", "Consultation", "Diagnostic", "Professionnel_de_sante",
    "Mutuelle", "Adher", "Prescription", "Medicaments",
    "Laboratoire", "Salle", "Specialites", "date", "AAAA",
]

CSV_SOURCES = [
    "etablissement_sante", "satisfaction_esatis48h_2019", "departements", "deces_2019",
]

with DAG(
    dag_id="chu_pipeline_split",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    default_args={"owner": "chu-team"},
    tags=["chu", "split", "pyspark"],
) as dag:

    # Bronze - Postgres
    with TaskGroup("bronze_postgres") as bronze_pg:
        pg_tasks = []
        for t in PG_TABLES:
            pg_tasks.append(BashOperator(
                task_id=f"extract_pg_{t.lower()}",
                bash_command=f"python /opt/spark-apps/01_extract_bronze.py --postgres-table \"{t}\"",
                env={**DEFAULT_ENV, "SPARK_APP_NAME": f"Bronze-PG-{t}"},
            ))

    # Bronze - CSV
    with TaskGroup("bronze_csv") as bronze_csv:
        csv_tasks = []
        for s in CSV_SOURCES:
            csv_tasks.append(BashOperator(
                task_id=f"extract_csv_{s}",
                bash_command=f"python /opt/spark-apps/01_extract_bronze.py --csv-source {s}",
                env={**DEFAULT_ENV, "SPARK_APP_NAME": f"Bronze-CSV-{s}"},
            ))

    # Silver - subjects
    silver_patient = BashOperator(
        task_id="silver_patient",
        bash_command="python /opt/spark-apps/02_transform_silver.py --subject patient",
        env={**DEFAULT_ENV, "SPARK_APP_NAME": "Silver-Patient"},
    )

    silver_consultation = BashOperator(
        task_id="silver_consultation",
        bash_command="python /opt/spark-apps/02_transform_silver.py --subject consultation",
        env={**DEFAULT_ENV, "SPARK_APP_NAME": "Silver-Consultation"},
    )

    silver_etab = BashOperator(
        task_id="silver_etablissement_sante",
        bash_command="python /opt/spark-apps/02_transform_silver.py --subject etablissement_sante",
        env={**DEFAULT_ENV, "SPARK_APP_NAME": "Silver-Etablissement"},
    )

    silver_satisf = BashOperator(
        task_id="silver_satisfaction",
        bash_command="python /opt/spark-apps/02_transform_silver.py --subject satisfaction",
        env={**DEFAULT_ENV, "SPARK_APP_NAME": "Silver-Satisfaction"},
    )

    silver_deces = BashOperator(
        task_id="silver_deces",
        bash_command="python /opt/spark-apps/02_transform_silver.py --subject deces",
        env={**DEFAULT_ENV, "SPARK_APP_NAME": "Silver-Deces"},
    )

    silver_refs = BashOperator(
        task_id="silver_references",
        bash_command="python /opt/spark-apps/02_transform_silver.py --subject references",
        env={**DEFAULT_ENV, "SPARK_APP_NAME": "Silver-References"},
    )

    # Gold - dimensions
    with TaskGroup("gold_dimensions") as gold_dims:
        dim_temps = BashOperator(task_id="dim_temps", bash_command="python /opt/spark-apps/03_transform_gold.py --task dim_temps", env={**DEFAULT_ENV})
        dim_patient = BashOperator(task_id="dim_patient", bash_command="python /opt/spark-apps/03_transform_gold.py --task dim_patient", env={**DEFAULT_ENV})
        dim_diagnostic = BashOperator(task_id="dim_diagnostic", bash_command="python /opt/spark-apps/03_transform_gold.py --task dim_diagnostic", env={**DEFAULT_ENV})
        dim_professionnel = BashOperator(task_id="dim_professionnel", bash_command="python /opt/spark-apps/03_transform_gold.py --task dim_professionnel", env={**DEFAULT_ENV})
        dim_etablissement = BashOperator(task_id="dim_etablissement", bash_command="python /opt/spark-apps/03_transform_gold.py --task dim_etablissement", env={**DEFAULT_ENV})

    # Gold - facts
    with TaskGroup("gold_facts") as gold_facts:
        fait_consultation = BashOperator(task_id="fait_consultation", bash_command="python /opt/spark-apps/03_transform_gold.py --task fait_consultation", env={**DEFAULT_ENV})
        fait_hospitalisation = BashOperator(task_id="fait_hospitalisation", bash_command="python /opt/spark-apps/03_transform_gold.py --task fait_hospitalisation", env={**DEFAULT_ENV})
        fait_deces = BashOperator(task_id="fait_deces", bash_command="python /opt/spark-apps/03_transform_gold.py --task fait_deces", env={**DEFAULT_ENV})
        fait_satisfaction = BashOperator(task_id="fait_satisfaction", bash_command="python /opt/spark-apps/03_transform_gold.py --task fait_satisfaction", env={**DEFAULT_ENV})

    # Benchmarks (single task)
    benchmarks = BashOperator(
        task_id="benchmarks",
        bash_command="python /opt/spark-apps/04_benchmarks.py",
        env={**DEFAULT_ENV, "SPARK_APP_NAME": "Benchmarks"},
    )

    # Dependencies
    # Bronze (Postgres + CSV) -> Silver transformations
    bronze_pg >> [silver_patient, silver_consultation, silver_refs]
    bronze_csv >> [silver_etab, silver_satisf, silver_deces]

    # Silver -> Gold dimensions
    [silver_patient, silver_consultation, silver_etab, silver_refs] >> gold_dims

    # Gold dimensions -> Gold facts
    gold_dims >> gold_facts

    # Gold facts -> Benchmarks
    gold_facts >> benchmarks
