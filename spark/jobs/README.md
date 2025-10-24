# CHU Spark Jobs - Structure Modulaire

## Architecture

Les jobs Spark sont organisés de manière modulaire pour permettre:
- Parallélisation maximale
- Retry ciblés en cas d'erreur
- Monitoring précis des performances
- Réutilisabilité du code

## Structure des Répertoires

```
spark/jobs/
├── common/                          # Utilitaires partagés
│   ├── __init__.py
│   └── spark_utils.py              # Fonctions communes (Spark session, paths, JDBC)
│
├── bronze/                          # Extraction des données brutes
│   ├── extract_postgres.py         # Extraction table PostgreSQL (1 table)
│   └── extract_csv_etablissements.py  # Extraction CSV établissements
│
├── silver/                          # Transformation et nettoyage
│   └── transform_patient.py        # Transformation Patient avec anonymisation
│
├── gold/                            # Star schema
│   ├── dimensions/
│   │   └── build_dim_patient.py    # Construction dimension patient
│   └── facts/
│       └── (à venir)
│
├── benchmarks/                      # Tests de performance
│   └── (à venir)
│
├── 01_extract_bronze.py            # Job monolithique Bronze (legacy)
├── 02_transform_silver.py          # Job monolithique Silver (legacy)
├── 03_transform_gold.py            # Job monolithique Gold (legacy)
└── 04_benchmarks.py                # Job benchmarks (legacy)
```

## Jobs Modulaires vs Monolithiques

### Jobs Monolithiques (actuels)
- `01_extract_bronze.py --postgres-table Patient` : Extrait UNE table
- `02_transform_silver.py --subject patient` : Transforme UN sujet
- `03_transform_gold.py --task dim_patient` : Construit UNE table

### Jobs Modulaires (nouveaux - recommandés)
- `bronze/extract_postgres.py Patient` : Extrait UNE table PostgreSQL
- `silver/transform_patient.py` : Transforme les patients
- `gold/dimensions/build_dim_patient.py` : Construit dim_patient

## Utilisation

### Via Airflow (recommandé)

Deux DAGs disponibles:

1. **chu_pipeline_pyspark_jobs** (monolithique complet)
   - Exécute tous les jobs d'un coup
   - Bronze → Silver → Gold → Benchmarks
   - Bon pour run complet nightly

2. **chu_pipeline_split** (split par tâche)
   - Exécute chaque tâche individuellement
   - Parallélisation maximale
   - Retry ciblé par tâche
   - Bon pour développement et debugging

### Via Spark Submit (manuel)

```bash
# Job monolithique
spark-submit \
  --master spark://chu-spark-master:7077 \
  --driver-memory 8g \
  --executor-memory 8g \
  /opt/spark-apps/01_extract_bronze.py --postgres-table Patient

# Job modulaire
spark-submit \
  --master spark://chu-spark-master:7077 \
  --driver-memory 8g \
  --executor-memory 8g \
  /opt/spark-apps/bronze/extract_postgres.py Patient
```

### Via Python (développement)

```bash
# Depuis le container Airflow ou Jupyter
export SPARK_MASTER_URL=spark://chu-spark-master:7077
export DATA_BASE=/opt/spark-data
export DATA_DIR=/data/DATA_2024
export SPARK_DRIVER_MEMORY=8g
export SPARK_EXECUTOR_MEMORY=8g

python /opt/spark-apps/bronze/extract_postgres.py Patient
```

## Configuration

### Variables d'Environnement

- `SPARK_MASTER_URL` : URL du master Spark (default: local[*])
- `DATA_BASE` : Répertoire de base des données (default: /opt/spark-data)
- `DATA_DIR` : Répertoire des données sources (default: /data/DATA_2024)
- `SPARK_DRIVER_MEMORY` : Mémoire driver (default: 8g)
- `SPARK_EXECUTOR_MEMORY` : Mémoire executor (default: 8g)
- `SPARK_APP_NAME` : Nom de l'application Spark

### Chemins de Données

- Bronze: `${DATA_BASE}/bronze/{postgres,csv}/`
- Silver: `${DATA_BASE}/silver/`
- Gold: `${DATA_BASE}/gold/`

## Développement

Pour créer un nouveau job modulaire:

1. Créer le fichier dans le bon répertoire
2. Importer `common.spark_utils`
3. Utiliser les fonctions communes
4. Ajouter le job au DAG Airflow correspondant

Exemple:

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.spark_utils import get_spark_session, get_paths, logger

def my_job():
    spark = get_spark_session("My-Job")
    paths = get_paths()

    # Your logic here

    spark.stop()
    return 0

if __name__ == "__main__":
    sys.exit(my_job())
```

## Performance

Avec 32G RAM disponible:
- Driver Memory: 8G
- Executor Memory: 8G
- Worker Cores: 2
- Parallélisation recommandée: 4-6 jobs simultanés max

## Notes

- Les jobs monolithiques sont conservés pour compatibilité
- Migrer progressivement vers les jobs modulaires
- Les jobs modulaires sont plus faciles à maintenir et débugger
