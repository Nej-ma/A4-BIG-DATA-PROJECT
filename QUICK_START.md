# Quick Start Guide - CHU Data Lakehouse

## 🚀 Démarrage Rapide

### 1. Démarrer l'Infrastructure

```bash
cd "C:\Users\littl\Desktop\Big DATA\projet_git"
docker-compose up -d
```

**Attendre 2-3 minutes** que tous les services démarrent.

### 2. Vérifier les Services

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep chu_
```

Tous les services doivent être `Up` ou `Up (healthy)`.

### 3. Accès aux Interfaces

| Service | URL | Login | Password |
|---------|-----|-------|----------|
| **Airflow** | http://localhost:8080 | admin | admin123 |
| **Jupyter Lab** | http://localhost:8888 | - | admin123 (token) |
| **Superset** | http://localhost:8088 | admin | admin123 |
| **MinIO Console** | http://localhost:9001 | minioadmin | minioadmin123 |
| **PgAdmin** | http://localhost:5050 | admin@chu.fr | admin123 |
| **Spark Master UI** | http://localhost:8081 | - | - |

## 📊 Exécuter le Pipeline ETL

### Option A: Pipeline Complet (Recommandé pour Production)

1. Aller sur http://localhost:8080
2. Login avec `admin` / `admin123`
3. Cliquer sur le DAG `chu_pipeline_pyspark_jobs`
4. Cliquer sur le bouton ▶️ (Play) en haut à droite
5. Confirmer avec "Trigger DAG"

**Durée**: ~3-5 minutes

**Ce qui est exécuté**:
- Bronze: Extraction de toutes les sources
- Silver: Nettoyage et anonymisation
- Gold: Construction du star schema
- Benchmarks: Tests de performance

### Option B: Pipeline Granulaire (Recommandé pour Dev/Debug)

1. Aller sur http://localhost:8080
2. Login avec `admin` / `admin123`
3. Cliquer sur le DAG `chu_pipeline_split`
4. Cliquer sur le bouton ▶️ (Play)

**Avantages**:
- Chaque tâche s'exécute individuellement
- Retry ciblé en cas d'erreur
- Parallélisation maximale
- Monitoring précis

### Option C: Notebooks Jupyter (Recommandé pour Exploration)

1. Aller sur http://localhost:8888
2. Token: `admin123`
3. Ouvrir le répertoire `notebooks/`
4. Exécuter les notebooks dans l'ordre:
   - `01_Extract_Bronze_SOURCES_DIRECTES.ipynb`
   - `02_Transform_Silver_NETTOYAGE.ipynb`
   - `03_Transform_Gold_STAR_SCHEMA.ipynb`
   - `04_Performance_Benchmarks_CLEAN.ipynb`
   - `06_Export_Gold_to_PostgreSQL.ipynb`

## 🔍 Monitoring

### Vérifier l'État des Jobs Airflow

```bash
# Liste des DAGs
docker exec chu_airflow_webserver airflow dags list

# État d'un run spécifique
docker exec chu_airflow_webserver airflow dags list-runs -d chu_pipeline_pyspark_jobs
```

### Logs en Temps Réel

```bash
# Logs Spark Worker
docker logs -f chu_spark_worker

# Logs Airflow Scheduler
docker logs -f chu_airflow_scheduler

# Logs Jupyter
docker logs -f chu_jupyter
```

### Vérifier les Données

```bash
# Bronze
docker exec chu_jupyter bash -c "ls -lh /home/jovyan/data/bronze/{postgres,csv}/"

# Silver
docker exec chu_jupyter bash -c "ls -lh /home/jovyan/data/silver/"

# Gold
docker exec chu_jupyter bash -c "ls -lh /home/jovyan/data/gold/"
```

## 🐛 Troubleshooting

### Erreur: Python version mismatch

**Symptôme**: `RuntimeError: Python in worker has different version 3.8 than that in driver 3.11`

**Solution**: Les DAGs ont déjà été corrigés avec les variables `PYSPARK_PYTHON` et `PYSPARK_DRIVER_PYTHON`.

Si le problème persiste:
```bash
docker-compose restart airflow-scheduler airflow-webserver
```

### Erreur: Permission denied

**Symptôme**: `Unable to clear output directory` ou `Permission denied`

**Solution**:
```bash
docker exec -u root chu_jupyter bash -c "chown -R jovyan:users /home/jovyan/data"
```

### Erreur: Spark Worker en restart loop

**Symptôme**: Container `chu_spark_worker` redémarre continuellement

**Solution**: Vérifier les logs:
```bash
docker logs --tail 50 chu_spark_worker
```

Le hostname est correct (`chu-spark-master`). Si problème persiste:
```bash
docker-compose restart spark-worker
```

### Erreur: Fichier manquant (PATH_NOT_FOUND)

**Symptôme**: `Path does not exist: file:/home/jovyan/data/bronze/csv/departements`

**Solution**: Le fichier a déjà été extrait. Vérifier:
```bash
docker exec chu_jupyter bash -c "ls -la /home/jovyan/data/bronze/csv/"
```

Si manquant, réexécuter le notebook 01 ou extraire manuellement.

### Nettoyer et Recommencer

Si vous voulez un fresh start complet:

```bash
# Arrêter tous les services
docker-compose down

