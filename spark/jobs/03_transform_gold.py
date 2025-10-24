"""
Gold Layer Transformation Job

Creates star schema dimensional model from Silver data.
Includes 5 dimensions and 4 fact tables with temporal partitioning.

Authors: Nejma MOUALHI, Brieuc OLIVIERI, Nicolas TAING
Date: October 2025
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, countDistinct,
    min as spark_min, max as spark_max, avg as spark_avg, sum as spark_sum,
    year, month, dayofmonth, date_format, datediff,
    monotonically_increasing_id, lit, substring, to_date,
    lag, row_number, concat_ws
)
from pyspark.sql.types import *
from datetime import datetime, timedelta
import sys
import logging
import os
from pyspark.sql.window import Window
import argparse
import shutil

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GoldTransformer:
    """Handles transformation of Silver to Gold star schema"""

    def __init__(self, spark):
        self.spark = spark
        data_base = os.getenv("DATA_BASE", "/opt/spark-data")
        self.silver_base = f"{data_base}/silver"
        self.bronze_base = f"{data_base}/bronze"
        self.gold_output = f"{data_base}/gold"
        self.results = []

    @staticmethod
    def _rm_rf(path: str):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
            elif os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logger.warning(f"Could not pre-delete path {path}: {e}")

    def _write_parquet_atomic(self, df, out_path: str, partition_cols=None):
        """Write to a temp path then swap into place to avoid clear-dir errors.

        - Writes df to out_path.tmp (overwrite)
        - Removes existing out_path if present
        - Moves tmp into final out_path
        """
        tmp_path = f"{out_path}.tmp_write"
        # Clean tmp and write
        self._rm_rf(tmp_path)
        writer = df.write.mode("overwrite").option(
            "mapreduce.fileoutputcommitter.marksuccessfuljobs", "false"
        )
        if partition_cols:
            writer = writer.partitionBy(*partition_cols)
        writer.parquet(tmp_path)
        # Swap
        self._rm_rf(out_path)
        try:
            os.replace(tmp_path, out_path)
        except Exception:
            shutil.move(tmp_path, out_path)

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

        self._write_parquet_atomic(dim_temps, f"{self.gold_output}/dim_temps")
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

            self._write_parquet_atomic(dim_patient, f"{self.gold_output}/dim_patient")
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

            self._write_parquet_atomic(dim_diagnostic, f"{self.gold_output}/dim_diagnostic")
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

            self._write_parquet_atomic(dim_professionnel, f"{self.gold_output}/dim_professionnel")
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

            self._write_parquet_atomic(dim_etablissement, f"{self.gold_output}/dim_etablissement")
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

            self._write_parquet_atomic(
                fait_consultation, f"{self.gold_output}/fait_consultation", partition_cols=["annee", "mois"]
            )

            logger.info("Saved fait_consultation (partitioned by annee, mois)")

            return {"table": "fait_consultation", "rows": row_count, "status": "SUCCESS"}

        except Exception as e:
            logger.error(f"Error creating fait_consultation: {str(e)}")
            return {"table": "fait_consultation", "rows": 0, "status": f"ERROR: {str(e)}"}

    def create_fait_hospitalisation(self):
        """Create hospitalization episodes from Silver consultations"""
        logger.info("Creating hospitalization fact table from consultation episodes")

        try:
            df_cons = self.spark.read.parquet(f"{self.silver_base}/consultation").select(
                col("id_patient"),
                col("id_diagnostic").alias("code_diag"),
                to_date(col("date_consultation")).alias("date_consultation")
            ).filter(col("date_consultation").isNotNull())

            if df_cons.rdd.isEmpty():
                logger.warning("Silver consultation dataset is empty; skipping fait_hospitalisation")
                return {"table": "fait_hospitalisation", "rows": 0, "status": "EMPTY"}

            w_order = Window.partitionBy("id_patient").orderBy(col("date_consultation"))
            w_cum = w_order.rowsBetween(Window.unboundedPreceding, Window.currentRow)

            lag_date = lag("date_consultation", 1).over(w_order)
            gap_days = datediff(col("date_consultation"), lag_date)
            new_episode = (lag_date.isNull() | (gap_days > 1)).cast("int")

            df_seq = df_cons.withColumn("new_ep", new_episode) \
                .withColumn("episode_seq", spark_sum(col("new_ep")).over(w_cum)) \
                .withColumn("episode_id", concat_ws("_",
                                      col("id_patient").cast("string"),
                                      col("episode_seq").cast("string")))

            # Diagnostic mode per episode (most frequent)
            diag_counts = df_seq.groupBy("episode_id", "id_patient", "code_diag").count()
            w_rank = Window.partitionBy("episode_id").orderBy(col("count").desc(), col("code_diag"))
            top_diag = diag_counts.withColumn("r", row_number().over(w_rank)) \
                                 .filter(col("r") == 1) \
                                 .select("episode_id", col("code_diag").alias("code_diag_mode"))

            # Aggregate to episodes
            from pyspark.sql.functions import min as fmin, max as fmax, countDistinct
            episodes = df_seq.groupBy("id_patient", "episode_id").agg(
                fmin("date_consultation").alias("date_entree"),
                fmax("date_consultation").alias("date_sortie"),
                count("*").alias("nb_consultations"),
                countDistinct("date_consultation").alias("nb_jours_distincts")
            ).join(top_diag, "episode_id", "left")

            episodes = episodes.withColumn(
                "duree_sejour_jours",
                datediff(col("date_sortie"), col("date_entree")) + lit(1)
            ).filter(
                (col("duree_sejour_jours") >= lit(2)) | (col("nb_jours_distincts") >= lit(2))
            )

            fait_hosp = episodes.select(
                monotonically_increasing_id().alias("id_hospitalisation"),
                col("id_patient"),
                col("code_diag_mode").alias("code_diag"),
                col("date_entree"),
                col("date_sortie"),
                date_format(col("date_entree"), "yyyyMMdd").alias("id_temps_entree"),
                date_format(col("date_sortie"), "yyyyMMdd").alias("id_temps_sortie"),
                col("duree_sejour_jours"),
                col("nb_consultations"),
                year(col("date_entree")).alias("annee"),
                month(col("date_entree")).alias("mois")
            )

            row_count = fait_hosp.count()
            logger.info(f"Created fact table with {row_count:,} hospitalization episodes")

            self._write_parquet_atomic(
                fait_hosp, f"{self.gold_output}/fait_hospitalisation", partition_cols=["annee", "mois"]
            )

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

            self._write_parquet_atomic(
                fait_deces, f"{self.gold_output}/fait_deces", partition_cols=["annee", "mois"]
            )

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

            self._write_parquet_atomic(
                fait_satisfaction, f"{self.gold_output}/fait_satisfaction", partition_cols=["annee"]
            )

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
    master = os.getenv("SPARK_MASTER_URL", "local[*]")
    builder = (
        SparkSession.builder
        .appName(os.getenv("SPARK_APP_NAME", "CHU - Gold Star Schema"))
        .config("spark.driver.memory", os.getenv("SPARK_DRIVER_MEMORY", "4g"))
        .config("spark.executor.memory", os.getenv("SPARK_EXECUTOR_MEMORY", "4g"))
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .config("spark.sql.adaptive.skewJoin.enabled", "true")
        .config("spark.sql.autoBroadcastJoinThreshold", "10485760")
        .config("spark.jars.packages", os.getenv("SPARK_PACKAGES", "org.postgresql:postgresql:42.7.3"))
    )
    if master:
        builder = builder.master(master)
    return builder.getOrCreate()


def main():
    """Main execution function"""
    logger.info("Starting Gold Star Schema Creation")

    spark = create_spark_session()
    logger.info(f"Spark {spark.version} initialized with optimizations")

    try:
        transformer = GoldTransformer(spark)

        parser = argparse.ArgumentParser(description="Gold star-schema creation job")
        parser.add_argument(
            "--task",
            choices=[
                "dim_temps", "dim_patient", "dim_diagnostic", "dim_professionnel", "dim_etablissement",
                "fait_consultation", "fait_hospitalisation", "fait_deces", "fait_satisfaction", "all"
            ],
            help="Run only a specific table build or all",
        )
        args = parser.parse_args()
        task = args.task or "all"

        if task in ("dim_temps", "all"):
            transformer.results.append(transformer.create_dim_temps())
        if task in ("dim_patient", "all"):
            transformer.results.append(transformer.create_dim_patient())
        if task in ("dim_diagnostic", "all"):
            transformer.results.append(transformer.create_dim_diagnostic())
        if task in ("dim_professionnel", "all"):
            transformer.results.append(transformer.create_dim_professionnel())
        if task in ("dim_etablissement", "all"):
            transformer.results.append(transformer.create_dim_etablissement())

        if task in ("fait_consultation", "all"):
            transformer.results.append(transformer.create_fait_consultation())
        if task in ("fait_hospitalisation", "all"):
            transformer.results.append(transformer.create_fait_hospitalisation())
        if task in ("fait_deces", "all"):
            transformer.results.append(transformer.create_fait_deces())
        if task in ("fait_satisfaction", "all"):
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
