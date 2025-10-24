"""
Bronze Layer - Etablissements CSV Extraction

Extracts etablissements de sante CSV file to Bronze layer.

Authors: Nejma MOUALHI, Brieuc OLIVIERI, Nicolas TAING
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.spark_utils import get_spark_session, get_paths, logger
from pyspark.sql.functions import current_timestamp, lit
from datetime import datetime


def extract_etablissements():
    """Extract etablissements CSV to Bronze layer"""

    spark = get_spark_session("Bronze-CSV-Etablissements")
    paths = get_paths()

    try:
        logger.info("Starting extraction: etablissements de sante")

        # Read CSV
        file_path = f"{paths['data_dir']}/Etablissement de SANTE/etablissement_sante.csv"
        df = spark.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .option("sep", ";") \
            .option("encoding", "UTF-8") \
            .csv(file_path)

        row_count = df.count()
        logger.info(f"Read {row_count:,} rows from etablissement_sante.csv")

        # Add ingestion metadata
        df_with_meta = df \
            .withColumn("ingestion_timestamp", current_timestamp()) \
            .withColumn("ingestion_date", lit(datetime.now().strftime("%Y-%m-%d")))

        # Save to Bronze
        output_path = f"{paths['bronze']}/csv/etablissement_sante"
        df_with_meta.write \
            .mode("overwrite") \
            .parquet(output_path)

        logger.info(f"SUCCESS: etablissement_sante saved to {output_path}")
        logger.info(f"Total: {row_count:,} rows")

        spark.stop()
        return 0

    except Exception as e:
        logger.error(f"ERROR extracting etablissements: {str(e)}")
        spark.stop()
        return 1


if __name__ == "__main__":
    exit_code = extract_etablissements()
    sys.exit(exit_code)
