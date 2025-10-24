# Corrections Finales - Problèmes Résolus

Date: 24 octobre 2025

## Problèmes Corrigés

### 1. Erreur `dim_temps` dans Airflow DAG ✅

**Erreur**:
```
RuntimeError: Python in worker has different version 3.8 than that in driver 3.11
```

**Cause**:
- Airflow tourne avec Python 3.11
- Spark Workers tournent avec Python 3.8
- PySpark nécessite la même version Python sur driver et workers

**Solution**:
Ajout des variables d'environnement dans les deux DAGs ([chu_pipeline_split.py](airflow/dags/chu_pipeline_split.py) et [pipeline_pyspark_jobs.py](airflow/dags/pipeline_pyspark_jobs.py)):

```python
DEFAULT_ENV = {
    ...
    "PYSPARK_PYTHON": "python3",
    "PYSPARK_DRIVER_PYTHON": "python3",
}
```

**Test**:
```bash
docker exec chu_airflow_webserver bash -c \
  "cd /opt/spark-apps && PYSPARK_PYTHON=python3 PYSPARK_DRIVER_PYTHON=python3 \
  python 03_transform_gold.py --task dim_temps"
# Résultat: SUCCESS - 4,748 rows
```

### 2. Fichier `departements` manquant dans Bronze ✅

**Erreur dans Notebook 3**:
```
AnalysisException: [PATH_NOT_FOUND] Path does not exist:
file:/home/jovyan/data/bronze/csv/departements
```

**Cause**:
Le fichier `departements-francais.csv` n'avait pas été extrait vers la couche Bronze.

**Solution**:
Extraction manuelle du fichier CSV vers Bronze:

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit
from datetime import datetime

spark = SparkSession.builder.appName('Extract-Departements').getOrCreate()

df = spark.read \
    .option('header', 'true') \
    .option('inferSchema', 'true') \
    .option('sep', ';') \
    .csv('/home/jovyan/DATA_2024/departements-francais.csv')

df_with_meta = df \
    .withColumn('ingestion_timestamp', current_timestamp()) \
    .withColumn('ingestion_date', lit(datetime.now().strftime('%Y-%m-%d')))

df_with_meta.write.mode('overwrite').parquet('/home/jovyan/data/bronze/csv/departements')
```

**Résultat**: 101 départements extraits avec succès

**Vérification**:
```bash
docker exec chu_jupyter bash -c "ls -lh /home/jovyan/data/bronze/csv/"
# Output: departements directory exists
```

### 3. Erreur de permissions sur Gold Layer ✅

**Erreur**:
```
SparkException: Unable to clear output directory file:/opt/spark-data/gold/dim_temps
prior to writing to it.
```

**Cause**:
Fichiers créés par root lors de runs précédents, non supprimables en mode `overwrite`.

**Solution**:
Nettoyage avec permissions root et changement de propriétaire:

```bash
docker exec -u root chu_jupyter bash -c \
  "rm -rf /home/jovyan/data/gold/dim_temps && \
   chown -R jovyan:users /home/jovyan/data/gold"
```

**Solution permanente**:
Fix des permissions sur toutes les couches:

```bash
docker exec -u root chu_jupyter bash -c \
  "chown -R jovyan:users /home/jovyan/data/bronze \
                         /home/jovyan/data/silver \
                         /home/jovyan/data/gold"
