# 🏗️ Architecture Visuelle - Stack Big Data CHU

## Vue d'ensemble simplifiée

```
┌─────────────────────────────────────────────────────────────────┐
│                         🌐 UTILISATEURS                          │
│  Analystes • Data Scientists • Décideurs • Médecins              │
└────────────┬──────────────────────────────┬─────────────────────┘
             │                              │
             ▼                              ▼
    ┌─────────────────┐           ┌─────────────────┐
    │   📊 SUPERSET   │           │  📓 JUPYTER     │
    │   Dashboards    │           │   Notebooks     │
    │   (Power BI)    │           │   Analyse       │
    └────────┬────────┘           └────────┬────────┘
             │                              │
             └──────────────┬───────────────┘
                            ▼
              ┌──────────────────────────┐
              │     🥇 ZONE GOLD         │
              │   Data Warehouse         │
              │  (Modèle dimensionnel)   │
              │                          │
              │  • DIM_TEMPS             │
              │  • DIM_PATIENT           │
              │  • DIM_ETABLISSEMENT     │
              │  • FAIT_CONSULTATION     │
              │  • FAIT_HOSPITALISATION  │
              └──────────┬───────────────┘
                         │
                    T2 Transform
                   (Modèle métier)
                         │
              ┌──────────▼───────────┐
              │   🥈 ZONE SILVER     │
              │  Données nettoyées   │
              │    (Conformes RGPD)  │
              │                      │
              │  • patient_clean     │
              │  • consultation_clean│
              └──────────┬───────────┘
                         │
                   T1 Transform
                  (Conformité)
                         │
              ┌──────────▼───────────┐
              │   🥉 ZONE BRONZE     │
              │   Données brutes     │
              │                      │
              │  • postgresql/       │
              │  • csv/              │
              └──────────┬───────────┘
                         │
                         │  MinIO (S3)
─────────────────────────┼─────────────────────────
                         │
              ┌──────────▼───────────┐
              │    ⚙️ AIRFLOW        │
              │   Orchestration      │
              │                      │
              │  Pipeline ETLT       │
              │  Planification       │
              │  Monitoring          │
              └──┬─────────────────┬─┘
                 │                 │
          Extract│                 │Extract
                 │                 │
    ┌────────────▼─────┐    ┌─────▼──────────┐
    │  🗄️ POSTGRESQL   │    │  📁 CSV Files  │
    │  Base opérationnelle   │  Fichiers plats│
    │                  │    │                │
    │ • patient        │    │ • etablissements│
    │ • consultation   │    │ • satisfaction │
    │ • professionnel  │    │ • deces        │
    │ • diagnostic     │    │ • hospitalisation│
    └──────────────────┘    └────────────────┘
```

---

## Architecture détaillée avec Spark

