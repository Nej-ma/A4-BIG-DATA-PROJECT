# Livrable 2 : Modèle Physique et Optimisation

**Projet:** CHU Data Lakehouse
**Auteurs:** Nejma MOUALHI | Brieuc OLIVIERI | Nicolas TAING
**Formation:** CESI FISA A4
**Année:** 2025-2026

---

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Scripts développés](#scripts-développés)
4. [Installation et démarrage](#installation-et-démarrage)
5. [Exécution des jobs](#exécution-des-jobs)
6. [Tests de performance](#tests-de-performance)
7. [Résultats attendus](#résultats-attendus)

---

## 🎯 Vue d'ensemble

Ce livrable implémente un **Data Lakehouse** complet avec architecture en 3 couches (Bronze, Silver, Gold) utilisant:
- **MinIO** (stockage objet S3-compatible)
- **Apache Spark** (traitement distribué)
- **Delta Lake** (format de stockage transactionnel)
- **PostgreSQL** (source de données opérationnelle)

### Objectifs du Livrable 2

✅ Script pour la création et le chargement de données dans les tables
✅ Vérification des données présentes et accès aux données à travers les tables
✅ Script montrant le peuplement des tables
✅ Script pour le partitionnement et les buckets
✅ Graphes montrant les temps de réponses pour évaluer la performance
✅ Requêtes faisant foi pour l'évaluation de la performance

---

## 🏗️ Architecture

### Architecture en 3 Couches (Medallion)

```
┌─────────────────────────────────────────────────────────────┐
│  SOURCES DE DONNÉES                                          │
├─────────────────────────────────────────────────────────────┤
│  • PostgreSQL (100K patients, 1M+ consultations)            │
│  • CSV Décès (~300K lignes)                                 │
│  • CSV Satisfaction (multiple années)                       │
│  • CSV Établissements de santé                              │
│  • CSV Hospitalisations                                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  BRONZE LAYER (Raw Data)                                     │
│  📦 s3a://lakehouse/bronze/                                  │
├─────────────────────────────────────────────────────────────┤
│  • Format: Delta Lake                                        │
│  • Données brutes non transformées                           │
│  • Partitionnement par date d'ingestion                      │
│  • Métadonnées d'ingestion ajoutées                          │
└─────────────────────────────────────────────────────────────┘
                           ↓ Spark ETL
┌─────────────────────────────────────────────────────────────┐
│  SILVER LAYER (Cleaned Data)                                 │
│  📦 s3a://lakehouse/silver/                                  │
├─────────────────────────────────────────────────────────────┤
│  • Nettoyage des données                                     │
│  • Validation et typage correct                              │
│  • Dédoublonnage                                             │
│  • Jointures et enrichissements                              │
│  • Partitionnement par année/mois                            │
└─────────────────────────────────────────────────────────────┘
                           ↓ Spark ETL
┌─────────────────────────────────────────────────────────────┐
│  GOLD LAYER (Business Layer - Star Schema)                   │
│  📦 s3a://lakehouse/gold/                                    │
├─────────────────────────────────────────────────────────────┤
│  • Modèle dimensionnel (étoile)                              │
│  • Tables de faits: Consultations, Hospitalisations, etc.    │
│  • Tables de dimensions: Temps, Patient, Diagnostic, etc.    │
│  • PARTITIONNEMENT optimisé                                  │
│  • BUCKETING sur clés de jointure                            │
│  • Z-ORDERING pour performance                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 Scripts Développés

### Structure des dossiers

```
spark/jobs/
├── utils/
│   └── spark_utils.py              # Utilitaires réutilisables
├── bronze/
│   ├── ingest_postgres_to_bronze.py # Ingestion PostgreSQL → Bronze
│   └── ingest_csv_to_bronze.py      # Ingestion CSV → Bronze
├── silver/
│   ├── transform_to_silver.py       # Nettoyage et validation
│   └── enrich_silver.py             # Enrichissement
├── gold/
│   ├── create_dimensions.py         # Création des dimensions
│   ├── create_facts.py              # Création des faits
│   └── optimize_gold.py             # Optimisations (partition, bucket)
└── performance/
    ├── benchmark_queries.py         # Requêtes de benchmark
    └── measure_performance.py       # Mesure et graphiques
```

### Scripts Principaux

#### 1. **utils/spark_utils.py**
Fonctions utilitaires pour:
- Création de sessions Spark configurées
- Connexion PostgreSQL
- Lecture/Écriture Delta Lake
- Ajout de métadonnées

#### 2. **bronze/ingest_postgres_to_bronze.py**
- Extrait 13 tables de PostgreSQL
- Sauvegarde en Delta Lake dans MinIO
- Partitionnement par date d'ingestion

#### 3. **bronze/ingest_csv_to_bronze.py**
- Ingère tous les CSV (décès, satisfaction, établissements)
- Gestion des différents séparateurs (`,` et `;`)
- Encodage UTF-8

#### 4. **silver/** (à venir)
- Nettoyage des données
- Validation des types
- Dédoublonnage

#### 5. **gold/** (à venir)
- Création du modèle dimensionnel
- Partitionnement et bucketing
- Optimisations Z-ORDER

#### 6. **performance/** (à venir)
- Requêtes de benchmark
- Mesure des temps de réponse
- Génération de graphiques

---

## 🚀 Installation et Démarrage

### Prérequis

- Docker et Docker Compose installés
- 8 GB RAM minimum
- 20 GB espace disque

### Démarrage de l'infrastructure

```bash
# 1. Démarrer tous les services
docker compose up -d

# 2. Vérifier que tous les conteneurs sont démarrés
docker compose ps

# 3. Vérifier les logs
docker logs chu_postgres
docker logs chu_minio
docker logs chu_spark_master
```

### Services disponibles

- **PostgreSQL:** localhost:5432
- **PgAdmin:** http://localhost:5050
- **MinIO Console:** http://localhost:9001 (minioadmin / minioadmin123)
- **Spark Master UI:** http://localhost:8081
- **Jupyter Lab:** http://localhost:8888 (token: admin123)
- **Airflow:** http://localhost:8080
- **Superset:** http://localhost:8088

---

## ⚙️ Exécution des Jobs

### Méthode 1: Via Jupyter Lab

```python
# 1. Ouvrir Jupyter: http://localhost:8888 (token: admin123)
# 2. Créer un nouveau notebook
# 3. Exécuter:

!cd /opt/spark-apps && python jobs/bronze/ingest_postgres_to_bronze.py
```

### Méthode 2: Via Docker Exec

```bash
# Job Bronze - PostgreSQL
docker exec chu_spark_master \
  /opt/spark/bin/spark-submit \
  --master local[*] \
  /opt/spark-apps/jobs/bronze/ingest_postgres_to_bronze.py

# Job Bronze - CSV
docker exec chu_spark_master \
  /opt/spark/bin/spark-submit \
  --master local[*] \
  /opt/spark-apps/jobs/bronze/ingest_csv_to_bronze.py
```

### Méthode 3: Via Airflow DAG (recommandé pour production)

Les DAGs Airflow seront créés pour orchestrer l'ensemble du pipeline.

---

## 📊 Tests de Performance

### Requêtes de Benchmark

Les requêtes suivantes seront testées:

1. **Consultations par établissement sur période**
   - Filtrage par établissement et date
   - Agrégation mensuelle

2. **Hospitalisations par diagnostic**
   - Jointure dimension diagnostic
   - Calcul de durée moyenne

3. **Décès par région**
   - Agrégation géographique
   - Filtrage temporel

4. **Satisfaction par région**
   - Scores moyens
   - Taux de recommandation

### Métriques mesurées

- **Temps de réponse** (ms)
- **Nombre de lignes scannées**
- **Efficacité du partitionnement**
- **Impact du bucketing**
- **Gains Z-ORDERING**

### Comparaisons

- Sans optimisation vs Avec partitionnement
- Avec partitionnement vs Avec bucketing
- Avant Z-ORDER vs Après Z-ORDER

---

## 📈 Résultats Attendus

### Volumétrie

| Source | Nombre de lignes | Taille estimée |
|--------|------------------|----------------|
| Patients | 100,000 | ~10 MB |
| Consultations | 1,027,157 | ~100 MB |
| Décès | ~300,000 | ~30 MB |
| Satisfaction | ~50,000 | ~20 MB |
| Établissements | ~30,000 | ~5 MB |

### Objectifs de Performance

- Requête simple: < 1 seconde
- Requête avec jointure: < 3 secondes
- Requête complexe (multiples jointures): < 10 secondes

---

## 🔍 Vérification des Données

### Vérifier les données Bronze

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Verification").getOrCreate()

# Lire une table Bronze
df = spark.read.format("delta").load("s3a://lakehouse/bronze/postgres/Patient")
print(f"Nombre de patients: {df.count()}")
df.show(5)
```

### Vérifier MinIO

1. Ouvrir http://localhost:9001
2. Login: minioadmin / minioadmin123
3. Naviguer dans le bucket `lakehouse`
4. Vérifier la présence des dossiers `bronze/`, `silver/`, `gold/`

---

## 📝 Documentation Complémentaire

- [Modèle Dimensionnel](./modele_dimensionnel.md)
- Architecture détaillée (à venir)
- Guide des optimisations (à venir)
- Rapport de performance (à venir)

---

## 🐛 Troubleshooting

### Problème: Conteneur Spark ne démarre pas
```bash
docker logs chu_spark_master
docker restart chu_spark_master
```

### Problème: Connexion MinIO échoue
```bash
# Vérifier que MinIO est démarré
docker logs chu_minio

# Recréer les buckets
docker restart chu_minio_setup
```

### Problème: PostgreSQL vide
```bash
# Restaurer le dump manuellement
docker exec chu_postgres pg_restore -U admin -d healthcare_data \
  -v --no-owner --no-acl \
  "/docker-entrypoint-initdb.d/DATA 2024/BDD PostgreSQL/DATA2023"
```

---

## 👥 Équipe

- **Nejma MOUALHI**
- **Brieuc OLIVIERI**
- **Nicolas TAING**

CESI FISA A4 - 2025-2026
