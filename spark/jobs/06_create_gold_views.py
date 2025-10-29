#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script : 06_create_gold_views.py
Description : Création de vues matérialisées dénormalisées en Gold pour Superset
              avec codes ISO région pour les Country Maps
Auteur : Projet Big Data CHU
Date : 2025-01-28
"""

import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, desc, lit, expr, when, substring
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

GOLD_INPUT = os.getenv("GOLD_INPUT", "/opt/spark-data/gold")
GOLD_OUTPUT = os.getenv("GOLD_OUTPUT", "/opt/spark-data/gold")
DPT_ISO_CSV = os.getenv("DPT_ISO_CSV", "/opt/spark-data/sources/dpt_fr_iso.csv")

JDBC_URL = "jdbc:postgresql://chu_postgres:5432/healthcare_data"
JDBC_PROPS = {
    "user": "admin",
    "password": "admin123",
    "driver": "org.postgresql.Driver"
}


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def add_region_iso_code(df, region_col_name="region_nom_iso"):
    """
    Ajoute une colonne region_iso avec mapping manuel pour éviter problèmes d'encodage.
    Gère toutes les variations de noms de régions.
    """
    from pyspark.sql.functions import when, col, lit

    # Mapping exhaustif: nom région → code ISO
    region_to_iso = {
        # Variantes avec tirets (dans dpt_iso même s'il y a des problèmes d'encodage)
        "Auvergne-Rhône-Alpes": "FR-ARA",
        "Auvergne-Rhone-Alpes": "FR-ARA",
        "Bourgogne-Franche-Comté": "FR-BFC",
        "Bourgogne-Franche-Comte": "FR-BFC",
        "Hauts-de-France": "FR-HDF",
        "Ile-de-France": "FR-IDF",
        "Nouvelle-Aquitaine": "FR-NAQ",
        "Provence-Alpes-Côte d'Azur": "FR-PAC",
        "Provence-Alpes-Cote d'Azur": "FR-PAC",

        # Variantes sans tirets (dans satisfaction 2020)
        "Auvergne Rhône Alpes": "FR-ARA",
        "Auvergne Rhone Alpes": "FR-ARA",
        "Bourgogne Franche Comté": "FR-BFC",
        "Bourgogne Franche Comte": "FR-BFC",
        "Hauts de France": "FR-HDF",
        "Ile de France": "FR-IDF",
        "Nouvelle Aquitaine": "FR-NAQ",

        # Noms courts/alternatifs
        "PACA": "FR-PAC",
        "Océan Indien": "FR-RE",
        "La Réunion": "FR-RE",
        "La Reunion": "FR-RE",

        # Noms standards
        "Bretagne": "FR-BRE",
        "Centre-Val de Loire": "FR-CVL",
        "Centre Val de Loire": "FR-CVL",
        "Corse": "FR-COR",
        "Grand Est": "FR-GES",
        "Normandie": "FR-NOR",
        "Occitanie": "FR-OCC",
        "Pays de la Loire": "FR-PDL",

        # DOM-TOM
        "Guadeloupe": "FR-GUA",
        "Martinique": "FR-MQ",
        "Guyane": "FR-GF",
        "Mayotte": "FR-YT"
    }

    # Construire l'expression when/otherwise
    iso_expr = None
    for region_name, iso_code in region_to_iso.items():
        if iso_expr is None:
            iso_expr = when(col(region_col_name) == region_name, lit(iso_code))
        else:
            iso_expr = iso_expr.when(col(region_col_name) == region_name, lit(iso_code))

    # Default: NULL si pas de match
    iso_expr = iso_expr.otherwise(lit(None))

    return df.withColumn("region_iso_code", iso_expr)


def create_spark_session():
    """Crée une session Spark configurée pour Delta Lake"""
    return SparkSession.builder \
        .appName("CHU - Gold Views (Delta Lake)") \
        .master("local[*]") \
        .config("spark.driver.memory", "8g") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.jars.packages", "io.delta:delta-core_2.12:2.4.0,org.postgresql:postgresql:42.7.3") \
        .getOrCreate()


def load_gold_table(spark, table_name):
    """Charge une table Gold depuis Delta Lake ou Parquet"""
    gold_path = f"{GOLD_INPUT}/{table_name}"
    try:
        df = spark.read.format("delta").load(gold_path)
        print(f"✅ Loaded {table_name} from Delta Lake: {df.count():,} rows")
    except:
        df = spark.read.parquet(gold_path)
        print(f"⚠️  Loaded {table_name} from Parquet: {df.count():,} rows")
    return df


def save_to_delta_and_postgres(df, table_name, description):
    """Sauvegarde en Delta Lake et exporte vers PostgreSQL"""
    # Delta Lake
    output_path = f"{GOLD_OUTPUT}/{table_name}"
    df.write.format("delta").mode("overwrite").save(output_path)
    print(f"💾 Delta Lake: {output_path}")

    # PostgreSQL
    df.write.jdbc(
        url=JDBC_URL,
        table=f"gold.{table_name}",
        mode="overwrite",
        properties=JDBC_PROPS
    )
    print(f"📤 PostgreSQL: gold.{table_name} ({df.count():,} lignes)")


# ============================================================
# ÉTAPE 1 : CHARGER LA DIMENSION GÉOGRAPHIQUE (codes ISO)
# ============================================================

def load_dpt_iso_dimension(spark):
    """
    Charge le fichier dpt_fr_iso.csv avec les codes ISO région (FR-ARA, FR-IDF, etc.)
    Nécessaire pour les Country Maps dans Superset
    """
    print("\n" + "="*60)
    print("🗺️  CHARGEMENT DIMENSION GÉOGRAPHIQUE (codes ISO)")
    print("="*60)

    dpt_iso = spark.read.csv(
        DPT_ISO_CSV,
        header=True,
        sep=";",
        encoding="UTF-8"
    )

    # Nettoyer les espaces
    for col_name in dpt_iso.columns:
        dpt_iso = dpt_iso.withColumnRenamed(col_name, col_name.strip())
        dpt_iso = dpt_iso.withColumn(col_name.strip(), expr(f"trim(`{col_name.strip()}`)"))

    print(f"✅ Loaded dpt_fr_iso: {dpt_iso.count():,} départements")
    dpt_iso.show(5, truncate=False)

    return dpt_iso


# ============================================================
# ÉTAPE 2 : CRÉER LA TABLE PROFESSIONNEL → ÉTABLISSEMENT
# ============================================================

def create_professionnel_etablissement(spark):
    """
    Crée la table de correspondance Professionnel → Établissement
    Logique: Un professionnel est assigné à l'établissement du département
    où il a le plus de patients
    """
    print("\n" + "="*60)
    print("🏥 CRÉATION PROFESSIONNEL → ÉTABLISSEMENT")
    print("="*60)

    consultations = load_gold_table(spark, "fait_consultation")
    professionnels = load_gold_table(spark, "dim_professionnel")
    patients = load_gold_table(spark, "dim_patient")
    etablissements = load_gold_table(spark, "dim_etablissement")

    # Compter les patients par professionnel par département
    prof_dept = consultations \
        .join(patients, "id_patient") \
        .withColumn("dept_patient", substring(col("code_postal"), 1, 2)) \
        .groupBy("id_prof", "dept_patient") \
        .agg(count("id_patient").alias("nb_patients"))

    # Trouver le département principal de chaque professionnel
    from pyspark.sql.window import Window
    window = Window.partitionBy("id_prof").orderBy(desc("nb_patients"))

    prof_dept_principal = prof_dept \
        .withColumn("rank", expr("row_number() over (partition by id_prof order by nb_patients desc)")) \
        .filter(col("rank") == 1) \
        .drop("rank")

    # Assigner chaque pro au premier établissement de son département
    etabl_dept = etablissements \
        .withColumn("dept_etablissement", substring(col("code_postal"), 1, 2)) \
        .select("finess", "dept_etablissement", "nom", "ville", "libelle_region")

    # Prendre le premier établissement par département (avec row_number)
    window_etabl = Window.partitionBy("dept_etablissement").orderBy("finess")
    etabl_dept_unique = etabl_dept \
        .withColumn("rank", expr("row_number() over (partition by dept_etablissement order by finess)")) \
        .filter(col("rank") == 1) \
        .drop("rank")

    # Jointure finale
    prof_etabl = professionnels \
        .join(prof_dept_principal, "id_prof", "left") \
        .join(
            etabl_dept_unique,
            prof_dept_principal.dept_patient == etabl_dept_unique.dept_etablissement,
            "left"
        ) \
        .select(
            professionnels.id_prof,
            professionnels.nom_specialite,
            professionnels.code_specialite,
            col("dept_patient").alias("departement_principal"),
            col("nb_patients").alias("nb_patients_suivis"),
            col("finess").alias("finess_etablissement"),
            col("nom").alias("etablissement_nom"),
            col("ville").alias("etablissement_ville"),
            col("libelle_region").alias("etablissement_region")
        )

    # Remplir les valeurs nulles (pros sans patients encore)
    prof_etabl = prof_etabl.fillna({
        "departement_principal": "75",  # Paris par défaut
        "nb_patients_suivis": 0,
        "finess_etablissement": "750000000"  # Finess par défaut
    })

    nb_rows = prof_etabl.count()
    print(f"✅ Table créée : {nb_rows:,} professionnels assignés à des établissements")

    save_to_delta_and_postgres(prof_etabl, "professionnel_etablissement", "Correspondance Pro→Établissement")

    return prof_etabl


# ============================================================
# ÉTAPE 3 : VUE 1 - CONSULTATIONS ENRICHIE
# ============================================================

def create_vue_consultations_enrichie(spark, prof_etabl, dpt_iso):
    """
    Vue consultations avec patient, diagnostic, professionnel, établissement, temps, région ISO
    Répond aux besoins 1, 2, 6 du cahier des charges
    """
    print("\n" + "="*60)
    print("📊 VUE 1: CONSULTATIONS ENRICHIE")
    print("="*60)

    consultations = load_gold_table(spark, "fait_consultation")
    patients = load_gold_table(spark, "dim_patient")
    diagnostics = load_gold_table(spark, "dim_diagnostic")
    professionnels = load_gold_table(spark, "dim_professionnel")
    etablissements = load_gold_table(spark, "dim_etablissement")
    temps = load_gold_table(spark, "dim_temps")

    # Préparation dpt_iso pour jointure sur département établissement
    # Normalisation : "1" -> "01" pour matcher les codes postaux
    from pyspark.sql.functions import lpad, trim

    dpt_iso_clean = dpt_iso.select(
        lpad(trim(col("num_departement")), 2, "0").alias("dept_num"),
        col("libelle_departement").alias("dept_libelle"),
        col("libelle_region").alias("region_nom_iso")
    ).dropDuplicates(["dept_num"])

    vue = consultations \
        .join(patients, "id_patient", "left") \
        .join(diagnostics, consultations.code_diag == diagnostics.code_diag, "left") \
        .join(professionnels, "id_prof", "left") \
        .join(prof_etabl, professionnels.id_prof == prof_etabl.id_prof, "left") \
        .join(etablissements, prof_etabl.finess_etablissement == etablissements.finess, "left") \
        .join(temps, consultations.id_temps == temps.id_temps, "left") \
        .withColumn("dept_etablissement", substring(etablissements.code_postal, 1, 2)) \
        .join(
            dpt_iso_clean,
            col("dept_etablissement") == dpt_iso_clean.dept_num,
            "left"
        )

    # Ajouter les codes ISO avec le mapping manuel
    vue = add_region_iso_code(vue, "region_nom_iso")

    vue = vue.select(
        # Consultation
        consultations.id_consultation,
        consultations.date_consultation,
        consultations.annee.alias("annee_consultation"),
        consultations.mois.alias("mois_consultation"),
        consultations.motif,

        # Patient (anonymisé)
        patients.id_patient,
        patients.sexe.alias("patient_sexe"),
        patients.age.alias("patient_age"),
        patients.groupe_sanguin.alias("patient_groupe_sanguin"),
        patients.ville.alias("patient_ville"),
        patients.code_postal.alias("patient_code_postal"),

        # Diagnostic
        diagnostics.code_diag,
        diagnostics.libelle.alias("diagnostic_libelle"),
        diagnostics.categorie.alias("diagnostic_categorie"),

        # Professionnel
        professionnels.id_prof,
        professionnels.nom.alias("professionnel_nom"),
        professionnels.prenom.alias("professionnel_prenom"),
        professionnels.nom_specialite,
        professionnels.code_specialite,

        # Établissement
        etablissements.finess,
        etablissements.nom.alias("etablissement_nom"),
        etablissements.ville.alias("etablissement_ville"),
        etablissements.code_postal.alias("etablissement_code_postal"),
        etablissements.libelle_region.alias("etablissement_region"),

        # Région ISO (pour Country Maps Superset)
        col("region_iso_code").alias("etablissement_region_iso"),  # FR-ARA, FR-IDF, etc.
        col("region_nom_iso").alias("etablissement_region_nom_iso"),

        # Temps
        temps.trimestre,
        temps.jour_semaine,
        temps.nom_mois,
        temps.est_weekend
    )

    nb_rows = vue.count()
    print(f"✅ Vue créée : {nb_rows:,} consultations enrichies")

    save_to_delta_and_postgres(vue, "vue_consultations_enrichie", "Consultations enrichies pour Superset")

    return vue


# ============================================================
# ÉTAPE 4 : VUE 2 - HOSPITALISATIONS ENRICHIE
# ============================================================

def create_vue_hospitalisations_enrichie(spark, dpt_iso):
    """
    Vue hospitalisations avec patient, diagnostic, temps, région patient ISO
    Répond aux besoins 3, 4, 5 du cahier des charges
    """
    print("\n" + "="*60)
    print("🏥 VUE 2: HOSPITALISATIONS ENRICHIE")
    print("="*60)

    hospitalisations = load_gold_table(spark, "fait_hospitalisation")
    patients = load_gold_table(spark, "dim_patient")
    diagnostics = load_gold_table(spark, "dim_diagnostic")
    temps = load_gold_table(spark, "dim_temps")

    # Préparation dpt_iso pour jointure sur département patient
    # Normalisation : "1" -> "01" pour matcher les codes postaux
    from pyspark.sql.functions import lpad, trim

    dpt_iso_clean = dpt_iso.select(
        lpad(trim(col("num_departement")), 2, "0").alias("dept_num"),
        col("libelle_region").alias("region_nom_iso")
    ).dropDuplicates(["dept_num"])

    vue = hospitalisations \
        .join(patients, "id_patient", "left") \
        .join(diagnostics, hospitalisations.code_diag == diagnostics.code_diag, "left") \
        .join(temps, hospitalisations.id_temps_entree == temps.id_temps, "left") \
        .withColumn("dept_patient", substring(patients.code_postal, 1, 2)) \
        .join(
            dpt_iso_clean,
            col("dept_patient") == dpt_iso_clean.dept_num,
            "left"
        )

    # Ajouter les codes ISO avec le mapping manuel
    vue = add_region_iso_code(vue, "region_nom_iso")

    vue = vue.select(
        # Hospitalisation
        hospitalisations.id_hospitalisation,
        hospitalisations.date_entree,
        hospitalisations.date_sortie,
        hospitalisations.duree_sejour_jours,
        hospitalisations.nb_consultations.alias("nb_consultations_pendant_hospi"),
        hospitalisations.annee.alias("annee_hospitalisation"),
        hospitalisations.mois.alias("mois_hospitalisation"),

        # Patient (anonymisé)
        patients.id_patient,
        patients.sexe.alias("patient_sexe"),
        patients.age.alias("patient_age"),
        patients.groupe_sanguin.alias("patient_groupe_sanguin"),
        patients.ville.alias("patient_ville"),
        patients.code_postal.alias("patient_code_postal"),

        # Région patient ISO (pour analyses géographiques)
        col("region_iso_code").alias("patient_region_iso"),  # FR-ARA, FR-IDF, etc.
        col("region_nom_iso").alias("patient_region_nom"),

        # Diagnostic
        diagnostics.code_diag,
        diagnostics.libelle.alias("diagnostic_libelle"),
        diagnostics.categorie.alias("diagnostic_categorie"),

        # Temps (entrée)
        temps.trimestre.alias("trimestre_entree"),
        temps.jour_semaine.alias("jour_semaine_entree"),
        temps.nom_mois.alias("mois_nom_entree"),
        temps.est_weekend.alias("entree_weekend")
    )

    nb_rows = vue.count()
    print(f"✅ Vue créée : {nb_rows:,} hospitalisations enrichies")

    save_to_delta_and_postgres(vue, "vue_hospitalisations_enrichie", "Hospitalisations enrichies pour Superset")

    return vue


# ============================================================
# ÉTAPE 5 : VUE 3 - SATISFACTION ENRICHIE
# ============================================================

def create_vue_satisfaction_enrichie(spark, dpt_iso):
    """
    Vue satisfaction avec codes ISO région pour Country Maps
    Répond au besoin 8 du cahier des charges

    NOTE: Les FINESS satisfaction ne sont PAS dans dim_etablissement.
    Utilise directement les colonnes region et raison_sociale_finess de fait_satisfaction.
    """
    print("\n" + "="*60)
    print("⭐ VUE 3: SATISFACTION ENRICHIE")
    print("="*60)

    satisfaction = load_gold_table(spark, "fait_satisfaction")

    # MAPPING MANUEL pour gérer les variations de noms de régions
    # Satisfaction 2020 -> Code ISO
    from pyspark.sql.functions import when

    region_to_iso_map = {
        "Auvergne-Rhône-Alpes": "FR-ARA",
        "Bourgogne-Franche-Comté": "FR-BFC",
        "Bretagne": "FR-BRE",
        "Centre-Val de Loire": "FR-CVL",
        "Corse": "FR-COR",
        "Grand Est": "FR-GES",
        "Guadeloupe": "FR-GUA",
        "Guyane": "FR-GF",
        "Hauts de France": "FR-HDF",
        "Ile de France": "FR-IDF",
        "Martinique": "FR-MQ",
        "Normandie": "FR-NOR",
        "Nouvelle Aquitaine": "FR-NAQ",
        "Occitanie": "FR-OCC",
        "Océan Indien": "FR-RE",  # La Réunion
        "PACA": "FR-PAC",
        "Pays de la Loire": "FR-PDL"
    }

    # Créer une colonne region_iso avec le mapping
    region_iso_expr = None
    for region_name, iso_code in region_to_iso_map.items():
        if region_iso_expr is None:
            region_iso_expr = when(col("region") == region_name, lit(iso_code))
        else:
            region_iso_expr = region_iso_expr.when(col("region") == region_name, lit(iso_code))

    satisfaction_with_iso = satisfaction.withColumn("region_iso", region_iso_expr)

    # Plus besoin de jointure avec dpt_iso!
    vue = satisfaction_with_iso.select(
        # Satisfaction
        col("id_satisfaction"),
        col("annee").alias("annee_satisfaction"),
        col("type_enquete"),
        col("score_global"),
        col("taux_recommandation"),

        # Établissement (depuis satisfaction directement)
        col("finess"),
        col("finess_geo"),
        col("etablissement_nom"),
        col("region").alias("etablissement_region"),

        # Codes ISO région pour Country Maps Superset (mappé directement)
        col("region_iso"),  # FR-ARA, FR-IDF, etc.
        col("region").alias("region_nom")
    )

    nb_rows = vue.count()
    print(f"✅ Vue créée : {nb_rows:,} évaluations de satisfaction enrichies")

    save_to_delta_and_postgres(vue, "vue_satisfaction_enrichie", "Satisfaction enrichie pour Superset")

    return vue


# ============================================================
# ÉTAPE 6 : VUE 4 - DÉCÈS ENRICHIE
# ============================================================

def create_vue_deces_enrichie(spark, dpt_iso):
    """
    Vue décès avec temps et codes ISO région pour Country Maps
    Répond au besoin 7 du cahier des charges
    """
    print("\n" + "="*60)
    print("💀 VUE 4: DÉCÈS ENRICHIE")
    print("="*60)

    deces = load_gold_table(spark, "fait_deces")
    temps = load_gold_table(spark, "dim_temps")

    # Préparation dpt_iso avec normalisation des numéros de département
    # Le CSV a "1", "2", etc. mais substring donne "01", "02", etc.
    from pyspark.sql.functions import lpad, trim

    dpt_iso_clean = dpt_iso.select(
        lpad(trim(col("num_departement")), 2, "0").alias("dept_num"),  # "1" -> "01"
        col("libelle_region").alias("region_nom_iso")
    ).dropDuplicates(["dept_num"])

    vue = deces \
        .join(temps, deces.id_temps == temps.id_temps, "left") \
        .withColumn("dept_deces", substring(col("code_lieu_deces"), 1, 2)) \
        .join(
            dpt_iso_clean,
            col("dept_deces") == dpt_iso_clean.dept_num,
            "left"
        )

    # Ajouter les codes ISO avec le mapping manuel
    vue = add_region_iso_code(vue, "region_nom_iso")

    vue = vue.select(
        # Décès
        deces.id_deces,
        deces.date_deces,
        deces.age_deces,
        deces.annee.alias("annee_deces"),
        deces.mois.alias("mois_deces"),

        # Sexe avec libellé
        deces.sexe.alias("sexe_code"),
        when(col("sexe") == 1, "Homme")
            .when(col("sexe") == 2, "Femme")
            .otherwise("Non renseigné").alias("sexe_libelle"),

        # Localisation
        deces.lieu_naissance,
        deces.code_lieu_naissance,
        deces.pays_naissance,
        deces.code_lieu_deces,

        # Région ISO pour Country Maps
        col("region_iso_code").alias("region_deces_iso"),  # FR-ARA, FR-IDF, etc.
        col("region_nom_iso").alias("region_deces_nom"),

        # Temps
        temps.trimestre.alias("trimestre_deces"),
        temps.jour_semaine.alias("jour_semaine_deces"),
        temps.nom_mois.alias("mois_nom_deces"),
        temps.est_weekend.alias("deces_weekend")
    )

    nb_rows = vue.count()
    print(f"✅ Vue créée : {nb_rows:,} décès enrichis")

    save_to_delta_and_postgres(vue, "vue_deces_enrichie", "Décès enrichis pour Superset")

    return vue


# ============================================================
# FONCTION PRINCIPALE
# ============================================================

def main():
    """Fonction principale"""
    print("\n" + "🎯"*30)
    print("CHU - CRÉATION DES VUES MATÉRIALISÉES GOLD")
    print("Pour optimiser les requêtes Superset avec codes ISO région")
    print("🎯"*30 + "\n")

    start_time = datetime.now()

    # Créer Spark session
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    try:
        # Étape 1 : Charger dimension géographique ISO
        dpt_iso = load_dpt_iso_dimension(spark)

        # Étape 2 : Créer table Professionnel → Établissement
        prof_etabl = create_professionnel_etablissement(spark)

        # Étape 3-6 : Créer les 4 vues enrichies
        vue1 = create_vue_consultations_enrichie(spark, prof_etabl, dpt_iso)
        vue2 = create_vue_hospitalisations_enrichie(spark, dpt_iso)
        vue3 = create_vue_satisfaction_enrichie(spark, dpt_iso)
        vue4 = create_vue_deces_enrichie(spark, dpt_iso)

        # Résumé
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DES VUES CRÉÉES")
        print("="*60)
        print(f"✅ professionnel_etablissement       : {prof_etabl.count():,} lignes")
        print(f"✅ vue_consultations_enrichie        : {vue1.count():,} lignes")
        print(f"✅ vue_hospitalisations_enrichie     : {vue2.count():,} lignes")
        print(f"✅ vue_satisfaction_enrichie         : {vue3.count():,} lignes")
        print(f"✅ vue_deces_enrichie                : {vue4.count():,} lignes")
        print("="*60)

        # Temps d'exécution
        duration = datetime.now() - start_time
        print(f"\n✅ SUCCÈS ! Durée totale : {duration}")

        print("\n💡 PROCHAINES ÉTAPES SUPERSET :")
        print("   1. Ouvre SQL Lab dans Superset")
        print("   2. Utilise ces vues simplifiées :")
        print("      SELECT * FROM gold.vue_consultations_enrichie WHERE annee_consultation = 2020")
        print("      SELECT * FROM gold.vue_hospitalisations_enrichie")
        print("      SELECT * FROM gold.vue_satisfaction_enrichie WHERE annee_satisfaction = 2020")
        print("      SELECT * FROM gold.vue_deces_enrichie WHERE annee_deces = 2019")
        print("   3. Pour les Country Maps, utilise les colonnes *_iso (ex: region_iso)")
        print("      Format ISO 3166-2 : FR-ARA, FR-IDF, FR-PAC, etc.")

    except Exception as e:
        print(f"\n❌ ERREUR : {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