```
┌───────────────────────────────────────────────────────────────┐
│                    COUCHE VISUALISATION                        │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────┐         ┌──────────────────┐           │
│  │  Apache Superset │         │   Jupyter Lab    │           │
│  │  :8088           │◄────────┤   :8888          │           │
│  │                  │         │                  │           │
│  │  • Dashboards    │         │  • PySpark       │           │
│  │  • Charts        │         │  • Pandas        │           │
│  │  • SQL Lab       │         │  • Visualisation │           │
│  └──────────────────┘         └──────────────────┘           │
│                                                                │
└──────────────┬─────────────────────────────┬──────────────────┘
               │                             │
               │                             │
               │         READ/QUERY          │
               │                             │
┌──────────────▼─────────────────────────────▼──────────────────┐
│                    DATA LAKE (MinIO S3)                        │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    🥇 GOLD ZONE                          │ │
│  │              s3://gold/                                   │ │
│  │                                                           │ │
│  │  dimensions/                  faits/                     │ │
│  │  ├─ dim_temps.parquet         ├─ fait_consultation/     │ │
│  │  ├─ dim_patient.parquet        │  ├─ annee=2019/        │ │
│  │  ├─ dim_etablissement.parquet  │  ├─ annee=2020/        │ │
│  │  ├─ dim_diagnostic.parquet     │  └─ annee=2021/        │ │
│  │  ├─ dim_professionnel.parquet  ├─ fait_hospitalisation/ │ │
│  │  └─ ...                        ├─ fait_deces/           │ │
│  │                                 └─ fait_satisfaction/    │ │
│  │                                                           │ │
│  │  Format: Parquet (compression Snappy)                    │ │
│  │  Partitionnement: Par année, région                      │ │
│  └───────────────────────────▲───────────────────────────────┘ │
│                               │                                │
│                               │ T2 (Spark)                     │
│                               │                                │
│  ┌────────────────────────────┴──────────────────────────────┐ │
│  │                    🥈 SILVER ZONE                         │ │
│  │              s3://silver/                                 │ │
│  │                                                           │ │
│  │  patient/                    consultation/               │ │
│  │  ├─ patient_clean_20250110   ├─ consultation_clean_...  │ │
│  │                                                           │ │
│  │  etablissement/              satisfaction/               │ │
│  │  professionnel/              deces/                      │ │
│  │                                                           │ │
│  │  Format: CSV ou Parquet                                  │ │
│  │  Données: Pseudonymisées, validées, normalisées          │ │
│  └───────────────────────────▲───────────────────────────────┘ │
│                               │                                │
│                               │ T1 (Airflow Python)            │
│                               │                                │
│  ┌────────────────────────────┴──────────────────────────────┐ │
│  │                    🥉 BRONZE ZONE                         │ │
│  │              s3://bronze/                                 │ │
│  │                                                           │ │
│  │  postgresql/                 csv/                        │ │
│  │  ├─ patient/                 ├─ etablissements/          │ │
│  │  ├─ consultation/            ├─ satisfaction/            │ │
│  │  ├─ professionnel/           ├─ deces/                   │ │
│  │  └─ diagnostic/              └─ hospitalisation/         │ │
│  │                                                           │ │
│  │  Format: CSV (tel quel)                                  │ │
│  │  Métadonnées: JSON (source, date, checksum)             │ │
│  └───────────────────────────▲───────────────────────────────┘ │
│                               │                                │
└───────────────────────────────┼────────────────────────────────┘
                                │
                                │ Load (Airflow)
                                │
┌───────────────────────────────┴────────────────────────────────┐
│                    COUCHE ORCHESTRATION                         │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Apache Airflow :8080                        │ │
│  │                                                           │ │
│  │  DAG: chu_etl_pipeline                                   │ │
│  │                                                           │ │
│  │  [Extract PostgreSQL] ──┬──> [T1 Patient] ──> [Dim Patient]│
│  │                         │                                │ │
│  │  [Extract CSV]      ────┴──> [T1 Consult] ──> [Fait Consult]│
│  │                                                           │ │
│  │  Scheduler │ Webserver │ Workers (Celery)                │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Apache Spark :8081                          │ │
│  │                                                           │ │
│  │  Master ──> Worker 1 (2 cores, 2GB RAM)                  │ │
│  │                                                           │ │
│  │  Jobs:                                                    │ │
│  │  • chu_spark_processing.py                               │ │
│  │  • Transformations lourdes                               │ │
│  │  • Agrégations distribuées                               │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
└──────────────┬─────────────────────────────┬──────────────────┘
               │                             │
            Extract                       Extract
               │                             │
┌──────────────▼──────────────┐  ┌──────────▼──────────────────┐
│     SOURCES PostgreSQL       │  │     SOURCES CSV             │
├─────────────────────────────┤  ├─────────────────────────────┤
│                              │  │                             │
│  PostgreSQL :5432            │  │  Fichiers plats (DATA 2024) │
│  Database: healthcare_data   │  │                             │
│                              │  │  • finess_*.csv             │
│  Tables:                     │  │  • SATISFACTION/*.csv       │
│  • patient      (100K)       │  │  • DECES/*.csv              │
│  • consultation (1M)         │  │  • hospitalisation.csv      │
│  • professionnel (1M)        │  │                             │
│  • diagnostic   (15K)        │  │  Total: ~27 fichiers        │
│  • medicaments              │  │                             │
│  • mutuelle                  │  │                             │
│                              │  │                             │
└──────────────────────────────┘  └─────────────────────────────┘


┌───────────────────────────────────────────────────────────────┐
│                    SERVICES SUPPORT                            │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  pgAdmin :5050          Redis :6379         Bases internes    │
│  Interface PostgreSQL   Cache Airflow       • airflow-db      │
│                                             • superset-db     │
│                                                                │
└───────────────────────────────────────────────────────────────┘
```

