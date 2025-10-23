"""
Performance Benchmarks Job

Measures query performance on Gold layer star schema.
Executes representative analytical queries and exports metrics.

Authors: Nejma MOUALHI, Brieuc OLIVIERI, Nicolas TAING
Date: October 2025
"""

from pyspark.sql import SparkSession
import time
import json
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BenchmarkRunner:
    """Executes and measures performance of analytical queries"""

    def __init__(self, spark):
        self.spark = spark
        self.gold_base = "/home/jovyan/data/gold"
        self.results = []

        self._load_gold_tables()

    def _load_gold_tables(self):
        """Load Gold tables into temporary views"""
        logger.info("Loading Gold tables into Spark SQL")

        tables = [
            "dim_temps", "dim_patient", "dim_diagnostic",
            "dim_professionnel", "dim_etablissement",
            "fait_consultation", "fait_hospitalisation",
            "fait_deces", "fait_satisfaction"
        ]

        for table in tables:
            try:
                df = self.spark.read.parquet(f"{self.gold_base}/{table}")
                df.createOrReplaceTempView(table)
                logger.info(f"Loaded {table}: {df.count():,} rows")
            except Exception as e:
                logger.warning(f"Could not load {table}: {str(e)}")

    def run_query(self, query_name, query_sql, runs=3):
        """Execute query multiple times and measure performance"""
        logger.info(f"Running benchmark: {query_name}")

        times = []
        result_count = 0

        for i in range(runs):
            self.spark.catalog.clearCache()

            start_time = time.time()
            try:
                result = self.spark.sql(query_sql)
                result_count = result.count()
                elapsed = time.time() - start_time
                times.append(elapsed)
                logger.info(f"  Run {i+1}: {elapsed:.3f}s | {result_count:,} rows")
            except Exception as e:
                logger.error(f"  Run {i+1}: ERROR - {str(e)}")
                times.append(None)

        valid_times = [t for t in times if t is not None]

        if valid_times:
            avg_time = sum(valid_times) / len(valid_times)
            min_time = min(valid_times)
            max_time = max(valid_times)
        else:
            avg_time = min_time = max_time = 0

        return {
            "query": query_name,
            "avg_time": round(avg_time, 3),
            "min_time": round(min_time, 3),
            "max_time": round(max_time, 3),
            "result_count": result_count,
            "runs": len(valid_times)
        }

    def benchmark_q1_count_consultations(self):
        """Q1: Simple aggregation - total consultations"""
        query = """
        SELECT COUNT(*) as total_consultations
        FROM fait_consultation
        """
        return self.run_query("Q1_Count_Total", query)

    def benchmark_q2_consultations_by_year(self):
        """Q2: Group by year - temporal analysis"""
        query = """
        SELECT
            annee,
            COUNT(*) as nb_consultations,
            COUNT(DISTINCT id_patient) as patients_uniques,
            COUNT(DISTINCT id_prof) as professionnels_uniques
        FROM fait_consultation
        GROUP BY annee
        ORDER BY annee
        """
        return self.run_query("Q2_Consultations_By_Year", query)

    def benchmark_q3_top_diagnostics(self):
        """Q3: Join + aggregation - top 10 diagnostics"""
        query = """
        SELECT
            d.code_diag,
            d.libelle,
            d.categorie,
            COUNT(*) as nb_consultations,
            COUNT(DISTINCT c.id_patient) as patients_concernes
        FROM fait_consultation c
        JOIN dim_diagnostic d ON c.code_diag = d.code_diag
        GROUP BY d.code_diag, d.libelle, d.categorie
        ORDER BY nb_consultations DESC
        LIMIT 10
        """
        return self.run_query("Q3_Top_Diagnostics", query)

    def benchmark_q4_consultations_by_specialite(self):
        """Q4: Multiple joins - consultations by medical specialty"""
        query = """
        SELECT
            p.nom_specialite,
            COUNT(*) as nb_consultations,
            COUNT(DISTINCT c.id_patient) as patients_uniques,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pourcentage
        FROM fait_consultation c
        JOIN dim_professionnel p ON c.id_prof = p.id_prof
        WHERE p.nom_specialite IS NOT NULL
        GROUP BY p.nom_specialite
        ORDER BY nb_consultations DESC
        LIMIT 15
        """
        return self.run_query("Q4_Consultations_By_Speciality", query)

    def benchmark_q5_temporal_filter(self):
        """Q5: Partition pruning - consultations for specific period"""
        query = """
        SELECT
            t.annee,
            t.mois,
            t.nom_mois,
            COUNT(*) as nb_consultations,
            COUNT(DISTINCT c.id_patient) as patients_uniques
        FROM fait_consultation c
        JOIN dim_temps t ON c.id_temps = t.id_temps
        WHERE t.annee = 2019
        GROUP BY t.annee, t.mois, t.nom_mois
        ORDER BY t.mois
        """
        return self.run_query("Q5_Temporal_Filter_2019", query)

    def benchmark_q6_hospitalisations_stats(self):
        """Q6: Hospitalization duration analysis"""
        query = """
        SELECT
            annee,
            COUNT(*) as nb_hospitalisations,
            ROUND(AVG(duree_sejour_jours), 2) as duree_moyenne_jours,
            MIN(duree_sejour_jours) as duree_min,
            MAX(duree_sejour_jours) as duree_max,
            COUNT(DISTINCT id_patient) as patients_uniques
        FROM fait_hospitalisation
        GROUP BY annee
        ORDER BY annee
        """
        return self.run_query("Q6_Hospitalisations_Stats", query)

    def benchmark_q7_deaths_by_age(self):
        """Q7: Deaths statistics by age group"""
        query = """
        SELECT
            CASE
                WHEN age_deces < 1 THEN '0-1 an'
                WHEN age_deces < 18 THEN '1-17 ans'
                WHEN age_deces < 65 THEN '18-64 ans'
                WHEN age_deces < 85 THEN '65-84 ans'
                ELSE '85+ ans'
            END as tranche_age,
            COUNT(*) as nb_deces,
            ROUND(AVG(age_deces), 1) as age_moyen,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pourcentage
        FROM fait_deces
        GROUP BY tranche_age
        ORDER BY
            CASE
                WHEN age_deces < 1 THEN 1
                WHEN age_deces < 18 THEN 2
                WHEN age_deces < 65 THEN 3
                WHEN age_deces < 85 THEN 4
                ELSE 5
            END
        """
        return self.run_query("Q7_Deaths_By_Age_Group", query)

    def benchmark_q8_satisfaction_by_region(self):
        """Q8: Satisfaction scores by region (if applicable)"""
        query = """
        SELECT
            e.libelle_region,
            COUNT(*) as nb_evaluations,
            ROUND(AVG(s.score_global), 2) as score_moyen,
            ROUND(AVG(s.score_accueil), 2) as score_accueil_moyen,
            ROUND(AVG(s.taux_recommandation), 2) as taux_reco_moyen
        FROM fait_satisfaction s
        JOIN dim_etablissement e ON s.finess = e.finess
        WHERE e.libelle_region IS NOT NULL
        GROUP BY e.libelle_region
        ORDER BY score_moyen DESC
        """
        return self.run_query("Q8_Satisfaction_By_Region", query)

    def benchmark_q9_consultations_multi_dimensions(self):
        """Q9: Complex query with multiple dimensions"""
        query = """
        SELECT
            t.annee,
            t.trimestre,
            pat.sexe,
            d.categorie as categorie_diagnostic,
            COUNT(*) as nb_consultations,
            COUNT(DISTINCT pat.id_patient) as patients_uniques
        FROM fait_consultation c
        JOIN dim_temps t ON c.id_temps = t.id_temps
        JOIN dim_patient pat ON c.id_patient = pat.id_patient
        JOIN dim_diagnostic d ON c.code_diag = d.code_diag
        WHERE t.annee BETWEEN 2018 AND 2020
        GROUP BY t.annee, t.trimestre, pat.sexe, d.categorie
        HAVING COUNT(*) > 100
        ORDER BY t.annee, t.trimestre, nb_consultations DESC
        LIMIT 20
        """
        return self.run_query("Q9_Multi_Dimension_Analysis", query)

    def benchmark_q10_hospitalisation_by_diagnostic(self):
        """Q10: Hospitalization analysis by diagnostic category"""
        query = """
        SELECT
            d.categorie,
            COUNT(*) as nb_hospitalisations,
            ROUND(AVG(h.duree_sejour_jours), 2) as duree_moyenne_jours,
            COUNT(DISTINCT h.id_patient) as patients_uniques
        FROM fait_hospitalisation h
        JOIN dim_diagnostic d ON h.code_diag = d.code_diag
        GROUP BY d.categorie
        HAVING COUNT(*) >= 100
        ORDER BY nb_hospitalisations DESC
        LIMIT 10
        """
        return self.run_query("Q10_Hospitalisation_By_Diagnostic", query)

    def run_all_benchmarks(self):
        """Execute all benchmark queries"""
        logger.info("Starting benchmark suite")

        self.results.append(self.benchmark_q1_count_consultations())
        self.results.append(self.benchmark_q2_consultations_by_year())
        self.results.append(self.benchmark_q3_top_diagnostics())
        self.results.append(self.benchmark_q4_consultations_by_specialite())
        self.results.append(self.benchmark_q5_temporal_filter())
        self.results.append(self.benchmark_q6_hospitalisations_stats())
        self.results.append(self.benchmark_q7_deaths_by_age())
        self.results.append(self.benchmark_q8_satisfaction_by_region())
        self.results.append(self.benchmark_q9_consultations_multi_dimensions())
        self.results.append(self.benchmark_q10_hospitalisation_by_diagnostic())

    def export_results(self):
        """Export benchmark results to JSON"""
        output_path = "/home/jovyan/data/benchmark_results.json"

        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        logger.info(f"Results exported to {output_path}")

    def print_summary(self):
        """Print benchmark summary"""
        logger.info("=" * 70)
        logger.info("BENCHMARK RESULTS SUMMARY")
        logger.info("=" * 70)

        for result in self.results:
            logger.info(f"{result['query']:35} | {result['avg_time']:>6.3f}s | {result['result_count']:>8,} rows")

        logger.info("=" * 70)

        total_time = sum(r['avg_time'] for r in self.results)
        avg_time = total_time / len(self.results)

        logger.info(f"Total execution time: {total_time:.3f}s")
        logger.info(f"Average query time: {avg_time:.3f}s")
        logger.info(f"Queries executed: {len(self.results)}")


def create_spark_session():
    """Create Spark session with optimal configuration"""
    return SparkSession.builder \
        .appName("CHU - Performance Benchmarks") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.sql.autoBroadcastJoinThreshold", "10485760") \
        .getOrCreate()


def main():
    """Main execution function"""
    logger.info("Starting Performance Benchmarks")

    spark = create_spark_session()
    logger.info(f"Spark {spark.version} initialized")

    try:
        runner = BenchmarkRunner(spark)

        runner.run_all_benchmarks()
        runner.print_summary()
        runner.export_results()

        logger.info("Benchmarks completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Benchmarks failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    sys.exit(main())
