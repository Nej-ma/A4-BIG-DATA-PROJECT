"""
Gold Layer - Dimension Patient

Builds patient dimension for star schema from Silver layer.

Authors: Nejma MOUALHI, Brieuc OLIVIERI, Nicolas TAING
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.spark_utils import get_spark_session, get_paths, logger
from pyspark.sql.functions import col


def build_dim_patient():
    """Build patient dimension for Gold layer"""

    spark = get_spark_session("Gold-Dimension-Patient")
    paths = get_paths()

    try:
        logger.info("Starting build: dim_patient")

        # Read from Silver
        df_patient_silver = spark.read.parquet(f"{paths['silver']}/patient")
        logger.info(f"Read {df_patient_silver.count():,} rows from Silver")

        # Select for dimension (already clean from Silver)
        dim_patient = df_patient_silver.select(
            col("id_patient"),
            col("nom_hash"),
            col("prenom_hash"),
            col("sexe"),
            col("age"),
            col("date_naissance"),
            col("ville"),
            col("code_postal"),
            col("pays"),
            col("groupe_sanguin")
        )

        count = dim_patient.count()
        logger.info(f"Built dimension with {count:,} patients")

        # Save to Gold
        output_path = f"{paths['gold']}/dim_patient"
        dim_patient.write \
            .mode("overwrite") \
            .parquet(output_path)

        logger.info(f"SUCCESS: dim_patient saved to {output_path}")

        spark.stop()
        return 0

    except Exception as e:
        logger.error(f"ERROR building dim_patient: {str(e)}")
        spark.stop()
        return 1


if __name__ == "__main__":
    exit_code = build_dim_patient()
    sys.exit(exit_code)
