"""
Analyse rapide des taux de consultations par professionnels
Script autonome avec DuckDB (sans Spark)
"""

import duckdb
import sys

def main():
    print("="*80)
    print("ANALYSE DES TAUX DE CONSULTATIONS PAR PROFESSIONNELS")
    print("="*80)

    # Connexion DuckDB (en mémoire)
    con = duckdb.connect()

    # Chemins locaux Windows
    data_base = r"c:\Users\littl\Desktop\Big DATA\projet_git\spark\data"
    gold_base = f"{data_base}/gold"

    print(f"\nChargement des données depuis: {gold_base}")

    try:
        # Charger les tables Gold depuis Parquet
        print("- Chargement fait_consultation...")
        con.execute(f"""
            CREATE OR REPLACE TABLE fait_consultation AS
            SELECT * FROM read_parquet('{gold_base}/fait_consultation/**/*.parquet')
        """)

        print("- Chargement dim_professionnel...")
        con.execute(f"""
            CREATE OR REPLACE TABLE dim_professionnel AS
            SELECT * FROM read_parquet('{gold_base}/dim_professionnel/*.parquet')
        """)

        print("- Chargement dim_temps...")
        con.execute(f"""
            CREATE OR REPLACE TABLE dim_temps AS
            SELECT * FROM read_parquet('{gold_base}/dim_temps/*.parquet')
        """)

        print("\nTables chargées avec succès !")

        # Vérifier les comptes
        count_consultations = con.execute("SELECT COUNT(*) FROM fait_consultation").fetchone()[0]
        count_prof = con.execute("SELECT COUNT(*) FROM dim_professionnel").fetchone()[0]
        print(f"\n- Consultations: {count_consultations:,}")
        print(f"- Professionnels: {count_prof:,}")

        # ANALYSE 1: Taux de consultations par spécialité
        print("\n" + "="*80)
        print("ANALYSE 1: TAUX DE CONSULTATIONS PAR SPÉCIALITÉ MÉDICALE")
        print("="*80 + "\n")

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

        result1 = con.execute(query1).fetchdf()
        print(result1.to_string(index=False))

        # ANALYSE 2: Top 20 professionnels individuels
        print("\n" + "="*80)
        print("ANALYSE 2: TOP 20 PROFESSIONNELS PAR NOMBRE DE CONSULTATIONS")
        print("="*80 + "\n")

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

        result2 = con.execute(query2).fetchdf()
        print(result2.to_string(index=False))

        # ANALYSE 3: Consultations moyennes par spécialité
        print("\n" + "="*80)
        print("ANALYSE 3: CONSULTATIONS MOYENNES PAR PROFESSIONNEL ET SPÉCIALITÉ")
        print("="*80 + "\n")

        query3 = """
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

        result3 = con.execute(query3).fetchdf()
        print(result3.to_string(index=False))

        # ANALYSE 4: Statistiques globales
        print("\n" + "="*80)
        print("ANALYSE 4: STATISTIQUES GLOBALES")
        print("="*80 + "\n")

        query4 = """
        SELECT
            COUNT(*) as total_consultations,
            COUNT(DISTINCT id_prof) as total_professionnels,
            COUNT(DISTINCT id_patient) as total_patients,
            ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT id_prof), 2) as consultations_moy_par_prof,
            ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT id_patient), 2) as consultations_moy_par_patient
        FROM fait_consultation
        """

        result4 = con.execute(query4).fetchdf()
        print(result4.to_string(index=False))

        # ANALYSE 5: Répartition annuelle
        print("\n" + "="*80)
        print("ANALYSE 5: RÉPARTITION ANNUELLE DES CONSULTATIONS")
        print("="*80 + "\n")

        query5 = """
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

        result5 = con.execute(query5).fetchdf()
        print(result5.to_string(index=False))

        print("\n" + "="*80)
        print("ANALYSE TERMINÉE AVEC SUCCÈS !")
        print("="*80)

        con.close()
        return 0

    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
