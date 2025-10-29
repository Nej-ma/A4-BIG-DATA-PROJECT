"""
Test Delta Lake configuration
Quick test to verify Delta Lake is working properly
"""

from pyspark.sql import SparkSession
import os

def test_delta_lake():
    """Test Delta Lake read/write operations"""

    # Create Spark session with Delta Lake
    # Note: when using spark-submit with --packages, we don't use configure_spark_with_delta_pip
    spark = (
        SparkSession.builder
        .appName("Test Delta Lake")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .getOrCreate()
    )

    print("✅ Spark session with Delta Lake created successfully")
    print(f"Spark version: {spark.version}")

    # Create test data
    data = [
        (1, "Test1", 100),
        (2, "Test2", 200),
        (3, "Test3", 300)
    ]

    df = spark.createDataFrame(data, ["id", "name", "value"])
    print(f"\n✅ Created test DataFrame with {df.count()} rows")

    # Write to Delta Lake
    test_path = "/opt/spark-data/test_delta"
    df.write.format("delta").mode("overwrite").save(test_path)
    print(f"✅ Written to Delta Lake: {test_path}")

    # Read from Delta Lake
    df_read = spark.read.format("delta").load(test_path)
    print(f"✅ Read from Delta Lake: {df_read.count()} rows")

    df_read.show()

    # Check Delta Lake metadata
    print("\n✅ Delta Lake test successful!")
    print(f"Delta table location: {test_path}")

    spark.stop()

if __name__ == "__main__":
    test_delta_lake()
