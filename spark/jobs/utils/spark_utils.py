"""
Utilitaires Spark pour le projet CHU Data Lakehouse
Auteurs: Nejma MOUALHI | Brieuc OLIVIERI | Nicolas TAING
"""

from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_spark_session(app_name: str, enable_delta: bool = True) -> SparkSession:
    """
    Crée une session Spark configurée pour Delta Lake et MinIO

    Args:
        app_name: Nom de l'application Spark
        enable_delta: Activer Delta Lake (défaut: True)

    Returns:
        SparkSession configurée
    """
    builder = SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://chu_minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.sql.warehouse.dir", "s3a://warehouse/") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "2g")

    if enable_delta:
        spark = configure_spark_with_delta_pip(builder).getOrCreate()
    else:
        spark = builder.getOrCreate()

    logger.info(f"Spark session créée: {app_name}")
    return spark


def get_postgres_connection_properties() -> dict:
    """
    Retourne les propriétés de connexion PostgreSQL

    Returns:
        Dictionnaire avec les propriétés JDBC
    """
    return {
        "url": "jdbc:postgresql://chu_postgres:5432/healthcare_data",
        "driver": "org.postgresql.Driver",
        "user": "admin",
        "password": "admin123"
    }


def write_to_delta(df, path: str, mode: str = "overwrite", partition_by: list = None):
    """
    Écrit un DataFrame au format Delta Lake

    Args:
        df: DataFrame à écrire
        path: Chemin S3 (s3a://bucket/path)
        mode: Mode d'écriture (overwrite, append)
        partition_by: Liste des colonnes de partitionnement
    """
    logger.info(f"Écriture Delta vers {path}")
    writer = df.write.format("delta").mode(mode)

    if partition_by:
        writer = writer.partitionBy(*partition_by)
        logger.info(f"Partitionnement par: {partition_by}")

    writer.save(path)
    logger.info(f"✅ Écriture terminée: {df.count()} lignes")


def read_delta(spark: SparkSession, path: str):
    """
    Lit une table Delta Lake

    Args:
        spark: Session Spark
        path: Chemin S3 de la table Delta

    Returns:
        DataFrame
    """
    logger.info(f"Lecture Delta depuis {path}")
    df = spark.read.format("delta").load(path)
    logger.info(f"✅ {df.count()} lignes chargées")
    return df


def add_ingestion_metadata(df):
    """
    Ajoute des colonnes de métadonnées d'ingestion

    Args:
        df: DataFrame source

    Returns:
        DataFrame enrichi avec métadonnées
    """
    from pyspark.sql.functions import current_timestamp, lit

    return df \
        .withColumn("ingestion_timestamp", current_timestamp()) \
        .withColumn("ingestion_date", lit(datetime.now().strftime("%Y-%m-%d")))


def log_dataframe_info(df, name: str):
    """
    Affiche les informations d'un DataFrame

    Args:
        df: DataFrame à analyser
        name: Nom du DataFrame
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"DataFrame: {name}")
    logger.info(f"{'='*60}")
    logger.info(f"Nombre de lignes: {df.count():,}")
    logger.info(f"Nombre de colonnes: {len(df.columns)}")
    logger.info(f"Schéma:")
    df.printSchema()
    logger.info(f"Aperçu:")
    df.show(5, truncate=False)
    logger.info(f"{'='*60}\n")