---

## Flux de données détaillé

```
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 1: EXTRACTION (E)                   │
└─────────────────────────────────────────────────────────────┘

PostgreSQL                         CSV Files
    │                                  │
    │ Airflow Task:                   │ Airflow Task:
    │ extract_from_postgres()         │ extract_csv_files()
    │                                  │
    ├─► SELECT * FROM patient         ├─► Read finess.csv
    ├─► SELECT * FROM consultation    ├─► Read SATISFACTION/*.csv
    ├─► SELECT * FROM professionnel   ├─► Read DECES/*.csv
    └─► SELECT * FROM diagnostic      └─► Read hospitalisation.csv
    │                                  │
    │                                  │
    ▼                                  ▼
┌──────────────────────────────────────────────────┐
│         MinIO Bronze (s3://bronze/)              │
│  • bronze/postgresql/patient/extract_20250110.csv │
│  • bronze/postgresql/consultation/...            │
│  • bronze/csv/etablissements/finess.csv          │
│  • bronze/csv/satisfaction/ESATIS48H_2020.csv    │
└──────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────┐
│           PHASE 2: TRANSFORMATION T1 (Conformité)            │
└─────────────────────────────────────────────────────────────┘

Bronze Zone
    │
    │ Airflow Tasks:
    │ • t1_transform_patient()
    │ • t1_transform_consultation()
    │ • t1_transform_etablissement()
    │ • t1_transform_satisfaction()
    │ • t1_transform_deces()
    │
    │ Opérations:
    ├─► Pseudonymisation SHA-256
    │   (nom, prenom, email, tel, NSS)
    │
    ├─► Suppression PII
    │   DROP COLUMN nom, prenom, ...
    │
    ├─► Normalisation dates
    │   ISO 8601: YYYY-MM-DD
    │
    ├─► Création tranches d'âge
    │   0-18, 19-35, 36-50, 51-65, 65+
    │
    ├─► Validation clés étrangères
    │   id_patient, id_professionnel, ...
    │
    └─► Nettoyage valeurs manquantes
        NULL handling
    │
    ▼
┌──────────────────────────────────────────────────┐
│         MinIO Silver (s3://silver/)              │
│  • silver/patient/patient_clean_20250110.csv     │
│  • silver/consultation/consultation_clean_...    │
│  • silver/etablissement/...                      │
└──────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────┐
│      PHASE 3: TRANSFORMATION T2 (Modèle dimensionnel)        │
└─────────────────────────────────────────────────────────────┘

Silver Zone
    │
    │ Spark Jobs / Airflow Tasks:
    │
    ├─► CREATE DIMENSIONS
    │   │
    │   ├─► DIM_TEMPS
    │   │   Calendrier 2014-2025
    │   │   (jour, mois, année, trimestre, semaine...)
    │   │
    │   ├─► DIM_PATIENT
    │   │   FROM silver/patient_clean
    │   │   (id, sexe, age, tranche_age)
    │   │
    │   ├─► DIM_ETABLISSEMENT
    │   │   JOIN silver/etablissement + FINESS
    │   │   (id, nom, type, region, capacite)
    │   │
    │   ├─► DIM_DIAGNOSTIC
    │   │   FROM diagnostic
    │   │   (id, code_CIM10, libelle, categorie)
    │   │
    │   ├─► DIM_PROFESSIONNEL
    │   │   FROM professionnel
    │   │   (id, specialite, service)
    │   │
    │   └─► DIM_MUTUELLE, DIM_SPECIALITE, DIM_TYPE_ENQUETE
    │
    │
    └─► CREATE FAITS
        │
        ├─► FAIT_CONSULTATION
        │   JOIN consultation + patient + professionnel
        │        + diagnostic + etablissement
        │   MESURES: nb_consultations, duree_moyenne
        │   PARTITION BY annee
        │
        ├─► FAIT_HOSPITALISATION
        │   JOIN hospitalisation + patient + etablissement
        │   MESURES: nb_hospit, duree_sejour, taux_occupation
        │   PARTITION BY annee, region
        │
        ├─► FAIT_DECES
        │   JOIN deces + patient + localisation
        │   MESURES: nb_deces, age_moyen
        │   PARTITION BY region
        │
        └─► FAIT_SATISFACTION
            JOIN satisfaction + etablissement + temps
            MESURES: note_moyenne, nb_reponses
            PARTITION BY annee
    │
    ▼
┌──────────────────────────────────────────────────┐
│         MinIO Gold (s3://gold/)                  │
│                                                   │
│  dimensions/                                      │
│  ├─ dim_temps.parquet                            │
│  ├─ dim_patient.parquet                          │
│  └─ ...                                           │
│                                                   │
│  faits/                                           │
│  ├─ fait_consultation/                           │
│  │   ├─ annee=2019/*.parquet                     │
│  │   ├─ annee=2020/*.parquet                     │
│  │   └─ annee=2021/*.parquet                     │
│  ├─ fait_hospitalisation/                        │
│  ├─ fait_deces/                                  │
│  └─ fait_satisfaction/                           │
└──────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────┐
│            PHASE 4: ANALYSE ET VISUALISATION                 │
└─────────────────────────────────────────────────────────────┘

Gold Zone (Parquet)
    │
    ├────────────────────┬────────────────────┐
    │                    │                    │
    ▼                    ▼                    ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│  Superset   │  │  Jupyter Lab │  │  Direct SQL  │
│             │  │              │  │              │
│ Dashboards: │  │ Analysis:    │  │ Requêtes:    │
│ • KPIs      │  │ • EDA        │  │ • Ad-hoc     │
│ • Charts    │  │ • ML         │  │ • Validation │
│ • Reports   │  │ • Graphes    │  │ • Tests      │
└─────────────┘  └──────────────┘  └──────────────┘
    │                    │                    │
    └────────────────────┴────────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │   UTILISATEURS   │
              │                  │
              │ • Analystes      │
              │ • Data Scientists│
              │ • Décideurs CHU  │
              │ • Médecins       │
              └──────────────────┘
```

