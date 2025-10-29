"""
Export Gold Layer (Delta Lake) to PostgreSQL for Superset
Exports all Gold dimensions and facts to PostgreSQL in 'gold' schema

Authors: Nejma MOUALHI, Brieuc OLIVIERI, Nicolas TAING
Date: October 2025
"""

from pyspark.sql import SparkSession
import sys
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_spark_session():
    """Create Spark session with Delta Lake and PostgreSQL support"""
    master = os.getenv("SPARK_MASTER_URL", "local[*]")
    builder = (
        SparkSession.builder
        .appName("CHU - Export Gold to PostgreSQL")
        .config("spark.driver.memory", "4g")
        .config("spark.executor.memory", "4g")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.3,io.delta:delta-core_2.12:2.4.0")
    )
    if master:
        builder = builder.master(master)
    return builder.getOrCreate()


def export_to_postgres(spark, table_name, gold_path, jdbc_url, jdbc_props):
    """Export a Delta Lake or Parquet table to PostgreSQL"""
    try:
        logger.info(f"Exporting {table_name}...")

        # Try Delta Lake first, fallback to Parquet
        try:
            df = spark.read.format("delta").load(gold_path)
            format_type = "Delta Lake"
        except:
            df = spark.read.parquet(gold_path)
            format_type = "Parquet"

        row_count = df.count()
        logger.info(f"  Read {row_count:,} rows from {format_type}")

        # Write to PostgreSQL (schema 'gold')
        df.write \
            .jdbc(
                url=jdbc_url,
                table=f"gold.{table_name}",
                mode="overwrite",
                properties=jdbc_props
            )

        logger.info(f"  ✅ Exported {row_count:,} rows to PostgreSQL gold.{table_name}")
        return {"table": table_name, "rows": row_count, "status": "SUCCESS"}

    except Exception as e:
        logger.error(f"  ❌ Error exporting {table_name}: {str(e)}")
        return {"table": table_name, "rows": 0, "status": f"ERROR: {str(e)}"}


def main():
    """Main execution function"""
    logger.info("="*80)
    logger.info("EXPORT GOLD LAYER TO POSTGRESQL FOR SUPERSET")
    logger.info("="*80)

    # Create Spark session
    spark = create_spark_session()
    logger.info(f"Spark {spark.version} session created")

    # Configuration
    data_base = os.getenv("DATA_BASE", "/opt/spark-data")
    gold_base = f"{data_base}/gold"

    # PostgreSQL connection
    jdbc_url = "jdbc:postgresql://chu_postgres:5432/healthcare_data"
    jdbc_props = {
        "user": "admin",
        "password": "admin123",
        "driver": "org.postgresql.Driver"
    }

    # Create 'gold' schema in PostgreSQL if not exists
    logger.info("\nCreating 'gold' schema in PostgreSQL...")
    try:
        spark.read.jdbc(
            url=jdbc_url,
            table="(SELECT 1) AS dummy",
            properties=jdbc_props
        ).collect()

        # Execute CREATE SCHEMA via JDBC
        from py4j.java_gateway import java_import
        java_import(spark._jvm, "java.sql.DriverManager")

        conn = spark._jvm.DriverManager.getConnection(
            jdbc_url,
            jdbc_props["user"],
            jdbc_props["password"]
        )
        stmt = conn.createStatement()
        stmt.execute("CREATE SCHEMA IF NOT EXISTS gold")
        stmt.close()
        conn.close()

        logger.info("  ✅ Schema 'gold' ready")
    except Exception as e:
        logger.warning(f"  Could not create schema: {e}")
        logger.info("  Continuing anyway...")

    # List of Gold tables to export
    tables_to_export = [
        # Dimensions
        "dim_temps",
        "dim_patient",
        "dim_diagnostic",
        "dim_professionnel",
        "dim_etablissement",
        # Facts
        "fait_consultation",
        "fait_hospitalisation",
        "fait_deces",
        "fait_satisfaction"
    ]

    # Export each table
    logger.info("\n" + "="*80)
    logger.info("EXPORTING TABLES")
    logger.info("="*80)

    results = []
    for table in tables_to_export:
        gold_path = f"{gold_base}/{table}"
        result = export_to_postgres(spark, table, gold_path, jdbc_url, jdbc_props)
        results.append(result)

    # Summary
    logger.info("\n" + "="*80)
    logger.info("EXPORT SUMMARY")
    logger.info("="*80)

    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    total_rows = sum(r["rows"] for r in results if r["status"] == "SUCCESS")

    for result in results:
        status_emoji = "✅" if result["status"] == "SUCCESS" else "❌"
        logger.info(f"{status_emoji} {result['table']:30s} | {result['rows']:>10,} rows | {result['status']}")

    logger.info("="*80)
    logger.info(f"Exported: {success_count}/{len(tables_to_export)} tables")
    logger.info(f"Total rows: {total_rows:,}")
    logger.info("="*80)

    # Connection info for Superset
    logger.info("\n" + "="*80)
    logger.info("SUPERSET CONNECTION INFO")
    logger.info("="*80)
    logger.info("Database Type: PostgreSQL")
    logger.info("Host: chu_postgres")
    logger.info("Port: 5432")
    logger.info("Database: healthcare_data")
    logger.info("Schema: gold")
    logger.info("Username: admin")
    logger.info("Password: admin123")
    logger.info("")
    logger.info("SQLAlchemy URI:")
    logger.info("postgresql://admin:admin123@chu_postgres:5432/healthcare_data")
    logger.info("="*80)

    spark.stop()

    if success_count == len(tables_to_export):
        logger.info("\n✅ All tables exported successfully!")
        return 0
    else:
        logger.warning(f"\n⚠️ Some tables failed to export ({len(tables_to_export) - success_count} errors)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
