# 🎯 PIPELINE ETL FINAL - Architecture Correcte

**Auteurs** : Nejma MOUALHI | Brieuc OLIVIERI | Nicolas TAING
**Date** : 21 Octobre 2025
**Livrable** : 2 & 3

---

## ✅ FLUX ETL CORRECT (Bronze → Silver → Gold)

```
📁 SOURCES BRUTES
├── PostgreSQL (100K patients, 1M+ consultations)
└── CSV dans /DATA_2024/ (décès, satisfaction, établissements)
         ↓
    EXTRACT (Notebook 01)
    • Lit directement les CSV bruts (PAS PostgreSQL!)
    • Lit les tables PostgreSQL originales
         ↓
📦 BRONZE LAYER (MinIO/data/bronze/)
├── bronze/postgres/ - Tables PostgreSQL en Parquet
└── bronze/csv/ - CSV convertis en Parquet
    Format: Copie exacte des sources
         ↓
    TRANSFORM 1 (Notebook 02) - NETTOYAGE
    • Anonymisation (SHA-256 des noms/prénoms)
    • Formats dates uniformes (yyyy-MM-dd)
    • Typage correct (integer, double, date)
    • Dédoublonnage
    • Validation données
         ↓
📦 SILVER LAYER (MinIO/data/silver/)
├── Données nettoyées et validées
├── Conformes RGPD (anonymisées)
└── Prêtes pour l'analyse
         ↓
    TRANSFORM 2 (Notebook 03) - MODÈLE MÉTIER
    • Création dimensions (Patient, Temps, Diagnostic...)
    • Création faits (Consultations, Décès, Satisfaction)
    • Partitionnement (année/mois)
    • Optimisations Spark
         ↓
⭐ GOLD LAYER (MinIO/data/gold/)
├── Star Schema optimisé
├── dim_temps, dim_patient, dim_diagnostic, dim_professionnel, dim_etablissement
├── fait_consultation (partitionné année/mois)
├── fait_deces (partitionné année/mois)
└── fait_satisfaction (partitionné année)
         ↓
📊 ANALYSE & VISUALISATION
├── Notebook 04: Benchmarks + Graphiques de performance
├── Jupyter: Requêtes SQL + Analyses exploratoires
├── Superset: Dashboards BI (Livrable 3)
└── Airflow: Automatisation (Livrable 3)
```

---

## 📓 NOTEBOOKS - Pipeline Complet

### ✅ Notebook 01 : Extract Bronze (Sources Directes)

**Fichier** : `01_Extract_Bronze_SOURCES_DIRECTES.ipynb`

**Ce qu'il fait** :
```python
# 1. EXTRACT depuis PostgreSQL (tables originales)
df_patient = spark.read.jdbc("postgresql://...", "Patient")
df_consultation = spark.read.jdbc("postgresql://...", "Consultation")
# ... 13 tables

# 2. EXTRACT depuis CSV BRUTS (directement!)
df_etab = spark.read.csv("/home/jovyan/DATA_2024/Etablissement de SANTE/etablissement_sante.csv")
df_satis = spark.read.csv("/home/jovyan/DATA_2024/Satisfaction/2019/...")
df_deces = spark.read.csv("/home/jovyan/DATA_2024/DECES EN FRANCE/deces.csv")
           .filter(year(col("date_deces")) == 2019)  # Filtrage intelligent

# 3. SAVE en BRONZE (données brutes)
df_patient.write.parquet("/home/jovyan/data/bronze/postgres/Patient")
df_etab.write.parquet("/home/jovyan/data/bronze/csv/etablissement_sante")
```

**Résultat** :
- ✅ 13 tables PostgreSQL en Bronze
- ✅ 3 fichiers CSV en Bronze (416K établissements, 1K satisfaction, 620K décès 2019)
- ✅ ~4.6 millions de lignes au total

---

### ✅ Notebook 02 : Transform Silver (Nettoyage)

**Fichier** : `02_Transform_Silver_NETTOYAGE.ipynb`

**Ce qu'il fait** :
```python
# 1. Lire depuis BRONZE
df_patient_bronze = spark.read.parquet("/home/jovyan/data/bronze/postgres/Patient")

# 2. ANONYMISATION (RGPD)
df_patient_clean = df_patient_bronze.select(
    col("Id_patient").alias("id_patient"),
    sha2(col("Nom"), 256).alias("nom_hash"),        # Hash SHA-256
    sha2(col("Prenom"), 256).alias("prenom_hash"),  # Anonymisation
    col("Sexe").alias("sexe"),
    col("Age").cast("integer").alias("age"),
    to_date(col("Date"), "M/d/yyyy").alias("date_naissance"),  # Format uniforme
    trim(upper(col("Ville"))).alias("ville"),       # Normalisation
    # ...
)

# 3. Sauvegarder en SILVER
df_patient_clean.write.parquet("/home/jovyan/data/silver/patient")
```

