"""
Analyse des taux de consultations par professionnels
Exécute plusieurs requêtes analytiques sur le schéma gold

Authors: Claude Assistant
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
    """Create Spark session"""
    master = os.getenv("SPARK_MASTER_URL", "local[*]")
    builder = (
        SparkSession.builder
        .appName("CHU - Analyse Consultations Professionnels")
        .config("spark.driver.memory", "4g")
        .config("spark.executor.memory", "4g")
        .config("spark.sql.adaptive.enabled", "true")
    )
    if master:
        builder = builder.master(master)
    return builder.getOrCreate()


def main():
    """Main execution function"""
    logger.info("Starting consultation analysis by professionals")

    spark = create_spark_session()
    logger.info(f"Spark {spark.version} initialized")

    try:
        data_base = os.getenv("DATA_BASE", "/opt/spark-data")
        gold_base = f"{data_base}/gold"

        # Load Gold tables
        logger.info("Loading Gold tables...")
        fait_consultation = spark.read.parquet(f"{gold_base}/fait_consultation")
        dim_professionnel = spark.read.parquet(f"{gold_base}/dim_professionnel")
        dim_temps = spark.read.parquet(f"{gold_base}/dim_temps")

        fait_consultation.createOrReplaceTempView("fait_consultation")
        dim_professionnel.createOrReplaceTempView("dim_professionnel")
        dim_temps.createOrReplaceTempView("dim_temps")

        logger.info("Tables loaded successfully")

        # Query 1: Taux de consultations par spécialité
        logger.info("\n" + "="*80)
        logger.info("ANALYSE 1: TAUX DE CONSULTATIONS PAR SPÉCIALITÉ MÉDICALE")
        logger.info("="*80)

        query1 = """
        SELECT
            p.nom_specialite,
            COUNT(*) as nb_consultations,
            COUNT(DISTINCT c.id_patient) as patients_uniques,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pourcentage_consultations
        FROM fait_consultation c
        JOIN dim_professionnel p ON c.id_prof = p.id_prof
        WHERE p.nom_specialite IS NOT NULL
        GROUP BY p.nom_specialite
        ORDER BY nb_consultations DESC
        LIMIT 20
        """

        result1 = spark.sql(query1)
        logger.info("\nRésultats - Top 20 spécialités:")
        result1.show(20, truncate=False)

        # Query 2: Top 20 professionnels individuels
        logger.info("\n" + "="*80)
        logger.info("ANALYSE 2: TOP 20 PROFESSIONNELS PAR NOMBRE DE CONSULTATIONS")
        logger.info("="*80)

        query2 = """
        SELECT
            p.id_prof,
            p.nom,
            p.prenom,
            p.nom_specialite,
            COUNT(*) as nb_consultations,
            COUNT(DISTINCT c.id_patient) as patients_uniques,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 4) as taux_pourcentage
        FROM fait_consultation c
        JOIN dim_professionnel p ON c.id_prof = p.id_prof
        GROUP BY p.id_prof, p.nom, p.prenom, p.nom_specialite
        ORDER BY nb_consultations DESC
        LIMIT 20
        """

        result2 = spark.sql(query2)
        logger.info("\nRésultats - Top 20 professionnels:")
        result2.show(20, truncate=False)

        # Query 3: Évolution temporelle par spécialité
        logger.info("\n" + "="*80)
        logger.info("ANALYSE 3: ÉVOLUTION TEMPORELLE DES CONSULTATIONS PAR SPÉCIALITÉ")
        logger.info("="*80)

        query3 = """
        SELECT
            t.annee,
            p.nom_specialite,
            COUNT(*) as nb_consultations,
            COUNT(DISTINCT c.id_prof) as professionnels_actifs,
            COUNT(DISTINCT c.id_patient) as patients_uniques
        FROM fait_consultation c
        JOIN dim_professionnel p ON c.id_prof = p.id_prof
        JOIN dim_temps t ON c.id_temps = t.id_temps
        WHERE p.nom_specialite IS NOT NULL
        GROUP BY t.annee, p.nom_specialite
        ORDER BY t.annee, nb_consultations DESC
        """

        result3 = spark.sql(query3)
        logger.info("\nRésultats - Évolution par année et spécialité (top 30):")
        result3.show(30, truncate=False)

        # Query 4: Consultations moyennes par professionnel et spécialité
        logger.info("\n" + "="*80)
        logger.info("ANALYSE 4: CONSULTATIONS MOYENNES PAR PROFESSIONNEL ET SPÉCIALITÉ")
        logger.info("="*80)

        query4 = """
        SELECT
            p.nom_specialite,
            COUNT(DISTINCT p.id_prof) as nb_professionnels,
            COUNT(*) as nb_consultations_total,
            ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT p.id_prof), 2) as consultations_moy_par_prof,
            COUNT(DISTINCT c.id_patient) as patients_uniques,
            ROUND(COUNT(DISTINCT c.id_patient) * 1.0 / COUNT(DISTINCT p.id_prof), 2) as patients_moy_par_prof
        FROM fait_consultation c
        JOIN dim_professionnel p ON c.id_prof = p.id_prof
        WHERE p.nom_specialite IS NOT NULL
        GROUP BY p.nom_specialite
        ORDER BY consultations_moy_par_prof DESC
        LIMIT 20
        """

        result4 = spark.sql(query4)
        logger.info("\nRésultats - Top 20 spécialités par consultation moyenne:")
        result4.show(20, truncate=False)

        # Query 5: Statistiques globales
        logger.info("\n" + "="*80)
        logger.info("ANALYSE 5: STATISTIQUES GLOBALES")
        logger.info("="*80)

        query5 = """
        SELECT
            COUNT(*) as total_consultations,
            COUNT(DISTINCT id_prof) as total_professionnels,
            COUNT(DISTINCT id_patient) as total_patients,
            ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT id_prof), 2) as consultations_moy_par_prof,
            ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT id_patient), 2) as consultations_moy_par_patient
        FROM fait_consultation
        """

        result5 = spark.sql(query5)
        logger.info("\nRésultats - Statistiques globales:")
        result5.show(truncate=False)

        # Query 6: Répartition par année
        logger.info("\n" + "="*80)
        logger.info("ANALYSE 6: RÉPARTITION ANNUELLE DES CONSULTATIONS")
        logger.info("="*80)

        query6 = """
        SELECT
            annee,
            COUNT(*) as nb_consultations,
            COUNT(DISTINCT id_patient) as patients_uniques,
            COUNT(DISTINCT id_prof) as professionnels_actifs,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pourcentage_annuel
        FROM fait_consultation
        GROUP BY annee
        ORDER BY annee
        """

        result6 = spark.sql(query6)
        logger.info("\nRésultats - Répartition par année:")
        result6.show(20, truncate=False)

        logger.info("\n" + "="*80)
        logger.info("ANALYSE COMPLETED SUCCESSFULLY")
        logger.info("="*80)

        return 0

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    sys.exit(main())
