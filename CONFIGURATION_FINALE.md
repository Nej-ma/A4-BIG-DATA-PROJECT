# Configuration Finale - CHU Data Lakehouse

## Résumé des Modifications

### 1. DAGs Airflow Nettoyés

**DAGs supprimés** (obsolètes):
- `chu_etl_pipeline.py`
- `chu_pipeline_modular.py`
- `exemple_delta_lake.py`

**DAGs actifs** (production):
- `chu_pipeline_pyspark_jobs` : Pipeline complet monolithique (Bronze → Silver → Gold → Benchmarks)
- `chu_pipeline_split` : Pipeline avec tâches individuelles (parallélisation max)

### 2. Mémoire Spark Optimisée pour 32G RAM

**Configuration Worker** ([docker-compose.yml](docker-compose.yml:150)):
```yaml
SPARK_WORKER_MEMORY=8G
SPARK_WORKER_CORES=2
```

**Configuration Jobs** (DAGs Airflow):
```python
SPARK_DRIVER_MEMORY=8g
SPARK_EXECUTOR_MEMORY=8g
```

**Vérification**:
```bash
docker logs chu_spark_worker | grep RAM
# Output: Starting Spark worker with 2 cores, 8.0 GiB RAM
```

### 3. Notebooks Nettoyés

Tous les notebooks ont été nettoyés pour respecter un style sobre:
- ✅ Suppression de tous les emojis
- ✅ Messages techniques concis
- ✅ Pas de décoration ASCII
- ✅ Code Python standard

**Notebooks modifiés**:
1. `01_Extract_Bronze_SOURCES_DIRECTES.ipynb` - Correction erreur df_results
2. `02_Transform_Silver_NETTOYAGE.ipynb`
3. `03_Transform_Gold_STAR_SCHEMA.ipynb`
4. `04_Performance_Benchmarks_CLEAN.ipynb`
5. `05_Setup_Superset.ipynb`
6. `06_Export_Gold_to_PostgreSQL.ipynb`

### 4. Structure Modulaire Jobs Spark

**Nouvelle structure créée**:
```
spark/jobs/
├── common/               # Utilitaires partagés
│   ├── spark_utils.py   # Fonctions communes
│   └── __init__.py
├── bronze/              # Jobs extraction
│   ├── extract_postgres.py
│   └── extract_csv_etablissements.py
├── silver/              # Jobs transformation
│   └── transform_patient.py
└── gold/                # Jobs star schema
    ├── dimensions/
    │   └── build_dim_patient.py
    └── facts/
```

**Jobs monolithiques conservés** (compatibilité):
- `01_extract_bronze.py` (supporte --postgres-table, --csv-source)
- `02_transform_silver.py` (supporte --subject)
- `03_transform_gold.py` (supporte --task)
- `04_benchmarks.py`

## Architecture Finale

### Services Docker

```
Port  Service         Status    Détails
----  ------------    -------   ------------------------
5432  PostgreSQL      Running   Données sources
5050  PgAdmin         Running   Interface PostgreSQL
9000  MinIO           Running   Stockage S3 (Delta Lake)
9001  MinIO Console   Running   Interface MinIO
7077  Spark Master    Running   Coordinateur Spark
8081  Spark Worker    Running   8GB RAM, 2 cores
8080  Airflow         Running   Orchestration
8088  Superset        Running   BI Dashboards
8888  Jupyter Lab     Running   Développement notebooks
4040  Spark UI        Running   Monitoring Spark jobs
```

### DAG Airflow Recommandé

**Pour développement** : `chu_pipeline_split`
- Exécution parallèle par tâche
- Retry ciblé en cas d'erreur
- Monitoring granulaire

**Pour production** : `chu_pipeline_pyspark_jobs`
- Exécution séquentielle complète
- Moins de ressources
- Run nightly

### Flux de Données