---

## Schéma réseau Docker

```
┌────────────────────────────────────────────────────────────────┐
│                Docker Network: chu_bigdata_network              │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  postgres    │  │  pgadmin     │  │  minio       │        │
│  │  :5432       │  │  :5050       │  │  :9000/:9001 │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ airflow-db   │  │ airflow-web  │  │ airflow-sch  │        │
│  │  :5432       │  │  :8080       │  │              │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │airflow-worker│  │ spark-master │  │spark-worker-1│        │
│  │              │  │  :8081       │  │              │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  jupyter     │  │ superset-db  │  │  superset    │        │
│  │  :8888       │  │  :5432       │  │  :8088       │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│  ┌──────────────┐                                              │
│  │  redis       │                                              │
│  │  :6379       │                                              │
│  └──────────────┘                                              │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
         │
         │ Port Mapping (Host → Container)
         │
         ▼
┌────────────────────────────────────────────────────────────────┐
│                    HÔTE (Votre machine)                         │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  localhost:5432  → postgres:5432     (PostgreSQL)              │
│  localhost:5050  → pgadmin:80        (pgAdmin)                 │
│  localhost:9000  → minio:9000        (MinIO API)               │
│  localhost:9001  → minio:9001        (MinIO Console)           │
│  localhost:8080  → airflow-web:8080  (Airflow)                 │
│  localhost:8081  → spark-master:8080 (Spark UI)                │
│  localhost:8888  → jupyter:8888      (Jupyter)                 │
│  localhost:8088  → superset:8088     (Superset)                │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## Volumes Docker persistants

```
┌────────────────────────────────────────────────────────────────┐
│                    VOLUMES DOCKER                               │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  chu_postgres_data         → /var/lib/postgresql/data          │
│  └─ Contient toutes les tables (patient, consultation, ...)    │
│                                                                 │
│  chu_pgadmin_data          → /var/lib/pgadmin                  │
│  └─ Configuration pgAdmin, connexions sauvegardées             │
│                                                                 │
│  chu_minio_data            → /data                             │
│  └─ Tous les buckets (bronze, silver, gold)                    │
│     ├─ bronze/ (données brutes)                                │
│     ├─ silver/ (données nettoyées)                             │
│     └─ gold/ (entrepôt de données)                             │
│                                                                 │
│  chu_airflow_db_data       → /var/lib/postgresql/data          │
│  └─ Métadonnées Airflow (DAGs, runs, logs)                     │
│                                                                 │
│  chu_superset_db_data      → /var/lib/postgresql/data          │
│  └─ Configuration Superset (dashboards, charts)                │
│                                                                 │
└────────────────────────────────────────────────────────────────┘

