"""
Bronze Layer - PostgreSQL Table Extraction

Extracts a single PostgreSQL table to Bronze layer.
Usage: python extract_postgres.py <table_name>

Authors: Nejma MOUALHI, Brieuc OLIVIERI, Nicolas TAING
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.spark_utils import get_spark_session, get_paths, get_jdbc_config, logger
from pyspark.sql.functions import current_timestamp, lit
from datetime import datetime


def extract_postgres_table(table_name):
    """Extract single PostgreSQL table to Bronze layer"""

    spark = get_spark_session(f"Bronze-Postgres-{table_name}")
    paths = get_paths()
    jdbc_config = get_jdbc_config()

    try:
        logger.info(f"Starting extraction: {table_name}")

        # Read from PostgreSQL
        df = spark.read.jdbc(
            url=jdbc_config["url"],
            table=f'"{table_name}"',
            properties=jdbc_config["properties"]
        )

        row_count = df.count()
        logger.info(f"Read {row_count:,} rows from {table_name}")

        # Add ingestion metadata
        df_with_meta = df \
            .withColumn("ingestion_timestamp", current_timestamp()) \
            .withColumn("ingestion_date", lit(datetime.now().strftime("%Y-%m-%d")))

        # Save to Bronze
        output_path = f"{paths['bronze']}/postgres/{table_name}"
        df_with_meta.write \
            .mode("overwrite") \
            .partitionBy("ingestion_date") \
            .parquet(output_path)

        logger.info(f"SUCCESS: {table_name} saved to {output_path}")
        logger.info(f"Total: {row_count:,} rows")

        spark.stop()
        return 0

    except Exception as e:
        logger.error(f"ERROR extracting {table_name}: {str(e)}")
        spark.stop()
        return 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_postgres.py <table_name>")
        print("Example: python extract_postgres.py Patient")
        sys.exit(1)

    table_name = sys.argv[1]
    exit_code = extract_postgres_table(table_name)
    sys.exit(exit_code)
