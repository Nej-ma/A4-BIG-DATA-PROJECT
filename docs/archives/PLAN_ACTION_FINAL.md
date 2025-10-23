# 🎯 PLAN D'ACTION - Livrable 2 & 3

## ✅ ÉTAT ACTUEL (Ce qui fonctionne)

### Infrastructure :
- ✅ PostgreSQL : 100K patients + 1M consultations + CSV (416K établissements, 1K satisfaction)
- ✅ MinIO : Buckets créés (vides pour l'instant - normal!)
- ✅ Spark Master + Worker : Prêts
- ✅ Jupyter : Fonctionnel avec tous les JARs
- ✅ Airflow : **RÉPARÉ** (CSRF désactivé)
- ✅ Superset : Fonctionnel

---

## 🔄 LE BON FLUX ETL (Ce que tu as compris)

```
📁 SOURCES BRUTES
├── PostgreSQL (patients, consultations)
└── CSV dans /data/DATA 2024/ (décès, satisfaction, établissements)
         ↓
    EXTRACT avec Spark
         ↓
📦 BRONZE (MinIO) - Données brutes en Parquet
├── Copie exacte des sources
└── Format: Parquet (compression)
         ↓
    TRANSFORM 1: Nettoyage
    • Anonymisation (supprimer noms/prénoms)
    • Formats dates cohérents
    • Typage correct
    • Dédoublonnage
         ↓
📦 SILVER (MinIO) - Données nettoyées
├── Données validées et propres
└── Prêtes pour l'analyse
         ↓
    TRANSFORM 2: Modèle métier
    • Créer dimensions (Patient, Temps, Diagnostic...)
    • Créer faits (Consultations, Décès...)
    • Partitionnement (année/mois)
    • Bucketing (optimisation)
         ↓
⭐ GOLD (MinIO) - Star Schema
├── dim_temps, dim_patient, dim_diagnostic...
├── fait_consultation (partitionné)
└── fait_deces, fait_satisfaction...
         ↓
📊 ANALYSE & VISUALISATION
├── Jupyter: Requêtes SQL + Graphiques
├── Superset: Dashboards BI
└── Airflow: Automatisation
```

---

## 📓 NOTEBOOKS À CRÉER/MODIFIER

### Notebook 01 : EXTRACT + BRONZE ✅ (À modifier)

**Ce qu'il doit faire** :
```python
# 1. Lire CSV BRUTS depuis /DATA_2024/
df_deces = spark.read.csv("/home/jovyan/DATA_2024/DECES EN FRANCE/deces.csv")
df_etab = spark.read.csv("/home/jovyan/DATA_2024/Etablissement.../etablissement_sante.csv")
df_satis = spark.read.csv("/home/jovyan/DATA_2024/Satisfaction/.../...")

# 2. Lire PostgreSQL
df_patient = spark.read.jdbc("postgresql://...", "Patient")
df_consult = spark.read.jdbc("postgresql://...", "Consultation")

# 3. Sauvegarder EN BRONZE (données brutes)
df_deces.write.parquet("s3a://lakehouse/bronze/csv/deces")
df_patient.write.parquet("s3a://lakehouse/bronze/postgres/patient")
```

**Résultat** : MinIO/lakehouse/bronze/ sera REMPLI

---

### Notebook 02 : SILVER (Nettoyage) - NOUVEAU

**Ce qu'il doit faire** :
```python
# 1. Lire depuis BRONZE
df_patient_bronze = spark.read.parquet("s3a://lakehouse/bronze/postgres/Patient")

# 2. ANONYMISER
df_patient_clean = df_patient_bronze.select(
    col("Id_patient"),
    # ANONYMISATION: On supprime nom/prénom ou on hash
    sha2(col("Nom"), 256).alias("nom_hash"),
    col("Sexe"),
    col("Age"),
    to_date(col("Date"), "M/d/yyyy").alias("date_naissance"),  # FORMAT DATE
    col("Ville"),
    col("Code_postal")
)

# 3. Sauvegarder en SILVER
df_patient_clean.write.parquet("s3a://lakehouse/silver/patient")
```

**Résultat** : MinIO/lakehouse/silver/ avec données propres

---

### Notebook 03 : GOLD (Star Schema) ⭐ (Déjà créé, à adapter)

**Ce qu'il doit faire** :
```python
# 1. Lire depuis SILVER (pas Bronze!)
df_patient = spark.read.parquet("s3a://lakehouse/silver/patient")
df_consult = spark.read.parquet("s3a://lakehouse/silver/consultation")

# 2. Créer dimensions
dim_patient = df_patient.select("id_patient", "sexe", "age", "ville")

# 3. Créer faits avec PARTITIONNEMENT
fait_consultation = df_consult \
    .withColumn("annee", year(col("date"))) \
    .withColumn("mois", month(col("date")))

# 4. Sauvegarder avec OPTIMISATIONS
fait_consultation.write \
    .partitionBy("annee", "mois") \  # PARTITION
    .parquet("s3a://lakehouse/gold/fait_consultation")
```

**Résultat** : MinIO/lakehouse/gold/ avec Star Schema

---

### Notebook 04 : BENCHMARKS (Déjà créé) ✅

Pas de changement, il lit depuis Gold et mesure les performances.

---

## 🎯 LIVRABLE 2 - Ce qu'il faut livrer

### 1. Scripts (= Notebooks)
- ✅ Notebook 01: Extract + Bronze
- 🆕 Notebook 02: Transform Silver (anonymisation, formats)
- ✅ Notebook 03: Transform Gold (Star Schema + partitionnement)
- ✅ Notebook 04: Benchmarks

### 2. Vérifications
Chaque notebook affiche :
- Nombre de lignes lues
- Nombre de lignes écrites
- Aperçu des données

### 3. Partitionnement
- `fait_consultation` partitionné par année/mois
- Démontré dans Notebook 03

### 4. Graphiques de performance
- Générés par Notebook 04
- Temps d'exécution des requêtes
- Heatmap des partitions

### 5. Rapport
- Markdown généré automatiquement par Notebook 04

---

## 🚀 LIVRABLE 3 - Ce qu'il faudra faire après

### 1. Pipelines Airflow (DAGs)

**Créer un DAG** :
```python
# airflow/dags/chu_etl_pipeline.py
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

dag = DAG('chu_etl_daily', schedule_interval='@daily')

bronze_task = SparkSubmitOperator(
    task_id='extract_bronze',
    application='/opt/spark-apps/bronze/ingest.py',
    dag=dag
)

silver_task = SparkSubmitOperator(
    task_id='transform_silver',
    application='/opt/spark-apps/silver/clean.py',
    dag=dag
)

gold_task = SparkSubmitOperator(
    task_id='transform_gold',
    application='/opt/spark-apps/gold/star_schema.py',
    dag=dag
)

bronze_task >> silver_task >> gold_task  # Ordre d'exécution
```

### 2. Dashboards Superset

- Se connecter à PostgreSQL OU Spark SQL
- Créer des graphiques (consultations par mois, top diagnostics, etc.)
- Assembler en dashboard
- **Storytelling** : Raconter une histoire avec les données

### 3. Présentation

- Montrer le pipeline Airflow en action
- Dashboard Superset en live
- Notebooks Jupyter pour analyses exploratoires

---

## ✅ ACTIONS IMMÉDIATES (Pour finir L2)

### Action 1 : Modifier Notebook 01

Faire qu'il lise les **CSV bruts** (pas PostgreSQL pour les CSV) :

```python
# Au lieu de :
df_etab = spark.read.jdbc(..., "Etablissement_sante")

# Faire :
df_etab = spark.read.csv("/home/jovyan/DATA_2024/Etablissement de SANTE/etablissement_sante.csv", sep=";")
```

### Action 2 : Créer Notebook 02 (Silver)

Avec anonymisation + formats dates

### Action 3 : Adapter Notebook 03

Qu'il lise depuis Silver (pas Bronze)

### Action 4 : Exécuter tout

01 → 02 → 03 → 04

---

## 🎓 POURQUOI CETTE ARCHITECTURE ?

### Pourquoi Bronze/Silver/Gold ?

- **Bronze** : "Zone de quarantaine" - données brutes, au cas où
- **Silver** : "Zone de confiance" - données validées, prêtes à être utilisées
- **Gold** : "Zone business" - modèle optimisé pour les décideurs

### Pourquoi pas tout mettre dans PostgreSQL ?

- PostgreSQL = OLTP (transactions rapides, petites requêtes)
- MinIO + Parquet = OLAP (analyses sur millions de lignes)
- Parquet = 10x plus compact que CSV
- Spark lit Parquet 100x plus vite que CSV

### Pourquoi Jupyter ET Airflow ?

- **Jupyter** : Développement, tests, prototypage
- **Airflow** : Production, automatisation, monitoring

C'est comme Word vs InDesign :
- Jupyter = Word (brouillon, essais)
- Airflow = InDesign (version finale, automatique)

---

## 🔧 SERVICES - Résumé

| Service | Rôle | Livrable 2 | Livrable 3 |
|---------|------|------------|------------|
| PostgreSQL | Source données | ✅ Essentiel | ✅ Essentiel |
| Spark | Moteur ETL | ✅ Essentiel | ✅ Essentiel |
| MinIO | Stockage Lakehouse | ✅ Essentiel | ✅ Essentiel |
| Jupyter | Développement | ✅ Essentiel | ⚠️ Optionnel |
| Airflow | Orchestration | ❌ Bonus | ✅ Essentiel |
| Superset | Dashboards BI | ❌ Bonus | ✅ Essentiel |

---

**Maintenant Airflow et Superset sont réparés. Prêt pour le L3 !**

**Pour finir le L2 : Exécute les notebooks 01 → 03 → 04 dans Jupyter.**
