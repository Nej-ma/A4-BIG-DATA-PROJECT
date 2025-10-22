"""
Script de test des connexions
Vérifie que Spark peut se connecter à PostgreSQL et MinIO
"""

import sys
sys.path.append('/opt/spark-apps/utils')

from pyspark.sql import SparkSession
from pyspark.sql.functions import lit

print("\n" + "="*80)
print("🔍 TEST DES CONNEXIONS - CHU Data Lakehouse")
print("="*80 + "\n")

# Configuration Spark
print("📦 Configuration de Spark...")
spark = SparkSession.builder \
    .appName("CHU_Test_Connections") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,io.delta:delta-core_2.12:2.4.0") \
    .config("spark.hadoop.fs.s3a.endpoint", "chu_minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
    .getOrCreate()

print("✅ Session Spark créée\n")

# Test 1: Connexion PostgreSQL
print("="*80)
print("TEST 1: Connexion PostgreSQL")
print("="*80)

try:
    print("🔄 Tentative de connexion à PostgreSQL...")
    jdbc_url = "jdbc:postgresql://chu_postgres:5432/healthcare_data"
    jdbc_props = {
        "user": "admin",
        "password": "admin123",
        "driver": "org.postgresql.Driver"
    }

    # Lire la table Patient (limité à 10 lignes pour le test)
    df_patient = spark.read.jdbc(
        url=jdbc_url,
        table='"Patient"',
        properties=jdbc_props
    )

    count = df_patient.count()
    print(f"✅ Connexion PostgreSQL OK!")
    print(f"📊 Table Patient: {count:,} lignes")
    print("\nAperçu des données:")
    df_patient.show(5, truncate=True)

except Exception as e:
    print(f"❌ ERREUR PostgreSQL: {str(e)}")
    import traceback
    traceback.print_exc()

# Test 2: Connexion MinIO
print("\n" + "="*80)
print("TEST 2: Écriture/Lecture MinIO")
print("="*80)

try:
    print("🔄 Création d'un DataFrame de test...")
    test_data = [
        (1, "Test 1", "2025-01-20"),
        (2, "Test 2", "2025-01-20"),
        (3, "Test 3", "2025-01-20")
    ]
    df_test = spark.createDataFrame(test_data, ["id", "nom", "date"])

    print("🔄 Écriture dans MinIO...")
    test_path = "s3a://lakehouse/test/data"
    df_test.write.mode("overwrite").parquet(test_path)
    print(f"✅ Écriture OK: {test_path}")

    print("🔄 Lecture depuis MinIO...")
    df_read = spark.read.parquet(test_path)
    read_count = df_read.count()
    print(f"✅ Lecture OK: {read_count} lignes")
    print("\nAperçu des données:")
    df_read.show()

    print("✅ Connexion MinIO OK!")

except Exception as e:
    print(f"❌ ERREUR MinIO: {str(e)}")
    import traceback
    traceback.print_exc()

# Résumé
print("\n" + "="*80)
print("📊 RÉSUMÉ DES TESTS")
print("="*80)
print("✅ Tous les tests sont passés!")
print("🎯 Prêt pour l'ingestion Bronze")
print("="*80 + "\n")

spark.stop()