📌 Ces volumes PERSISTENT même si vous arrêtez les conteneurs
   Pour tout supprimer : docker-compose down -v
```

---

## Correspondance Ancien ↔ Nouveau

```
┌──────────────────────┬─────────────────────────────────────────┐
│   ANCIEN (Manuel)    │      NOUVEAU (Docker Stack)             │
├──────────────────────┼─────────────────────────────────────────┤
│                      │                                         │
│  Talend 7.3.1        │  Apache Airflow 2.8                    │
│  - Jobs ETL manuels  │  - DAGs Python automatisés             │
│  - Interface lourde  │  - Web UI moderne                      │
│  - Obsolète (2020)   │  - À jour (2024)                       │
│                      │                                         │
│  Cloudera VM         │  MinIO (S3-compatible)                 │
│  - HDFS distribué    │  - Object Storage                      │
│  - 60 GB VM          │  - Conteneur Docker léger              │
│  - Lent au démarrage │  - Démarrage instantané                │
│                      │                                         │
│  Hive/Hadoop         │  Apache Spark 3.5                      │
│  - MapReduce classique│  - 100x plus rapide                    │
│  - HiveQL            │  - PySpark + SQL                       │
│  - Pas de Python     │  - API Python complète                 │
│                      │                                         │
│  Power BI (payant)   │  Apache Superset (gratuit)             │
│  - 150€/utilisateur  │  - Open source                         │
│  - Windows only      │  - Cross-platform                      │
│  - Licence requise   │  - Libre                               │
│                      │                                         │
│  PostgreSQL 14       │  PostgreSQL 15                         │
│  - Installation      │  - Docker                              │
│    manuelle          │  - Configuration automatique           │
│                      │                                         │
│  Scripts manuels     │  Jupyter Lab                           │
│  - Python/R isolés   │  - Environnement complet               │
│  - Pas d'interactivité│  - Notebooks interactifs               │
│                      │                                         │
│  Installation :      │  Installation :                        │
│  2-3 heures          │  5 minutes                             │
│                      │                                         │
│  Stockage :          │  Stockage :                            │
│  60+ GB (VM)         │  10-20 GB (conteneurs)                 │
│                      │                                         │
│  Démarrage :         │  Démarrage :                           │
│  10-15 minutes       │  30 secondes                           │
│                      │                                         │
└──────────────────────┴─────────────────────────────────────────┘
```

---

## Légende des symboles

```
📊  Visualisation / Dashboards
📓  Notebooks / Analyse
🥇  Zone Gold (Data Warehouse)
🥈  Zone Silver (Cleaned Data)
🥉  Zone Bronze (Raw Data)
⚙️  Orchestration / ETL
🗄️  Base de données relationnelle
📁  Fichiers plats (CSV)
🔄  Transformation
➡️  Flux de données
🌐  Interface web
🐳  Conteneur Docker
💾  Stockage persistant
```

---

Cette architecture vous permet de :
✅ Traiter des données massives (1M+ lignes)
✅ Respecter le RGPD (pseudonymisation)
✅ Optimiser les performances (partitionnement, Parquet)
✅ Visualiser les résultats (dashboards interactifs)
✅ Travailler en équipe (tout en Docker)
✅ Reproduire facilement (portable)

**Le tout en 1 seule commande de démarrage ! 🚀**
