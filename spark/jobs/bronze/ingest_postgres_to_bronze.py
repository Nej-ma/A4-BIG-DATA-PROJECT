"""
BRONZE LAYER - Ingestion PostgreSQL → MinIO Delta Lake
====================================================
Extrait toutes les tables PostgreSQL et les charge en format Delta Lake
dans MinIO (couche Bronze - données brutes)

Auteurs: Nejma MOUALHI | Brieuc OLIVIERI | Nicolas TAING
Date: 2025
"""

import sys
sys.path.append('/opt/spark-apps/utils')

from spark_utils import (
    create_spark_session,
    get_postgres_connection_properties,
    write_to_delta,
    add_ingestion_metadata,
    log_dataframe_info,
    logger
)

# Tables à extraire de PostgreSQL
TABLES = [
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

# Chemin base pour la couche Bronze dans MinIO
BRONZE_BASE_PATH = "s3a://lakehouse/bronze/postgres"


def ingest_table_to_bronze(spark, table_name: str, jdbc_props: dict):
    """
    Ingère une table PostgreSQL vers la couche Bronze

    Args:
        spark: Session Spark
        table_name: Nom de la table PostgreSQL
        jdbc_props: Propriétés de connexion JDBC
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"🔄 Ingestion de la table: {table_name}")
    logger.info(f"{'='*80}")

    try:
        # Lecture depuis PostgreSQL
        logger.info(f"📖 Lecture depuis PostgreSQL...")
        df = spark.read.jdbc(
            url=jdbc_props["url"],
            table=f'"{table_name}"',  # Guillemets pour les noms en majuscules
            properties=jdbc_props
        )

        log_dataframe_info(df, table_name)

        # Ajout des métadonnées d'ingestion
        df_with_metadata = add_ingestion_metadata(df)

        # Écriture en Delta Lake (Bronze)
        bronze_path = f"{BRONZE_BASE_PATH}/{table_name}"
        write_to_delta(
            df_with_metadata,
            bronze_path,
            mode="overwrite",
            partition_by=["ingestion_date"]
        )

        logger.info(f"✅ Table {table_name} ingérée avec succès!")
        return True

    except Exception as e:
        logger.error(f"❌ Erreur lors de l'ingestion de {table_name}: {str(e)}")
        return False


def main():
    """
    Point d'entrée principal
    """
    logger.info("\n" + "="*80)
    logger.info("🚀 DÉMARRAGE - Ingestion PostgreSQL vers Bronze Layer")
    logger.info("="*80 + "\n")

    # Création de la session Spark
    spark = create_spark_session("CHU_Bronze_Postgres_Ingestion")

    # Propriétés de connexion PostgreSQL
    jdbc_props = get_postgres_connection_properties()

    # Statistiques
    success_count = 0
    failed_count = 0

    # Ingestion de toutes les tables
    for table in TABLES:
        if ingest_table_to_bronze(spark, table, jdbc_props):
            success_count += 1
        else:
            failed_count += 1

    # Résumé
    logger.info("\n" + "="*80)
    logger.info("📊 RÉSUMÉ DE L'INGESTION")
    logger.info("="*80)
    logger.info(f"✅ Tables ingérées avec succès: {success_count}/{len(TABLES)}")
    logger.info(f"❌ Tables en erreur: {failed_count}/{len(TABLES)}")
    logger.info(f"📦 Localisation Bronze: {BRONZE_BASE_PATH}")
    logger.info("="*80 + "\n")

    # Arrêt de la session Spark
    spark.stop()
    logger.info("🏁 Ingestion terminée!")


if __name__ == "__main__":
    main()