```
Sources (PostgreSQL + CSV)
    ↓
Bronze Layer (Parquet - données brutes)
    ↓
Silver Layer (Parquet - nettoyé + anonymisé RGPD)
    ↓
Gold Layer (Parquet - Star Schema)
    ↓
PostgreSQL Gold Schema (pour Superset)
    ↓
Superset Dashboards
```

## Problèmes Résolus

### 1. Erreur Spark Worker Restart Loop
**Cause** : Incohérence hostname (chu_spark_master vs chu-spark-master)
**Solution** : Uniformisé à `chu-spark-master` dans docker-compose.yml:161

### 2. Erreur Permission Bronze Layer
**Cause** : Fichiers créés par root, non supprimables par jovyan
**Solution** :
```bash
docker exec -u root chu_jupyter rm -rf /home/jovyan/data/bronze/*
docker exec -u root chu_jupyter chown -R jovyan:users /home/jovyan/data
```

### 3. Erreur df_results Notebook
**Cause** : Variable `df_results` non définie (devrait être `results`)
**Solution** : Ajout de `df_results = pd.DataFrame(results)` dans cellule 13

### 4. Erreur DAG TaskGroup Dependencies
**Cause** : `[bronze_pg, bronze_csv] >> [silver_tasks]` non supporté
**Solution** : Séparation en lignes individuelles

## Utilisation

### Lancer le Pipeline Complet

```bash
# Via Airflow UI (http://localhost:8080)
# Login: admin / admin123
# DAGs → chu_pipeline_pyspark_jobs → Trigger DAG

# Via CLI
docker exec chu_airflow_webserver airflow dags trigger chu_pipeline_pyspark_jobs
```

### Lancer une Tâche Spécifique

```bash
# Via Airflow
docker exec chu_airflow_webserver airflow dags trigger chu_pipeline_split

# Via Spark Submit (exemple)
docker exec chu_spark_master spark-submit \
  --master spark://chu-spark-master:7077 \
  --driver-memory 8g \
  --executor-memory 8g \
  /opt/spark-apps/01_extract_bronze.py --postgres-table Patient
```

### Développement Notebook

```python
# Dans Jupyter (http://localhost:8888, token: admin123)
# Les notebooks sont prêts à l'emploi
# Data disponible dans /home/jovyan/data/{bronze,silver,gold}
```

## Performance

### Benchmarks Actuels

- Bronze Extract: ~50s (13 tables PostgreSQL + 4 CSV)
- Silver Transform: ~40s (toutes transformations)
- Gold Star Schema: ~30s (5 dimensions + 4 faits)
- Total Pipeline: ~2-3 minutes

### Optimisations Appliquées

1. ✅ Mémoire Spark: 4G → 8G
2. ✅ Adaptive Query Execution activé
3. ✅ Partition coalescing activé
4. ✅ Parallélisation TaskGroups Airflow
5. ✅ Données 2019 filtrées (98% réduction pour deces.csv)

## Prochaines Étapes Recommandées

1. **Migration progressive vers jobs modulaires**
   - Plus maintenable
   - Meilleur monitoring
   - Réutilisabilité

2. **Ajouter tests unitaires**
   - pytest pour jobs Spark
   - Validation schéma

3. **Monitoring avancé**
   - Metrics Prometheus
   - Grafana dashboards

4. **CI/CD**
   - GitHub Actions
   - Automated tests
   - Deployment automation

## Documentation

- [README Jobs Spark](spark/jobs/README.md) : Structure modulaire détaillée
- [Docker Compose](docker-compose.yml) : Configuration services
- [Notebooks Jupyter](jupyter/notebooks/) : ETL interactif

## Support

Pour toute question:
1. Vérifier les logs: `docker logs <container_name>`
2. Consulter Airflow UI: http://localhost:8080
3. Consulter Spark UI: http://localhost:4040 (pendant job)
4. Consulter ce document: CONFIGURATION_FINALE.md

---

**Date de configuration** : 24 octobre 2025
**Auteurs** : Nejma MOUALHI | Brieuc OLIVIERI | Nicolas TAING
**Version** : 2.0 (optimisée 32G RAM)
