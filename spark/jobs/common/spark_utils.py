"""
Common utilities for Spark jobs

Shared functions and configurations used across all jobs.
"""

from pyspark.sql import SparkSession
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_spark_session(app_name="CHU-Job"):
    """Create and configure Spark session with standard settings"""
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.driver.memory", os.getenv("SPARK_DRIVER_MEMORY", "4g")) \
        .config("spark.executor.memory", os.getenv("SPARK_EXECUTOR_MEMORY", "4g")) \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()

    logger.info(f"Spark session created: {app_name} (v{spark.version})")
    return spark


def get_paths():
    """Get standard paths for data storage"""
    data_dir = os.getenv("DATA_DIR", "/data/DATA_2024")
    data_base = os.getenv("DATA_BASE", "/opt/spark-data")

    return {
        "data_dir": data_dir,
        "bronze": f"{data_base}/bronze",
        "silver": f"{data_base}/silver",
        "gold": f"{data_base}/gold"
    }


def get_jdbc_config():
    """Get PostgreSQL JDBC configuration"""
    return {
        "url": "jdbc:postgresql://chu_postgres:5432/healthcare_data",
        "properties": {
            "user": "admin",
            "password": "admin123",
            "driver": "org.postgresql.Driver"
        }
    }