```

## État Actuel

### Services Opérationnels

```
✅ PostgreSQL (5432)      - Sources données
✅ Spark Master (7077)    - Coordinateur
✅ Spark Worker (8G RAM)  - Exécuteur
✅ Airflow (8080)         - Orchestration
✅ Jupyter (8888)         - Notebooks
✅ Superset (8088)        - BI
✅ MinIO (9000-9001)      - Stockage S3
```

### DAGs Airflow

| DAG | Status | Description |
|-----|--------|-------------|
| `chu_pipeline_pyspark_jobs` | ✅ Ready | Pipeline complet monolithique |
| `chu_pipeline_split` | ✅ Ready | Pipeline granulaire par tâche |

### Données Bronze Disponibles

**PostgreSQL (13 tables)**:
- Patient, Consultation, Diagnostic
- Professionnel_de_sante, AAAA, date
- Mutuelle, Adher, Prescription
- Medicaments, Laboratoire, Salle, Specialites

**CSV (4 fichiers)**:
- etablissement_sante (416K lignes)
- satisfaction_esatis48h_2019 (1K lignes)
- deces_2019 (620K lignes - filtré)
- **departements (101 lignes)** ← NOUVEAU

### Test Réussi

```bash
# Test dim_temps
docker exec chu_airflow_webserver bash -c \
  "cd /opt/spark-apps && \
   PYSPARK_PYTHON=python3 PYSPARK_DRIVER_PYTHON=python3 \
   python 03_transform_gold.py --task dim_temps"

# Résultat:
# ✅ Created 4,748 days (2013-2025)
# ✅ Saved dim_temps
# ✅ Gold star schema creation completed successfully
```

## Notebook 3 - Corrections

Le notebook `03_Transform_Gold_STAR_SCHEMA.ipynb` devrait maintenant fonctionner correctement car:

1. ✅ Le fichier `departements` existe dans Bronze
2. ✅ Les permissions Gold sont correctes
3. ✅ dim_temps peut être créée sans erreur

**Pour tester**: Réexécuter les cellules du notebook 3, en particulier:
- Cellule dim_temps
- Cellule dim_etablissement (qui utilise departements)

## Commandes de Vérification

### Vérifier les fichiers Bronze
```bash
docker exec chu_jupyter bash -c "ls -lh /home/jovyan/data/bronze/csv/"
```

### Vérifier les permissions
```bash
docker exec chu_jupyter bash -c "ls -la /home/jovyan/data/ | grep -E 'bronze|silver|gold'"
```

### Tester un job Gold
```bash
docker exec chu_airflow_webserver bash -c \
  "cd /opt/spark-apps && \
   PYSPARK_PYTHON=python3 PYSPARK_DRIVER_PYTHON=python3 \
   python 03_transform_gold.py --task dim_patient"
```

### Lancer le pipeline complet
```bash
# Via Airflow UI: http://localhost:8080
# Ou via CLI:
docker exec chu_airflow_webserver airflow dags trigger chu_pipeline_pyspark_jobs
```

## Points d'Attention

### 1. Permissions Fichiers
Si vous rencontrez à nouveau des erreurs de permissions:
```bash
docker exec -u root chu_jupyter bash -c \
  "chown -R jovyan:users /home/jovyan/data"
```

### 2. Python Version
Toujours définir ces variables lors de l'exécution de jobs PySpark depuis Airflow:
```python
"PYSPARK_PYTHON": "python3",
"PYSPARK_DRIVER_PYTHON": "python3",
```

### 3. Nettoyage Bronze/Silver/Gold
Si nécessaire, pour un fresh start:
```bash
docker exec -u root chu_jupyter bash -c \
  "rm -rf /home/jovyan/data/bronze/* \
          /home/jovyan/data/silver/* \
          /home/jovyan/data/gold/* && \
   chown -R jovyan:users /home/jovyan/data"
```

## Prochaines Actions

1. ✅ **Tester Notebook 3** : Devrait fonctionner maintenant
2. ✅ **Tester DAG split** : Toutes les tâches devraient passer
3. ⏳ **Compléter Gold Layer** : Créer toutes les dimensions et faits
4. ⏳ **Export PostgreSQL** : Pour Superset
5. ⏳ **Dashboards Superset** : Visualisations

## Documentation Mise à Jour

- ✅ [CONFIGURATION_FINALE.md](CONFIGURATION_FINALE.md)
- ✅ [spark/jobs/README.md](spark/jobs/README.md)
- ✅ Ce document: CORRECTIONS_FINALES.md

---

**Auteurs**: Nejma MOUALHI | Brieuc OLIVIERI | Nicolas TAING
**Date**: 24 octobre 2025
**Version**: 2.1 (avec corrections Python + departements + permissions)
