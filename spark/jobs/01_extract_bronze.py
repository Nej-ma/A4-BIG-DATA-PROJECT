"""
Bronze Layer Extraction Job

Extracts data from PostgreSQL and CSV sources into Bronze layer.
Preserves raw data with minimal transformation (metadata only).

Authors: Nejma MOUALHI, Brieuc OLIVIERI, Nicolas TAING
Date: October 2025
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit, col
from datetime import datetime
import sys
import logging
import os
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BronzeExtractor:
    """Handles extraction of raw data to Bronze layer"""

    def __init__(self, spark):
        self.spark = spark
        self.jdbc_url = "jdbc:postgresql://chu_postgres:5432/healthcare_data"
        self.jdbc_props = {
            "user": "admin",
            "password": "admin123",
            "driver": "org.postgresql.Driver"
        }
        # Use env-configurable paths for portability (Airflow/Jupyter/Spark)
        self.data_dir = os.getenv("DATA_DIR", "/data/DATA_2024")
        data_base = os.getenv("DATA_BASE", "/opt/spark-data")
        self.output_base = f"{data_base}/bronze"
        self.results = []

    def extract_postgres_table(self, table_name):
        """Extract single PostgreSQL table to Bronze"""
        logger.info(f"Extracting PostgreSQL table: {table_name}")

        try:
            df = self.spark.read.jdbc(
                url=self.jdbc_url,
                table=f'"{table_name}"',
                properties=self.jdbc_props
            )

            row_count = df.count()
            logger.info(f"Read {row_count:,} rows from {table_name}")

            df_with_meta = df \
                .withColumn("ingestion_timestamp", current_timestamp()) \
                .withColumn("ingestion_date", lit(datetime.now().strftime("%Y-%m-%d")))

            output_path = f"{self.output_base}/postgres/{table_name}"
            df_with_meta.write \
                .mode("overwrite") \
                .partitionBy("ingestion_date") \
                .parquet(output_path)

            logger.info(f"Saved {table_name} to {output_path}")

            return {
                "source": "PostgreSQL",
                "table": table_name,
                "rows": row_count,
                "status": "SUCCESS"
            }

        except Exception as e:
            logger.error(f"Error extracting {table_name}: {str(e)}")
            return {
                "source": "PostgreSQL",
                "table": table_name,
                "rows": 0,
                "status": f"ERROR: {str(e)}"
            }

    def extract_csv_file(self, name, file_path, separator=";"):
        """Extract CSV file to Bronze"""
        logger.info(f"Extracting CSV: {name} from {file_path}")

        try:
            df = self.spark.read \
                .option("header", "true") \
                .option("inferSchema", "true") \
                .option("sep", separator) \
                .option("encoding", "UTF-8") \
                .csv(file_path)

            row_count = df.count()
            logger.info(f"Read {row_count:,} rows from {name}")

            df_with_meta = df \
                .withColumn("ingestion_timestamp", current_timestamp()) \
                .withColumn("ingestion_date", lit(datetime.now().strftime("%Y-%m-%d")))

            output_path = f"{self.output_base}/csv/{name}"
            df_with_meta.write \
                .mode("overwrite") \
                .parquet(output_path)

            logger.info(f"Saved {name} to {output_path}")

            return {
                "source": "CSV",
                "table": name,
                "rows": row_count,
                "status": "SUCCESS"
            }

        except Exception as e:
            logger.error(f"Error extracting {name}: {str(e)}")
            return {
                "source": "CSV",
                "table": name,
                "rows": 0,
                "status": f"ERROR: {str(e)}"
            }

    def extract_deces_filtered(self):
        """Extract deaths data filtered for year 2019 only"""
        logger.info("Extracting deaths data (2019 only)")

        try:
            df_raw = self.spark.read \
                .option("header", "true") \
                .option("inferSchema", "true") \
                .csv(f"{self.data_dir}/DECES EN FRANCE/deces.csv")

            logger.info("Filtering deaths for year 2019")
            df_filtered = df_raw.filter(col("date_deces").startswith("2019"))
            df_filtered = df_filtered.repartition(10)

            row_count = df_filtered.count()
            logger.info(f"Filtered to {row_count:,} rows (2019 only)")

            df_with_meta = df_filtered \
                .withColumn("ingestion_timestamp", current_timestamp()) \
                .withColumn("ingestion_date", lit(datetime.now().strftime("%Y-%m-%d")))

            output_path = f"{self.output_base}/csv/deces_2019"
            df_with_meta.write \
                .mode("overwrite") \
                .option("compression", "snappy") \
                .parquet(output_path)

            logger.info(f"Saved deaths 2019 to {output_path}")

            return {
                "source": "CSV",
                "table": "deces_2019",
                "rows": row_count,
                "status": "SUCCESS"
            }

        except Exception as e:
            logger.error(f"Error extracting deaths: {str(e)}")
            return {
                "source": "CSV",
                "table": "deces_2019",
                "rows": 0,
                "status": f"ERROR: {str(e)}"
            }

    def extract_all_postgres(self):
        """Extract all PostgreSQL tables"""
        postgres_tables = [
            "Patient",
            "Consultation",
            "Diagnostic",
            "Professionnel_de_sante",
            "Mutuelle",
            "Adher",
            "Prescription",
            "Medicaments",
            "Laboratoire",
            "Salle",
            "Specialites",
            "date",
            "AAAA"
        ]

        logger.info(f"Extracting {len(postgres_tables)} PostgreSQL tables")

        for table in postgres_tables:
            result = self.extract_postgres_table(table)
            self.results.append(result)

    def extract_all_csv(self):
        """Extract all CSV files"""
        logger.info("Extracting CSV files")

        csv_files = [
            ("etablissement_sante", f"{self.data_dir}/Etablissement de SANTE/etablissement_sante.csv"),
            ("satisfaction_esatis48h_2019", f"{self.data_dir}/Satisfaction/2019/resultats-esatis48h-mco-open-data-2019.csv"),
            ("departements", f"{self.data_dir}/departements-francais.csv")
        ]

        for name, path in csv_files:
            result = self.extract_csv_file(name, path)
            self.results.append(result)

        result = self.extract_deces_filtered()
        self.results.append(result)

    def print_summary(self):
        """Print extraction summary"""
        success = [r for r in self.results if r["status"] == "SUCCESS"]
        total_rows = sum(r["rows"] for r in success)

        logger.info("=" * 60)
        logger.info("EXTRACTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Tables extracted: {len(success)}/{len(self.results)}")
        logger.info(f"Total rows: {total_rows:,}")
        logger.info("=" * 60)

        for result in self.results:
            status_symbol = "OK" if result["status"] == "SUCCESS" else "ERROR"
            logger.info(f"{result['source']:12} | {result['table']:30} | {result['rows']:>10,} rows | {status_symbol}")


def create_spark_session():
    """Create Spark session with optimal configuration"""
    master = os.getenv("SPARK_MASTER_URL", "local[*]")
    builder = (
        SparkSession.builder
        .appName(os.getenv("SPARK_APP_NAME", "CHU - Bronze Extraction"))
        .config("spark.driver.memory", os.getenv("SPARK_DRIVER_MEMORY", "4g"))
        .config("spark.executor.memory", os.getenv("SPARK_EXECUTOR_MEMORY", "4g"))
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .config("spark.jars.packages", os.getenv("SPARK_PACKAGES", "org.postgresql:postgresql:42.7.3"))
    )
    if master:
        builder = builder.master(master)
    return builder.getOrCreate()


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Bronze extraction job")
    parser.add_argument("--postgres-table", dest="postgres_table", help="Single PostgreSQL table to extract")
    parser.add_argument("--csv-source", dest="csv_source", help="Single CSV source to extract: etablissement_sante|satisfaction_esatis48h_2019|departements|deces_2019")
    parser.add_argument("--all", dest="run_all", action="store_true", help="Run full extraction (Postgres + CSV)")
    args = parser.parse_args()

    logger.info("Starting Bronze Layer Extraction")

    spark = create_spark_session()
    logger.info(f"Spark {spark.version} initialized")

    exit_code = 0
    try:
        extractor = BronzeExtractor(spark)

        ran_any = False

        if args.postgres_table:
            res = extractor.extract_postgres_table(args.postgres_table)
            extractor.results.append(res)
            ran_any = True

        if args.csv_source:
            name = args.csv_source
            if name == "deces_2019":
                res = extractor.extract_deces_filtered()
                extractor.results.append(res)
            else:
                mapping = {
                    "etablissement_sante": f"{extractor.data_dir}/Etablissement de SANTE/etablissement_sante.csv",
                    "satisfaction_esatis48h_2019": f"{extractor.data_dir}/Satisfaction/2019/resultats-esatis48h-mco-open-data-2019.csv",
                    "departements": f"{extractor.data_dir}/departements-francais.csv",
                }
                if name not in mapping:
                    logger.error(f"Unknown CSV source: {name}")
                    return 2
                res = extractor.extract_csv_file(name, mapping[name])
                extractor.results.append(res)
            ran_any = True

        if args.run_all or not ran_any:
            extractor.extract_all_postgres()
            extractor.extract_all_csv()

        extractor.print_summary()
        logger.info("Bronze extraction completed successfully")

    except Exception as e:
        logger.error(f"Bronze extraction failed: {str(e)}")
        import traceback
        traceback.print_exc()
        exit_code = 1

    finally:
        spark.stop()
        logger.info("Spark session stopped")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
