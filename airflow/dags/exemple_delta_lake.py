"""
DAG EXEMPLE - DELTA LAKE
=========================
Exemple complet d'utilisation de Delta Lake pour le pipeline ETLT CHU

Étapes :
1. Extract depuis PostgreSQL
2. Transform T1 (pseudonymisation RGPD)
3. Load dans Delta Lake (Bronze)
4. Transform T2 (enrichissement)
5. Load dans Delta Lake (Silver)

Auteurs : Nejma MOUALHI, Brieuc OLIVIERI, Nicolas TAING
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import sha2, col, current_timestamp, year, month
from delta import *

# ============================================================
# CONFIGURATION
# ============================================================

default_args = {
    'owner': 'chu-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def create_spark_session(app_name="CHU ETL"):
    """Créer une session Spark avec Delta Lake configuré"""
    return SparkSession.builder \
        .appName(app_name) \
        .master("spark://chu_spark_master:7077") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://chu_minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.jars.packages", "io.delta:delta-core_2.12:2.4.0,org.apache.hadoop:hadoop-aws:3.3.4") \
        .getOrCreate()

# ============================================================
# TÂCHE 1 : EXTRACT + T1 (RGPD)
# ============================================================

def extract_and_pseudonymize_patients():
    """
    Extract patients depuis PostgreSQL
    + Transformation T1 : Pseudonymisation RGPD
    + Load dans Delta Lake (Bronze)
    """
    print("🔄 Démarrage Extract + T1 Patient...")

    spark = create_spark_session("T1 Patient Pseudonymisation")

    # 1. EXTRACT depuis PostgreSQL
    print("📥 Extraction depuis PostgreSQL...")
    df = spark.read.jdbc(
        url="jdbc:postgresql://chu_postgres:5432/healthcare_data",
        table='"Patient"',
        properties={
            "user": "admin",
            "password": "admin123",
            "driver": "org.postgresql.Driver"
        }
    )

    print(f"✅ {df.count()} patients extraits")

    # 2. TRANSFORM T1 - Pseudonymisation
    print("🔐 Pseudonymisation SHA-256...")

    # Renommer colonnes en minuscules
    for old_col in df.columns:
        df = df.withColumnRenamed(old_col, old_col.lower())

    # Pseudonymiser l'ID patient
    df_pseudo = df.withColumn(
        "id_patient_pseudo",
        sha2(col("id_patient").cast("string"), 256)
    )

    # 3. SUPPRESSION DES PII (Conformité RGPD)
    print("🗑️  Suppression des PII...")
    pii_columns = ["nom", "prenom", "email", "tel", "num_secu", "adresse"]
    df_clean = df_pseudo.drop(*[c for c in pii_columns if c in df_pseudo.columns])

    # 4. Ajout de métadonnées
    df_clean = df_clean.withColumn("etl_timestamp", current_timestamp())

    # 5. LOAD dans Delta Lake (Bronze)
    print("💾 Écriture dans Delta Lake (Bronze)...")

    bronze_path = "s3a://lakehouse/bronze/patient"

    df_clean.write \
        .format("delta") \
        .mode("overwrite") \
        .save(bronze_path)

    print(f"✅ {df_clean.count()} patients écrits dans {bronze_path}")

    # Vérification
    df_verify = spark.read.format("delta").load(bronze_path)
    print(f"✔️  Vérification : {df_verify.count()} lignes dans Delta Lake")

    spark.stop()
    print("✅ T1 Patient terminé avec succès!")

# ============================================================
# TÂCHE 2 : T2 (ENRICHISSEMENT)
# ============================================================

def enrich_patients_silver():
    """
    Transformation T2 : Enrichissement des données patient
    + Calcul de l'âge, catégorie d'âge, etc.
    + Load dans Delta Lake (Silver)
    """
    print("🔄 Démarrage T2 Patient Enrichissement...")

    spark = create_spark_session("T2 Patient Enrichissement")

    # 1. EXTRACT depuis Delta Lake Bronze
    print("📥 Lecture depuis Delta Lake (Bronze)...")
    bronze_path = "s3a://lakehouse/bronze/patient"
    df = spark.read.format("delta").load(bronze_path)

    print(f"✅ {df.count()} patients lus depuis Bronze")

    # 2. TRANSFORM T2 - Enrichissement
    print("⚙️  Enrichissement des données...")

    # Calculer l'âge
    from pyspark.sql.functions import datediff, lit, when
    from datetime import datetime as dt

    df_enriched = df.withColumn(
        "age",
        (datediff(lit(dt.now().date()), col("date")) / 365).cast("int")
    )

    # Catégorie d'âge
    df_enriched = df_enriched.withColumn(
        "categorie_age",
        when(col("age") < 18, "0-17 ans")
        .when(col("age") < 30, "18-29 ans")
        .when(col("age") < 45, "30-44 ans")
        .when(col("age") < 60, "45-59 ans")
        .when(col("age") < 75, "60-74 ans")
        .otherwise("75+ ans")
    )

    # Normalisation sexe
    df_enriched = df_enriched.withColumn(
        "sexe",
        when(col("sexe").isin("M", "Homme", "H"), "M")
        .when(col("sexe").isin("F", "Femme"), "F")
        .otherwise("Inconnu")
    )

    # Métadonnées T2
    df_enriched = df_enriched.withColumn("enrichment_timestamp", current_timestamp())

    # 3. LOAD dans Delta Lake (Silver)
    print("💾 Écriture dans Delta Lake (Silver)...")

    silver_path = "s3a://lakehouse/silver/patient"

    df_enriched.write \
        .format("delta") \
        .mode("overwrite") \
        .save(silver_path)

    print(f"✅ {df_enriched.count()} patients écrits dans {silver_path}")

    # Afficher un échantillon
    print("\n📊 Échantillon de données enrichies :")
    df_enriched.select("id_patient_pseudo", "age", "categorie_age", "sexe", "region").show(5)

    spark.stop()
    print("✅ T2 Patient terminé avec succès!")

# ============================================================
# TÂCHE 3 : STATISTIQUES (optionnel)
# ============================================================

def generate_patient_stats():
    """Générer des statistiques sur les patients"""
    print("📊 Génération des statistiques...")

    spark = create_spark_session("Stats Patient")

    # Lire depuis Silver
    silver_path = "s3a://lakehouse/silver/patient"
    df = spark.read.format("delta").load(silver_path)

    # Statistiques par catégorie d'âge
    stats_age = df.groupBy("categorie_age", "sexe").count()
    print("\n📊 Répartition par âge et sexe :")
    stats_age.orderBy("categorie_age", "sexe").show()

    # Statistiques par région
    stats_region = df.groupBy("region").count()
    print("\n🗺️  Répartition par région :")
    stats_region.orderBy(col("count").desc()).show()

    spark.stop()
    print("✅ Statistiques générées!")

# ============================================================
# DÉFINITION DU DAG
# ============================================================

with DAG(
    'exemple_delta_lake',
    default_args=default_args,
    description='Exemple complet Delta Lake - Pipeline ETLT Patient',
    schedule_interval='@daily',
    catchup=False,
    tags=['exemple', 'delta-lake', 'etlt', 'patient'],
) as dag:

    # Tâche 1 : Extract + T1 (RGPD)
    task_t1_patient = PythonOperator(
        task_id='t1_extract_pseudonymize_patient',
        python_callable=extract_and_pseudonymize_patients,
    )

    # Tâche 2 : T2 (Enrichissement)
    task_t2_patient = PythonOperator(
        task_id='t2_enrich_patient',
        python_callable=enrich_patients_silver,
    )

    # Tâche 3 : Statistiques
    task_stats = PythonOperator(
        task_id='generate_stats',
        python_callable=generate_patient_stats,
    )

    # Définir l'ordre d'exécution
    task_t1_patient >> task_t2_patient >> task_stats

# ============================================================
# UTILISATION
# ============================================================
#
# 1. Déployer ce fichier dans airflow/dags/
# 2. Aller sur http://localhost:8080
# 3. Activer le DAG "exemple_delta_lake"
# 4. Cliquer sur "Trigger DAG"
# 5. Suivre les logs dans la vue "Grid"
#
# VÉRIFICATION DANS MINIO :
# - Aller sur http://localhost:9001
# - Bucket : lakehouse
# - Dossiers : bronze/patient/, silver/patient/
# - Chaque dossier contient :
#   - _delta_log/ (historique des versions)
#   - part-XXXXX.parquet (données)
#
# REQUÊTER AVEC SPARK SQL :
# spark.sql("SELECT * FROM delta.`s3a://lakehouse/silver/patient` LIMIT 10").show()
#
# TIME TRAVEL (versions précédentes) :
# spark.read.format("delta").option("versionAsOf", 0).load("s3a://lakehouse/bronze/patient")
#
# ============================================================