**Transformations appliquées** :
- 🔐 **Anonymisation** : Hash SHA-256 des noms, prénoms, téléphones, emails, numéros sécu
- 📅 **Dates uniformes** : M/d/yyyy → yyyy-MM-dd (format ISO)
- 🔢 **Typage correct** : Conversion string → integer/double/date
- 🧹 **Nettoyage texte** : trim(), upper() pour normalisation
- ✅ **Validation** : Filtres sur âges, dates, identifiants
- 🔄 **Dédoublonnage** : dropDuplicates() sur clés primaires

**Tables traitées** :
- ✅ Patient (anonymisé)
- ✅ Consultation (dates formatées)
- ✅ Établissements (nettoyé)
- ✅ Satisfaction (scores typés)
- ✅ Décès (anonymisé)
- ✅ 7 tables de référence (nettoyées)

---

### ✅ Notebook 03 : Transform Gold (Star Schema)

**Fichier** : `03_Transform_Gold_STAR_SCHEMA.ipynb`

**Ce qu'il fait** :
```python
# 1. Lire depuis SILVER (pas Bronze!)
df_patient_silver = spark.read.parquet("/home/jovyan/data/silver/patient")
df_consult_silver = spark.read.parquet("/home/jovyan/data/silver/consultation")

# 2. Créer DIMENSIONS
dim_patient = df_patient_silver.select(
    col("id_patient"),
    col("nom_hash"),      # Déjà anonymisé en Silver
    col("sexe"),
    col("age"),
    col("ville")
)

# 3. Créer FAITS avec PARTITIONNEMENT
fait_consultation = df_consult_silver.select(
    col("id_consultation"),
    col("id_patient"),
    col("id_professionnel"),
    date_format(col("date_consultation"), "yyyyMMdd").alias("id_temps"),
    col("annee"),  # Pour partitionnement
    col("mois"),
    col("duree_minutes")
)

# 4. Sauvegarder avec OPTIMISATIONS
fait_consultation.write \
    .partitionBy("annee", "mois") \
    .parquet("/home/jovyan/data/gold/fait_consultation")
```

**Modèle créé** :

**Dimensions (5)** :
- ✅ `dim_temps` : 4,748 jours (2013-2025)
- ✅ `dim_patient` : 100K patients anonymisés
- ✅ `dim_diagnostic` : ~15K codes diagnostics
- ✅ `dim_professionnel` : 1M+ professionnels + spécialités
- ✅ `dim_etablissement` : 416K établissements

**Faits (3)** :
- ✅ `fait_consultation` : 1M+ consultations (partitionné année/mois)
- ✅ `fait_deces` : 620K décès 2019 (partitionné année/mois)
- ✅ `fait_satisfaction` : 1,152 évaluations 2019 (partitionné année)

---

### ✅ Notebook 04 : Benchmarks (Déjà existant)

**Fichier** : `04_Performance_Benchmarks.ipynb`

**Ce qu'il fait** :
- Lit depuis Gold
- Mesure performance des requêtes SQL
- Génère graphiques de performance
- Crée rapport markdown

**Pas de modification nécessaire** - Lit déjà depuis Gold.

---

## 🔄 DIFFÉRENCES AVEC L'ANCIENNE APPROCHE

### ❌ ANCIENNE APPROCHE (Incorrecte)

```
CSV → PostgreSQL → Bronze → Gold
```

**Problèmes** :
- CSV d'abord chargés dans PostgreSQL (étape inutile)
- Pas de layer Silver (pas de nettoyage/anonymisation)
- Lecture depuis PostgreSQL alors que sources = CSV

### ✅ NOUVELLE APPROCHE (Correcte)

```
CSV (brut) → Bronze → Silver (nettoyé) → Gold (métier)
PostgreSQL → Bronze → Silver → Gold
```

**Avantages** :
- CSV lus **directement** (pas via PostgreSQL)
- Layer Silver = Nettoyage + Anonymisation + Validation
- Séparation claire des responsabilités (Bronze/Silver/Gold)
- Conforme architecture Medallion (best practice)
- Conforme RGPD (anonymisation en Silver)

---

## 📋 CHECKLIST EXÉCUTION

### Pour Livrable 2 :