# Nettoyer les données (ATTENTION: supprime toutes les données!)
docker exec -u root chu_jupyter bash -c "rm -rf /home/jovyan/data/bronze/* /home/jovyan/data/silver/* /home/jovyan/data/gold/*"

# Redémarrer
docker-compose up -d
```

## 📈 Visualiser les Résultats

### Option 1: Superset (BI)

1. Aller sur http://localhost:8088
2. Login: `admin` / `admin123`
3. Settings → Database Connections → + DATABASE
4. Sélectionner "PostgreSQL"
5. SQLAlchemy URI:
   ```
   postgresql://admin:admin123@chu_postgres:5432/healthcare_data
   ```
6. Advanced → SQL Lab: Cocher "Expose database in SQL Lab"
7. Test Connection → CONNECT
8. SQL Lab → sélectionner schema `gold`

### Option 2: PgAdmin

1. Aller sur http://localhost:5050
2. Login: `admin@chu.fr` / `admin123`
3. Add Server:
   - Name: CHU Healthcare
   - Host: chu_postgres
   - Port: 5432
   - Database: healthcare_data
   - Username: admin
   - Password: admin123

### Option 3: Jupyter Notebooks

Ouvrir `06_Export_Gold_to_PostgreSQL.ipynb` pour voir les requêtes SQL exemples.

## 📊 Données Disponibles

### Bronze Layer (Données Brutes)
- **PostgreSQL**: 13 tables (Patient, Consultation, Diagnostic, etc.)
- **CSV**: 4 fichiers (établissements, satisfaction, décès 2019, départements)
- **Total**: ~4M lignes

### Silver Layer (Nettoyé + Anonymisé)
- Patient (anonymisé SHA-256)
- Consultation (dates standardisées)
- Établissements (enrichis)
- Satisfaction 2019
- Décès 2019
- Tables de référence

### Gold Layer (Star Schema)
**Dimensions**:
- dim_temps (4,748 jours: 2013-2025)
- dim_patient
- dim_diagnostic
- dim_professionnel
- dim_etablissement

**Faits**:
- fait_consultation (1M+ consultations)
- fait_hospitalisation (82K hospitalisations)
- fait_deces (620K décès 2019)
- fait_satisfaction (8 évaluations 2019)

## 🔧 Configuration

### Mémoire Spark (32G RAM disponible)
- Driver Memory: 8G
- Executor Memory: 8G
- Worker Cores: 2

Pour modifier:
1. Éditer [docker-compose.yml](docker-compose.yml) (ligne 150)
2. Éditer les DAGs: [chu_pipeline_split.py](airflow/dags/chu_pipeline_split.py), [pipeline_pyspark_jobs.py](airflow/dags/pipeline_pyspark_jobs.py)
3. Redémarrer: `docker-compose restart spark-worker airflow-scheduler`

## 📚 Documentation Complète

- [CONFIGURATION_FINALE.md](CONFIGURATION_FINALE.md) - Configuration détaillée
- [CORRECTIONS_FINALES.md](CORRECTIONS_FINALES.md) - Problèmes résolus
- [spark/jobs/README.md](spark/jobs/README.md) - Structure jobs modulaires

## 🆘 Support

En cas de problème:
1. Vérifier les logs du container concerné
2. Consulter [CORRECTIONS_FINALES.md](CORRECTIONS_FINALES.md)
3. Redémarrer le service: `docker-compose restart <service_name>`
4. Fresh start complet si nécessaire

---

**Projet**: CHU Data Lakehouse
**Auteurs**: Nejma MOUALHI | Brieuc OLIVIERI | Nicolas TAING
**Version**: 2.1
**Date**: 24 octobre 2025
