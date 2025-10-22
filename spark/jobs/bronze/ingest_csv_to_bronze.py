"""
BRONZE LAYER - Ingestion CSV → MinIO Delta Lake
================================================
Ingère tous les fichiers CSV (Décès, Satisfaction, Établissements, Hospitalisation)
vers la couche Bronze en format Delta Lake

Auteurs: Nejma MOUALHI | Brieuc OLIVIERI | Nicolas TAING
Date: 2025
"""

import sys
sys.path.append('/opt/spark-apps/utils')

from spark_utils import (
    create_spark_session,
    write_to_delta,
    add_ingestion_metadata,
    log_dataframe_info,
    logger
)
from pyspark.sql.types import *

# Configuration des fichiers CSV à ingérer
CSV_CONFIGS = {
    # Décès en France
    "deces": {
        "path": "/home/jovyan/DATA_2024/DECES EN FRANCE/deces.csv",
        "options": {"header": "true", "inferSchema": "true", "encoding": "UTF-8"},
        "output": "s3a://lakehouse/bronze/csv/deces"
    },

    # Établissements de santé
    "etablissement_sante": {
        "path": "/home/jovyan/DATA_2024/Etablissement de SANTE/etablissement_sante.csv",
        "options": {"header": "true", "inferSchema": "true", "sep": ";", "encoding": "UTF-8"},
        "output": "s3a://lakehouse/bronze/csv/etablissement_sante"
    },

    "professionnel_sante": {
        "path": "/home/jovyan/DATA_2024/Etablissement de SANTE/professionnel_sante.csv",
        "options": {"header": "true", "inferSchema": "true", "sep": ";", "encoding": "UTF-8"},
        "output": "s3a://lakehouse/bronze/csv/professionnel_sante"
    },

    "activite_professionnel_sante": {
        "path": "/home/jovyan/DATA_2024/Etablissement de SANTE/activite_professionnel_sante.csv",
        "options": {"header": "true", "inferSchema": "true", "sep": ";", "encoding": "UTF-8"},
        "output": "s3a://lakehouse/bronze/csv/activite_professionnel_sante"
    },

    # Hospitalisation
    "hospitalisations": {
        "path": "/home/jovyan/DATA_2024/Hospitalisation/Hospitalisations.csv",
        "options": {"header": "true", "inferSchema": "true", "encoding": "UTF-8"},
        "output": "s3a://lakehouse/bronze/csv/hospitalisations"
    },

    # Satisfaction 2019 (fichiers principaux)
    "satisfaction_esatis48h_2019": {
        "path": "/home/jovyan/DATA_2024/Satisfaction/2019/resultats-esatis48h-mco-open-data-2019.csv",
        "options": {"header": "true", "inferSchema": "true", "sep": ";", "encoding": "UTF-8"},
        "output": "s3a://lakehouse/bronze/csv/satisfaction/esatis48h_2019"
    },

    "satisfaction_esatisca_2019": {
        "path": "/home/jovyan/DATA_2024/Satisfaction/2019/resultats-esatisca-mco-open-data-2019.csv",
        "options": {"header": "true", "inferSchema": "true", "sep": ";", "encoding": "UTF-8"},
        "output": "s3a://lakehouse/bronze/csv/satisfaction/esatisca_2019"
    },

    "satisfaction_iqss_2019": {
        "path": "/home/jovyan/DATA_2024/Satisfaction/2019/resultats-iqss-open-data-2019.csv",
        "options": {"header": "true", "inferSchema": "true", "sep": ";", "encoding": "UTF-8"},
        "output": "s3a://lakehouse/bronze/csv/satisfaction/iqss_2019"
    },
}


def ingest_csv_to_bronze(spark, name: str, config: dict):
    """
    Ingère un fichier CSV vers la couche Bronze

    Args:
        spark: Session Spark
        name: Nom du dataset
        config: Configuration (path, options, output)
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"🔄 Ingestion CSV: {name}")
    logger.info(f"{'='*80}")

    try:
        # Lecture du CSV
        logger.info(f"📖 Lecture depuis: {config['path']}")
        df = spark.read.options(**config['options']).csv(config['path'])

        log_dataframe_info(df, name)

        # Ajout des métadonnées d'ingestion
        df_with_metadata = add_ingestion_metadata(df)

        # Écriture en Delta Lake (Bronze)
        write_to_delta(
            df_with_metadata,
            config['output'],
            mode="overwrite",
            partition_by=["ingestion_date"]
        )

        logger.info(f"✅ Dataset {name} ingéré avec succès!")
        return True

    except Exception as e:
        logger.error(f"❌ Erreur lors de l'ingestion de {name}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    """
    Point d'entrée principal
    """
    logger.info("\n" + "="*80)
    logger.info("🚀 DÉMARRAGE - Ingestion CSV vers Bronze Layer")
    logger.info("="*80 + "\n")

    # Création de la session Spark
    spark = create_spark_session("CHU_Bronze_CSV_Ingestion")

    # Statistiques
    success_count = 0
    failed_count = 0

    # Ingestion de tous les CSV
    for name, config in CSV_CONFIGS.items():
        if ingest_csv_to_bronze(spark, name, config):
            success_count += 1
        else:
            failed_count += 1

    # Résumé
    logger.info("\n" + "="*80)
    logger.info("📊 RÉSUMÉ DE L'INGESTION CSV")
    logger.info("="*80)
    logger.info(f"✅ Datasets ingérés avec succès: {success_count}/{len(CSV_CONFIGS)}")
    logger.info(f"❌ Datasets en erreur: {failed_count}/{len(CSV_CONFIGS)}")
    logger.info(f"📦 Localisation Bronze: s3a://lakehouse/bronze/csv/")
    logger.info("="*80 + "\n")

    # Arrêt de la session Spark
    spark.stop()
    logger.info("🏁 Ingestion CSV terminée!")


if __name__ == "__main__":
    main()
