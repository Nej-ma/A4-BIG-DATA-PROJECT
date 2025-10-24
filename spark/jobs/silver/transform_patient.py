"""
Silver Layer - Patient Transformation

Transforms Patient data from Bronze to Silver with:
- Anonymization (SHA-256 hashing)
- Date format standardization
- Data cleaning and validation

Authors: Nejma MOUALHI, Brieuc OLIVIERI, Nicolas TAING
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.spark_utils import get_spark_session, get_paths, logger
from pyspark.sql.functions import (
    col, sha2, trim, upper, to_date, current_timestamp
)


def transform_patient():
    """Transform Patient data to Silver layer"""

    spark = get_spark_session("Silver-Patient")
    paths = get_paths()

    try:
        logger.info("Starting transformation: Patient")

        # Read from Bronze
        df_patient_bronze = spark.read.parquet(f"{paths['bronze']}/postgres/Patient")
        logger.info(f"Read {df_patient_bronze.count():,} rows from Bronze")

        # Transformation with anonymization
        df_patient_silver = df_patient_bronze.select(
            col("Id_patient").alias("id_patient"),

            # Anonymization: SHA-256 hash of sensitive data
            sha2(col("Nom"), 256).alias("nom_hash"),
            sha2(col("Prenom"), 256).alias("prenom_hash"),

            # Demographics
            col("Sexe").alias("sexe"),
            col("Age").cast("integer").alias("age"),

            # Date format: M/d/yyyy -> yyyy-MM-dd
            to_date(col("Date"), "M/d/yyyy").alias("date_naissance"),

            # Location (geographical broad = OK for GDPR)
            trim(upper(col("Ville"))).alias("ville"),
            col("Code_postal").alias("code_postal"),
            trim(upper(col("Pays"))).alias("pays"),

            # Medical info
            col("Poid").cast("double").alias("poids_kg"),
            col("Taille").cast("double").alias("taille_cm"),
            trim(upper(col("Groupe_sanguin"))).alias("groupe_sanguin"),

            # Contact (hashed)
            sha2(col("Tel"), 256).alias("telephone_hash"),
            sha2(col("EMail"), 256).alias("email_hash"),

            # Social security (hashed)
            sha2(col("Num_Secu"), 256).alias("num_secu_hash"),

            # Metadata
            col("ingestion_date"),
            current_timestamp().alias("transformation_timestamp")
        ).dropDuplicates(["id_patient"])

        count = df_patient_silver.count()
        logger.info(f"Transformed {count:,} patients")

        # Save to Silver
        output_path = f"{paths['silver']}/patient"
        df_patient_silver.write \
            .mode("overwrite") \
            .parquet(output_path)

        logger.info(f"SUCCESS: Patient saved to {output_path}")

        spark.stop()
        return 0

    except Exception as e:
        logger.error(f"ERROR transforming Patient: {str(e)}")
        spark.stop()
        return 1


if __name__ == "__main__":
    exit_code = transform_patient()
    sys.exit(exit_code)
