"""
Gold Layer Transformation Job

Creates star schema dimensional model from Silver data.
Includes 5 dimensions and 4 fact tables with temporal partitioning.

Authors: Nejma MOUALHI, Brieuc OLIVIERI, Nicolas TAING
Date: October 2025
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, countDistinct, min as spark_min, max as spark_max,
    year, month, dayofmonth, date_format, datediff,
    monotonically_increasing_id, lit, substring, to_date
)
from pyspark.sql.types import *
from datetime import datetime, timedelta
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GoldTransformer:
    """Handles transformation of Silver to Gold star schema"""

    def __init__(self, spark):
        self.spark = spark
        self.silver_base = "/home/jovyan/data/silver"
        self.bronze_base = "/home/jovyan/data/bronze"
        self.gold_output = "/home/jovyan/data/gold"
        self.results = []

    def create_dim_temps(self):
        """Create time dimension (2013-2025)"""
        logger.info("Creating time dimension")

        start_date = datetime(2013, 1, 1)
        end_date = datetime(2025, 12, 31)
        dates = []

        current = start_date
        while current <= end_date:
            dates.append((
                current.strftime("%Y%m%d"),
                current,
                current.year,
                current.month,
                (current.month - 1) // 3 + 1,
                current.strftime("%A"),
                current.strftime("%B"),
                current.weekday() >= 5,
                current.weekday()
            ))
            current += timedelta(days=1)

        schema = StructType([
            StructField("id_temps", StringType(), False),
            StructField("date_complete", DateType(), False),
            StructField("annee", IntegerType(), False),
            StructField("mois", IntegerType(), False),
            StructField("trimestre", IntegerType(), False),
            StructField("jour_semaine", StringType(), True),
            StructField("nom_mois", StringType(), True),
            StructField("est_weekend", BooleanType(), True),
            StructField("numero_jour_semaine", IntegerType(), True)
        ])

        dim_temps = self.spark.createDataFrame(dates, schema=schema)
        row_count = dim_temps.count()
        logger.info(f"Created {row_count:,} days (2013-2025)")

        dim_temps.write.mode("overwrite").parquet(f"{self.gold_output}/dim_temps")
        logger.info("Saved dim_temps")

        return {"table": "dim_temps", "rows": row_count, "status": "SUCCESS"}

    def create_dim_patient(self):
        """Create patient dimension from Silver"""
        logger.info("Creating patient dimension")

        try:
            df_silver = self.spark.read.parquet(f"{self.silver_base}/patient")

            dim_patient = df_silver.select(
                col("id_patient"),
                col("nom_hash"),
                col("prenom_hash"),
                col("sexe"),
                col("age"),
                col("date_naissance"),
                col("ville"),
                col("code_postal"),
                col("pays"),
                col("groupe_sanguin")
            )

            row_count = dim_patient.count()
            logger.info(f"Created dimension with {row_count:,} patients")

            dim_patient.write.mode("overwrite").parquet(f"{self.gold_output}/dim_patient")
            logger.info("Saved dim_patient")

            return {"table": "dim_patient", "rows": row_count, "status": "SUCCESS"}

        except Exception as e:
            logger.error(f"Error creating dim_patient: {str(e)}")
            return {"table": "dim_patient", "rows": 0, "status": f"ERROR: {str(e)}"}

    def create_dim_diagnostic(self):
        """Create diagnostic dimension from Silver"""
        logger.info("Creating diagnostic dimension")

        try:
            df_silver = self.spark.read.parquet(f"{self.silver_base}/diagnostic")

            dim_diagnostic = df_silver.select(
                col("Code_diag").alias("code_diag"),
                col("Diagnostic").alias("libelle"),
                substring(col("Code_diag"), 1, 1).alias("categorie")
            ).dropDuplicates(["code_diag"])

            row_count = dim_diagnostic.count()
            logger.info(f"Created dimension with {row_count:,} diagnostics")

            dim_diagnostic.write.mode("overwrite").parquet(f"{self.gold_output}/dim_diagnostic")
            logger.info("Saved dim_diagnostic")

            return {"table": "dim_diagnostic", "rows": row_count, "status": "SUCCESS"}

        except Exception as e:
            logger.error(f"Error creating dim_diagnostic: {str(e)}")
            return {"table": "dim_diagnostic", "rows": 0, "status": f"ERROR: {str(e)}"}

    def create_dim_professionnel(self):
        """Create healthcare professional dimension from Silver"""
        logger.info("Creating professional dimension")

        try:
            df_prof = self.spark.read.parquet(f"{self.silver_base}/professionnel_de_sante")
            df_spec = self.spark.read.parquet(f"{self.silver_base}/specialites")

            dim_professionnel = df_prof.select(
                col("Identifiant").alias("id_prof"),
                col("Nom").alias("nom"),
                col("Prenom").alias("prenom"),
                col("Code_specialite").alias("code_specialite")
            ).dropDuplicates(["id_prof"])

            dim_professionnel = dim_professionnel.join(
                df_spec.select(
                    col("Code_specialite"),
                    col("Specialite").alias("nom_specialite")
                ),
                on="code_specialite",
                how="left"
            )

            row_count = dim_professionnel.count()
            logger.info(f"Created dimension with {row_count:,} professionals")

            dim_professionnel.write.mode("overwrite").parquet(f"{self.gold_output}/dim_professionnel")
            logger.info("Saved dim_professionnel")

            return {"table": "dim_professionnel", "rows": row_count, "status": "SUCCESS"}

        except Exception as e:
            logger.error(f"Error creating dim_professionnel: {str(e)}")
            return {"table": "dim_professionnel", "rows": 0, "status": f"ERROR: {str(e)}"}

    def create_dim_etablissement(self):
        """Create healthcare facility dimension from Silver"""
        logger.info("Creating facility dimension")

        try:
            df_etab = self.spark.read.parquet(f"{self.silver_base}/etablissement_sante")
            df_dept = self.spark.read.parquet(f"{self.bronze_base}/csv/departements")

            dim_etablissement = df_etab.select(
                col("finess_site").alias("finess"),
                col("siret_site").alias("siret"),
                col("raison_sociale").alias("nom"),
                col("commune").alias("ville"),
                col("code_postal"),
                col("telephone"),
                col("email"),
                substring(col("code_postal"), 1, 2).alias("code_departement")
            ).filter(
                col("finess").isNotNull()
            ).dropDuplicates(["finess"])

            dim_etablissement = dim_etablissement.join(
                df_dept.select(
                    col("num_departement"),
                    col("libelle_departement"),
                    col("libelle_region"),
                    col("abv_region")
                ),
                dim_etablissement["code_departement"] == df_dept["num_departement"],
                "left"
            )

            row_count = dim_etablissement.count()
            logger.info(f"Created dimension with {row_count:,} facilities")

            dim_etablissement.write.mode("overwrite").parquet(f"{self.gold_output}/dim_etablissement")
            logger.info("Saved dim_etablissement")

            return {"table": "dim_etablissement", "rows": row_count, "status": "SUCCESS"}

        except Exception as e:
            logger.error(f"Error creating dim_etablissement: {str(e)}")
            return {"table": "dim_etablissement", "rows": 0, "status": f"ERROR: {str(e)}"}

    def create_fait_consultation(self):
        """Create consultation fact table from Silver"""
        logger.info("Creating consultation fact table")

        try:
            df_silver = self.spark.read.parquet(f"{self.silver_base}/consultation")

            fait_consultation = df_silver.select(
                col("id_consultation"),
                col("id_patient"),
                col("id_professionnel").alias("id_prof"),
                col("id_diagnostic").alias("code_diag"),
                col("id_mutuelle"),
                date_format(col("date_consultation"), "yyyyMMdd").alias("id_temps"),
                col("date_consultation"),
                col("annee"),
                col("mois"),
                col("jour"),
                col("heure_debut"),
                col("heure_fin"),
                col("motif")
            )

            row_count = fait_consultation.count()
            logger.info(f"Created fact table with {row_count:,} consultations")

            fait_consultation.write \
                .mode("overwrite") \
                .partitionBy("annee", "mois") \
                .parquet(f"{self.gold_output}/fait_consultation")

            logger.info("Saved fait_consultation (partitioned by annee, mois)")

            return {"table": "fait_consultation", "rows": row_count, "status": "SUCCESS"}

        except Exception as e:
            logger.error(f"Error creating fait_consultation: {str(e)}")
            return {"table": "fait_consultation", "rows": 0, "status": f"ERROR: {str(e)}"}

    def create_fait_hospitalisation(self):
        """Create hospitalization fact table from AAAA + date tables"""
        logger.info("Creating hospitalization fact table")

        try:
            df_aaaa = self.spark.read.parquet(f"{self.bronze_base}/postgres/AAAA") \
                .drop("ingestion_timestamp", "ingestion_date")
            df_date = self.spark.read.parquet(f"{self.bronze_base}/postgres/date") \
                .drop("ingestion_timestamp", "ingestion_date")

            logger.info(f"Loaded AAAA: {df_aaaa.count():,} rows")
            logger.info(f"Loaded date: {df_date.count():,} rows")

            df_aaaa_idx = df_aaaa.withColumn("row_id", monotonically_increasing_id())
            df_date_idx = df_date.withColumn("row_id", monotonically_increasing_id())

            df_hospit_raw = df_aaaa_idx.join(df_date_idx, "row_id", "inner")

            fait_hospitalisation = df_hospit_raw.select(
                monotonically_increasing_id().alias("id_hospitalisation"),
                col("Num").alias("id_patient"),
                col("Code_diag").alias("code_diag"),
                to_date(col("date1"), "dd/MM/yyyy").alias("date_entree"),
                to_date(col("date2"), "dd/MM/yyyy").alias("date_sortie"),
                date_format(to_date(col("date1"), "dd/MM/yyyy"), "yyyyMMdd").alias("id_temps_entree"),
                date_format(to_date(col("date2"), "dd/MM/yyyy"), "yyyyMMdd").alias("id_temps_sortie"),
                datediff(
                    to_date(col("date2"), "dd/MM/yyyy"),
                    to_date(col("date1"), "dd/MM/yyyy")
                ).alias("duree_sejour_jours"),
                year(to_date(col("date1"), "dd/MM/yyyy")).alias("annee"),
                month(to_date(col("date1"), "dd/MM/yyyy")).alias("mois")
            ).filter(
                (col("date_entree").isNotNull()) &
                (col("date_sortie").isNotNull()) &
                (col("duree_sejour_jours") >= 0)
            )

            row_count = fait_hospitalisation.count()
            logger.info(f"Created fact table with {row_count:,} hospitalizations")

            fait_hospitalisation.write \
                .mode("overwrite") \
                .partitionBy("annee", "mois") \
                .parquet(f"{self.gold_output}/fait_hospitalisation")

            logger.info("Saved fait_hospitalisation (partitioned by annee, mois)")

            return {"table": "fait_hospitalisation", "rows": row_count, "status": "SUCCESS"}

        except Exception as e:
            logger.error(f"Error creating fait_hospitalisation: {str(e)}")
            return {"table": "fait_hospitalisation", "rows": 0, "status": f"ERROR: {str(e)}"}

    def create_fait_deces(self):
        """Create death fact table from Silver"""
        logger.info("Creating death fact table")

        try:
            df_silver = self.spark.read.parquet(f"{self.silver_base}/deces_2019")

            fait_deces = df_silver.select(
                monotonically_increasing_id().alias("id_deces"),
                col("nom_hash"),
                col("prenom_hash"),
                col("acte_deces_hash"),
                col("sexe"),
                col("date_naissance"),
                col("date_deces"),
                col("age_deces"),
                date_format(col("date_deces"), "yyyyMMdd").alias("id_temps"),
                col("annee_deces").alias("annee"),
                col("mois_deces").alias("mois"),
                col("code_lieu_naissance"),
                col("lieu_naissance"),
                col("pays_naissance"),
                col("code_lieu_deces")
            )

            row_count = fait_deces.count()
            logger.info(f"Created fact table with {row_count:,} deaths")

            fait_deces.write \
                .mode("overwrite") \
                .partitionBy("annee", "mois") \
                .parquet(f"{self.gold_output}/fait_deces")

            logger.info("Saved fait_deces (partitioned by annee, mois)")

            return {"table": "fait_deces", "rows": row_count, "status": "SUCCESS"}

        except Exception as e:
            logger.error(f"Error creating fait_deces: {str(e)}")
            return {"table": "fait_deces", "rows": 0, "status": f"ERROR: {str(e)}"}

    def create_fait_satisfaction(self):
        """Create satisfaction fact table from Silver"""
        logger.info("Creating satisfaction fact table")

        try:
            df_silver = self.spark.read.parquet(f"{self.silver_base}/satisfaction_2019")

            fait_satisfaction = df_silver.select(
                monotonically_increasing_id().alias("id_satisfaction"),
                col("finess"),
                lit("20190101").alias("id_temps"),
                col("annee"),
                col("score_global"),
                col("score_accueil"),
                col("score_pec_infirmier"),
                col("score_pec_medical"),
                col("score_chambre"),
                col("score_repas"),
                col("score_sortie"),
                col("taux_recommandation"),
                col("nb_reponses_global").alias("nb_repondants"),
                col("nb_recommandations"),
                col("classement"),
                col("evolution")
            )

            row_count = fait_satisfaction.count()
            logger.info(f"Created fact table with {row_count:,} satisfaction evaluations")

            fait_satisfaction.write \
                .mode("overwrite") \
                .partitionBy("annee") \
                .parquet(f"{self.gold_output}/fait_satisfaction")

            logger.info("Saved fait_satisfaction (partitioned by annee)")

            return {"table": "fait_satisfaction", "rows": row_count, "status": "SUCCESS"}

        except Exception as e:
            logger.error(f"Error creating fait_satisfaction: {str(e)}")
            return {"table": "fait_satisfaction", "rows": 0, "status": f"ERROR: {str(e)}"}

    def print_summary(self):
        """Print transformation summary"""
        success = [r for r in self.results if r["status"] == "SUCCESS"]
        total_rows = sum(r["rows"] for r in success)

        logger.info("=" * 60)
        logger.info("GOLD STAR SCHEMA SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Tables created: {len(success)}/{len(self.results)}")
        logger.info(f"Total rows: {total_rows:,}")
        logger.info("=" * 60)

        dimensions = [r for r in success if r["table"].startswith("dim_")]
        facts = [r for r in success if r["table"].startswith("fait_")]

        logger.info(f"Dimensions: {len(dimensions)}")
        for result in dimensions:
            logger.info(f"  {result['table']:30} | {result['rows']:>10,} rows")

        logger.info(f"Facts: {len(facts)}")
        for result in facts:
            logger.info(f"  {result['table']:30} | {result['rows']:>10,} rows")


def create_spark_session():
    """Create Spark session with optimal configuration"""
    return SparkSession.builder \
        .appName("CHU - Gold Star Schema") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.sql.adaptive.skewJoin.enabled", "true") \
        .config("spark.sql.autoBroadcastJoinThreshold", "10485760") \
        .getOrCreate()


def main():
    """Main execution function"""
    logger.info("Starting Gold Star Schema Creation")

    spark = create_spark_session()
    logger.info(f"Spark {spark.version} initialized with optimizations")

    try:
        transformer = GoldTransformer(spark)

        transformer.results.append(transformer.create_dim_temps())
        transformer.results.append(transformer.create_dim_patient())
        transformer.results.append(transformer.create_dim_diagnostic())
        transformer.results.append(transformer.create_dim_professionnel())
        transformer.results.append(transformer.create_dim_etablissement())

        transformer.results.append(transformer.create_fait_consultation())
        transformer.results.append(transformer.create_fait_hospitalisation())
        transformer.results.append(transformer.create_fait_deces())
        transformer.results.append(transformer.create_fait_satisfaction())

        transformer.print_summary()

        logger.info("Gold star schema creation completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Gold transformation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    sys.exit(main())