1. **Lancer Docker** :
   ```bash
   docker compose up -d
   ```

2. **Accéder à Jupyter** :
   - URL : http://localhost:8888
   - Token : `chu_token`

3. **Exécuter les notebooks dans l'ordre** :
   ```
   ✅ 01_Extract_Bronze_SOURCES_DIRECTES.ipynb
   ✅ 02_Transform_Silver_NETTOYAGE.ipynb
   ✅ 03_Transform_Gold_STAR_SCHEMA.ipynb
   ✅ 04_Performance_Benchmarks.ipynb
   ```

4. **Vérifier MinIO** :
   - URL : http://localhost:9001
   - Login : `minioadmin` / `minioadmin`
   - Vérifier buckets :
     - `lakehouse/bronze/` → Données brutes
     - `lakehouse/silver/` → Données nettoyées
     - `lakehouse/gold/` → Star Schema

5. **Livrables générés** :
   - ✅ 4 notebooks exécutés avec résultats
   - ✅ Graphiques de performance
   - ✅ Rapport markdown (généré par Notebook 04)
   - ✅ Données Bronze/Silver/Gold dans MinIO

---

## 🚀 LIVRABLE 3 (Suite)

### À faire ensuite :

#### 1. Pipelines Airflow

**Fichier** : `airflow/dags/chu_etl_pipeline.py`

```python
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

dag = DAG('chu_etl_daily', schedule_interval='@daily')

bronze_task = SparkSubmitOperator(
    task_id='extract_bronze',
    application='/opt/spark-apps/bronze_extract.py',
    dag=dag
)

silver_task = SparkSubmitOperator(
    task_id='transform_silver',
    application='/opt/spark-apps/silver_clean.py',
    dag=dag
)

gold_task = SparkSubmitOperator(
    task_id='transform_gold',
    application='/opt/spark-apps/gold_star_schema.py',
    dag=dag
)

bronze_task >> silver_task >> gold_task
```

#### 2. Dashboards Superset

- Connecter Superset à Gold layer (via Spark SQL ou PostgreSQL)
- Créer graphiques :
  - Consultations par mois
  - Top 10 diagnostics
  - Répartition décès par localisation
  - Scores satisfaction par région
- Assembler en dashboard avec storytelling

#### 3. Présentation

- Montrer pipeline Airflow en exécution
- Dashboard Superset en live
- Notebooks Jupyter pour analyses

---

## 📊 VOLUMÉTRIES

| Layer | Tables | Lignes Total | Format | Optimisations |
|-------|--------|--------------|--------|---------------|
| **Bronze** | 16 | ~4.6M | Parquet | Copie brute sources |
| **Silver** | 12 | ~4.6M | Parquet | Anonymisé, typé, nettoyé |
| **Gold** | 8 | ~1.7M | Parquet | Partitionné année/mois, Star Schema |

---

## 🎓 POURQUOI CETTE ARCHITECTURE ?

### Bronze / Silver / Gold (Medallion)

- **Bronze** : Zone de quarantaine - Données brutes au cas où
- **Silver** : Zone de confiance - Données validées RGPD
- **Gold** : Zone business - Modèle optimisé pour décideurs

### Pourquoi pas tout dans PostgreSQL ?

- **PostgreSQL** = OLTP (transactions rapides, petites requêtes)
- **MinIO + Parquet** = OLAP (analyses sur millions de lignes)
- **Parquet** = 10x plus compact que CSV
- **Spark** lit Parquet 100x plus vite que CSV

### Pourquoi Jupyter ET Airflow ?

- **Jupyter** : Développement, tests, prototypage (Livrable 2)
- **Airflow** : Production, automatisation, monitoring (Livrable 3)

Comme Word vs InDesign :
- Jupyter = Word (brouillon, essais)
- Airflow = InDesign (version finale, automatique)

---

## ✅ RÉSUMÉ

**Pipeline correct** :
1. ✅ Extract depuis sources brutes (CSV + PostgreSQL) → Bronze
2. ✅ Transform avec anonymisation/nettoyage → Silver
3. ✅ Transform avec modèle métier Star Schema → Gold
4. ✅ Analyse avec Jupyter + Benchmarks

**Livrables Livrable 2** :
- ✅ Scripts (4 notebooks)
- ✅ Vérifications (counts, aperçus)
- ✅ Partitionnement (année/mois)
- ✅ Graphiques performance
- ✅ Documentation complète

**Prêt pour Livrable 3** :
- DAGs Airflow à créer
- Dashboards Superset à créer
- Présentation à préparer

---

**Architecture validée et conforme aux best practices Big Data !** 🎉
