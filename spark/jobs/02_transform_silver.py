"""
Silver Layer Transformation Job

Cleans and anonymizes Bronze data according to GDPR requirements.
Applies data quality rules and standardizes formats.

Authors: Nejma MOUALHI, Brieuc OLIVIERI, Nicolas TAING
Date: October 2025
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, sha2, when, trim, upper,
    to_date, year, month, dayofmonth,
    regexp_replace, coalesce, lit,
    current_timestamp
)
import sys
import logging
import os
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SilverTransformer:
    """Handles transformation and cleaning of Bronze to Silver layer"""

    def __init__(self, spark):
        self.spark = spark
        data_base = os.getenv("DATA_BASE", "/opt/spark-data")
        self.bronze_base = f"{data_base}/bronze"
        self.silver_base = f"{data_base}/silver"
        self.results = []

    def transform_patient(self):
        """Anonymize patient data (GDPR compliance)"""
        logger.info("Transforming patient data with anonymization")

        try:
            df_bronze = self.spark.read.parquet(f"{self.bronze_base}/postgres/Patient")
            row_count_in = df_bronze.count()
            logger.info(f"Read {row_count_in:,} patients from Bronze")

            df_silver = df_bronze.select(
                col("Id_patient").alias("id_patient"),

                # GDPR: Hash sensitive data with SHA-256
                sha2(col("Nom"), 256).alias("nom_hash"),
                sha2(col("Prenom"), 256).alias("prenom_hash"),

                # Demographic data (non-sensitive)
                col("Sexe").alias("sexe"),
                col("Age").cast("integer").alias("age"),

                # Date format standardization: M/d/yyyy to yyyy-MM-dd
                to_date(col("Date"), "M/d/yyyy").alias("date_naissance"),

                # Geographic data (aggregated level acceptable for GDPR)
                trim(upper(col("Ville"))).alias("ville"),
                col("Code_postal").alias("code_postal"),
                trim(upper(col("Pays"))).alias("pays"),

                # Medical information
                col("Poid").cast("double").alias("poids_kg"),
                col("Taille").cast("double").alias("taille_cm"),
                trim(upper(col("Groupe_sanguin"))).alias("groupe_sanguin"),

                # Contact information (hashed)
                sha2(col("Tel"), 256).alias("telephone_hash"),
                sha2(col("EMail"), 256).alias("email_hash"),

                # Social security number (hashed)
                sha2(col("Num_Secu"), 256).alias("num_secu_hash"),

                # Metadata
                col("ingestion_date"),
                current_timestamp().alias("transformation_timestamp")
            ).dropDuplicates(["id_patient"])

            row_count_out = df_silver.count()
            logger.info(f"Anonymized {row_count_out:,} patients (removed {row_count_in - row_count_out} duplicates)")

            df_silver.write.mode("overwrite").parquet(f"{self.silver_base}/patient")
            logger.info("Saved patient data to Silver")

            return {"table": "patient", "rows": row_count_out, "status": "SUCCESS"}

        except Exception as e:
            logger.error(f"Error transforming patient: {str(e)}")
            return {"table": "patient", "rows": 0, "status": f"ERROR: {str(e)}"}

    def transform_consultation(self):
        """Clean consultation data with date standardization"""
        logger.info("Transforming consultation data")

        try:
            df_bronze = self.spark.read.parquet(f"{self.bronze_base}/postgres/Consultation")
            row_count_in = df_bronze.count()
            logger.info(f"Read {row_count_in:,} consultations from Bronze")

            df_silver = df_bronze.select(
                col("Num_consultation").alias("id_consultation"),
                col("Id_patient").alias("id_patient"),
                col("Code_diag").alias("id_diagnostic"),
                col("Id_prof_sante").alias("id_professionnel"),
                col("Id_mut").alias("id_mutuelle"),

                # Date format: M/d/yyyy to yyyy-MM-dd
                to_date(col("Date"), "M/d/yyyy").alias("date_consultation"),

                # Extract temporal components for partitioning
                year(to_date(col("Date"), "M/d/yyyy")).alias("annee"),
                month(to_date(col("Date"), "M/d/yyyy")).alias("mois"),
                dayofmonth(to_date(col("Date"), "M/d/yyyy")).alias("jour"),

                # Time information
                col("Heure_debut").alias("heure_debut"),
                col("Heure_fin").alias("heure_fin"),

                # Consultation reason
                trim(col("Motif")).alias("motif"),

                # Metadata
                col("ingestion_date"),
                current_timestamp().alias("transformation_timestamp")
            ).filter(
                # Validation: dates between 2013-2025
                (col("annee") >= 2013) & (col("annee") <= 2025)
            ).dropDuplicates(["id_consultation"])

            row_count_out = df_silver.count()
            logger.info(f"Cleaned {row_count_out:,} consultations")

            df_silver.write.mode("overwrite").parquet(f"{self.silver_base}/consultation")
            logger.info("Saved consultation data to Silver")

            return {"table": "consultation", "rows": row_count_out, "status": "SUCCESS"}

        except Exception as e:
            logger.error(f"Error transforming consultation: {str(e)}")
            return {"table": "consultation", "rows": 0, "status": f"ERROR: {str(e)}"}

    def transform_etablissement_sante(self):
        """Clean healthcare facilities data from CSV"""
        logger.info("Transforming healthcare facilities data")

        try:
            df_bronze = self.spark.read.parquet(f"{self.bronze_base}/csv/etablissement_sante")
            row_count_in = df_bronze.count()
            logger.info(f"Read {row_count_in:,} facilities from Bronze")

            df_silver = df_bronze.select(
                # Identifiers
                trim(col("finess_site")).alias("finess_site"),
                trim(col("siret_site")).alias("siret_site"),
                trim(col("siren_site")).alias("siren_site"),

                # Names
                trim(col("raison_sociale_site")).alias("raison_sociale"),
                trim(col("enseigne_commerciale_site")).alias("enseigne_commerciale"),

                # Address (normalized)
                trim(col("numero_voie")).alias("numero_voie"),
                trim(upper(col("type_voie"))).alias("type_voie"),
                trim(upper(col("voie"))).alias("voie"),
                trim(col("code_postal")).alias("code_postal"),
                trim(upper(col("commune"))).alias("commune"),
                trim(col("cedex")).alias("cedex"),
                trim(upper(col("pays"))).alias("pays"),

                # Contact (public data, not hashed)
                regexp_replace(col("telephone"), "[^0-9]", "").alias("telephone"),
                trim(col("email")).alias("email"),

                # Metadata
                col("ingestion_date"),
                current_timestamp().alias("transformation_timestamp")
            ).filter(
                # Validation: at least one identifier present
                col("finess_site").isNotNull() | col("siret_site").isNotNull()
            ).dropDuplicates(["finess_site", "siret_site"])

            row_count_out = df_silver.count()
            logger.info(f"Cleaned {row_count_out:,} facilities")

            df_silver.write.mode("overwrite").parquet(f"{self.silver_base}/etablissement_sante")
            logger.info("Saved facility data to Silver")

            return {"table": "etablissement_sante", "rows": row_count_out, "status": "SUCCESS"}

        except Exception as e:
            logger.error(f"Error transforming facilities: {str(e)}")
            return {"table": "etablissement_sante", "rows": 0, "status": f"ERROR: {str(e)}"}

    def transform_satisfaction(self):
        """Clean satisfaction survey data from CSV"""
        logger.info("Transforming satisfaction data")

        try:
            df_bronze = self.spark.read.parquet(f"{self.bronze_base}/csv/satisfaction_esatis48h_2019")
            row_count_in = df_bronze.count()
            logger.info(f"Read {row_count_in:,} satisfaction records from Bronze")

            df_silver = df_bronze.select(
                # Identifiers
                trim(col("finess")).alias("finess"),
                trim(col("finess_geo")).alias("finess_geo"),
                trim(col("region")).alias("region"),
                trim(col("rs_finess")).alias("raison_sociale_finess"),

                # Participation
                trim(col("participation")).alias("participation"),
                trim(col("depot")).alias("depot"),

                # Scores (cast to double)
                col("score_all_rea_ajust").cast("double").alias("score_global"),
                col("score_accueil_rea_ajust").cast("double").alias("score_accueil"),
                col("score_PECinf_rea_ajust").cast("double").alias("score_pec_infirmier"),
                col("score_PECmed_rea_ajust").cast("double").alias("score_pec_medical"),
                col("score_chambre_rea_ajust").cast("double").alias("score_chambre"),
                col("score_repas_rea_ajust").cast("double").alias("score_repas"),
                col("score_sortie_rea_ajust").cast("double").alias("score_sortie"),

                # Response counts
                col("nb_rep_score_all_rea_ajust").cast("integer").alias("nb_reponses_global"),
                col("nb_reco_brut").cast("integer").alias("nb_recommandations"),
                col("taux_reco_brut").cast("double").alias("taux_recommandation"),

                # Classification
                trim(col("classement")).alias("classement"),
                trim(col("evolution")).alias("evolution"),

                # Fixed year
                lit(2019).alias("annee"),

                # Metadata
                col("ingestion_date"),
                current_timestamp().alias("transformation_timestamp")
            ).filter(
                col("score_global").isNotNull()
            ).dropDuplicates(["finess"])

            row_count_out = df_silver.count()
            logger.info(f"Cleaned {row_count_out:,} satisfaction records")

            df_silver.write.mode("overwrite").parquet(f"{self.silver_base}/satisfaction_2019")
            logger.info("Saved satisfaction data to Silver")

            return {"table": "satisfaction_2019", "rows": row_count_out, "status": "SUCCESS"}

        except Exception as e:
            logger.error(f"Error transforming satisfaction: {str(e)}")
            return {"table": "satisfaction_2019", "rows": 0, "status": f"ERROR: {str(e)}"}

    def transform_deces(self):
        """Anonymize death records (GDPR compliance)"""
        logger.info("Transforming death records with anonymization")

        try:
            df_bronze = self.spark.read.parquet(f"{self.bronze_base}/csv/deces_2019")
            row_count_in = df_bronze.count()
            logger.info(f"Read {row_count_in:,} death records from Bronze")

            df_silver = df_bronze.select(
                # GDPR: Hash identities
                sha2(col("nom"), 256).alias("nom_hash"),
                sha2(col("prenom"), 256).alias("prenom_hash"),
                sha2(col("numero_acte_deces"), 256).alias("acte_deces_hash"),

                # Demographics
                col("sexe"),
                to_date(col("date_naissance")).alias("date_naissance"),
                to_date(col("date_deces")).alias("date_deces"),

                # Calculated age at death
                (year(to_date(col("date_deces"))) - year(to_date(col("date_naissance")))).alias("age_deces"),

                # Geographic data (aggregated acceptable for GDPR)
                trim(col("code_lieu_naissance")).alias("code_lieu_naissance"),
                trim(upper(col("lieu_naissance"))).alias("lieu_naissance"),
                trim(upper(col("pays_naissance"))).alias("pays_naissance"),
                trim(col("code_lieu_deces")).alias("code_lieu_deces"),

                # Temporal components
                year(to_date(col("date_deces"))).alias("annee_deces"),
                month(to_date(col("date_deces"))).alias("mois_deces"),

                # Metadata
                col("ingestion_date"),
                current_timestamp().alias("transformation_timestamp")
            ).filter(
                # Validation: coherent dates and ages
                (col("date_deces").isNotNull()) &
                (col("annee_deces") == 2019) &
                (col("age_deces") >= 0) & (col("age_deces") <= 120)
            )

            row_count_out = df_silver.count()
            logger.info(f"Anonymized {row_count_out:,} death records")

            df_silver.write.mode("overwrite").parquet(f"{self.silver_base}/deces_2019")
            logger.info("Saved death records to Silver")

            return {"table": "deces_2019", "rows": row_count_out, "status": "SUCCESS"}

        except Exception as e:
            logger.error(f"Error transforming deaths: {str(e)}")
            return {"table": "deces_2019", "rows": 0, "status": f"ERROR: {str(e)}"}

    def transform_reference_tables(self):
        """Clean reference tables (basic cleaning only)"""
        reference_tables = [
            "Diagnostic",
            "Professionnel_de_sante",
            "Mutuelle",
            "Medicaments",
            "Laboratoire",
            "Salle",
            "Specialites",
            "AAAA",
            "date",
            "Adher",
            "Prescription"
        ]

        logger.info(f"Transforming {len(reference_tables)} reference tables")

        for table in reference_tables:
            try:
                logger.info(f"Processing {table}")

                df = self.spark.read.parquet(f"{self.bronze_base}/postgres/{table}")

                # Basic cleaning: trim strings
                df_clean = df
                for col_name in df.columns:
                    if dict(df.dtypes)[col_name] == 'string':
                        df_clean = df_clean.withColumn(col_name, trim(col(col_name)))

                # Add metadata
                df_clean = df_clean.withColumn(
                    "transformation_timestamp",
                    current_timestamp()
                )

                # Save
                output_path = f"{self.silver_base}/{table.lower()}"
                df_clean.write.mode("overwrite").parquet(output_path)

                row_count = df_clean.count()
                logger.info(f"Cleaned {row_count:,} rows for {table}")

                self.results.append({
                    "table": table.lower(),
                    "rows": row_count,
                    "status": "SUCCESS"
                })

            except Exception as e:
                logger.error(f"Error transforming {table}: {str(e)}")
                self.results.append({
                    "table": table.lower(),
                    "rows": 0,
                    "status": f"ERROR: {str(e)}"
                })

    def print_summary(self):
        """Print transformation summary"""
        success = [r for r in self.results if r["status"] == "SUCCESS"]
        total_rows = sum(r["rows"] for r in success)

        logger.info("=" * 60)
        logger.info("TRANSFORMATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Tables transformed: {len(success)}/{len(self.results)}")
        logger.info(f"Total rows: {total_rows:,}")
        logger.info("=" * 60)

        for result in self.results:
            status_symbol = "OK" if result["status"] == "SUCCESS" else "ERROR"
            logger.info(f"{result['table']:30} | {result['rows']:>10,} rows | {status_symbol}")


def create_spark_session():
    """Create Spark session with optimal configuration"""
    master = os.getenv("SPARK_MASTER_URL", "local[*]")
    builder = (
        SparkSession.builder
        .appName(os.getenv("SPARK_APP_NAME", "CHU - Silver Transformation"))
        .config("spark.driver.memory", os.getenv("SPARK_DRIVER_MEMORY", "4g"))
        .config("spark.executor.memory", os.getenv("SPARK_EXECUTOR_MEMORY", "4g"))
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.jars.packages", os.getenv("SPARK_PACKAGES", "org.postgresql:postgresql:42.7.3"))
    )
    if master:
        builder = builder.master(master)
    return builder.getOrCreate()


def main():
    """Main execution function"""
    logger.info("Starting Silver Layer Transformation")

    spark = create_spark_session()
    logger.info(f"Spark {spark.version} initialized")

    try:
        transformer = SilverTransformer(spark)

        parser = argparse.ArgumentParser(description="Silver transformation job")
        parser.add_argument(
            "--subject",
            choices=[
                "patient", "consultation", "etablissement_sante",
                "satisfaction", "satisfaction_2019", "deces", "deces_2019",
                "references", "all"
            ],
            help="Run only a specific subject or all",
        )
        args = parser.parse_args()

        subj = args.subject or "all"

        if subj in ("patient", "all"):
            transformer.results.append(transformer.transform_patient())
        if subj in ("consultation", "all"):
            transformer.results.append(transformer.transform_consultation())
        if subj in ("etablissement_sante", "all"):
            transformer.results.append(transformer.transform_etablissement_sante())
        if subj in ("satisfaction", "satisfaction_2019", "all"):
            transformer.results.append(transformer.transform_satisfaction())
        if subj in ("deces", "deces_2019", "all"):
            transformer.results.append(transformer.transform_deces())
        if subj in ("references", "all"):
            transformer.transform_reference_tables()

        transformer.print_summary()

        logger.info("Silver transformation completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Silver transformation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    sys.exit(main())
