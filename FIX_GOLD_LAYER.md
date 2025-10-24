# Fix Gold Layer - Erreurs TypeError

Date: 24 octobre 2025

## Problème: TypeError 'int' object is not callable

### Symptôme
```python
TypeError: 'int' object is not callable
```

Erreur dans:
- Notebook `03_Transform_Gold_STAR_SCHEMA.ipynb`
- Script `03_transform_gold.py`
- DAGs Airflow (`chu_pipeline_split`, `chu_pipeline_pyspark_jobs`)

### Cause Racine

**Conflit de noms de variables avec les fonctions PySpark.**

Quand tu importes :
```python
from pyspark.sql.functions import count, min, max, avg
```

Et que tu fais :
```python
count = df.count()  # count devient un integer
```

Ensuite, quand tu essaies d'utiliser `count()` comme fonction:
```python
.agg(count("*"))  # ERREUR: count est maintenant un int, pas une fonction
```

### Solutions Appliquées

#### 1. Notebook 03 - Utiliser l'alias F

**AVANT**:
```python
from pyspark.sql.functions import (
    col, count, countDistinct, min, max, sum, avg,
    year, month, dayofmonth, date_format
)

# Plus tard dans le code
count("*")  # ERREUR si count a été écrasé
```

**APRÈS**:
```python
from pyspark.sql import functions as F

# Dans tout le code
F.count("*")
F.min("date")
F.max("date")
F.avg("score")
```

**Fichier corrigé**: Tous les usages dans le notebook ont été remplacés par `F.function_name`

#### 2. Script 03_transform_gold.py - Utiliser des alias

**AVANT**:
```python
from pyspark.sql.functions import (
    col, count, countDistinct, min as spark_min, max as spark_max,
    year, month, dayofmonth, date_format, datediff,
    monotonically_increasing_id, lit, substring, to_date,
    lag, row_number, sum as spark_sum, concat_ws
)
```

**APRÈS**:
```python
from pyspark.sql.functions import (
    col, count, countDistinct,
    min as spark_min, max as spark_max, avg as spark_avg, sum as spark_sum,
    year, month, dayofmonth, date_format, datediff,
    monotonically_increasing_id, lit, substring, to_date,
    lag, row_number, concat_ws
)
```

#### 3. Permissions Gold Layer

**Problème secondaire**: Fichiers créés par root, non supprimables en mode overwrite.

**Solution**:
```bash
docker exec -u root chu_jupyter bash -c \
  "rm -rf /home/jovyan/data/gold/* && \
   chown -R jovyan:users /home/jovyan/data/gold"
```

## Tests de Validation

### Test 1: dim_temps

```bash
docker exec chu_airflow_webserver bash -c \
  "cd /opt/spark-apps && \
   PYSPARK_PYTHON=python3 PYSPARK_DRIVER_PYTHON=python3 \
   python 03_transform_gold.py --task dim_temps"
```

**Résultat**: ✅ SUCCESS
```
Created 4,748 days (2013-2025)
Saved dim_temps
Gold star schema creation completed successfully
```

### Test 2: Notebook 03

1. Ouvrir http://localhost:8888 (token: admin123)
2. Ouvrir `03_Transform_Gold_STAR_SCHEMA.ipynb`
3. Restart Kernel & Run All

**Résultat attendu**: ✅ Toutes les cellules s'exécutent sans TypeError

### Test 3: DAG chu_pipeline_split

```bash
# Via Airflow UI
http://localhost:8080
DAG: chu_pipeline_split
Trigger DAG
```

**Résultat attendu**: ✅ Task `gold_dimensions.dim_temps` passe en SUCCESS

## Bonnes Pratiques pour Éviter ce Problème

### ✅ Recommandé

**Option A: Utiliser l'alias F** (le plus propre)
```python
from pyspark.sql import functions as F

df.select(
    F.count("*").alias("total"),
    F.min("date").alias("date_min"),
    F.max("date").alias("date_max"),
    F.avg("score").alias("score_moyen")
)
```

**Option B: Aliases explicites**
```python
from pyspark.sql.functions import (
    count,
    min as fmin,
    max as fmax,
    avg as favg,
    sum as fsum
)

df.select(
    count("*").alias("total"),
    fmin("date").alias("date_min"),
    fmax("date").alias("date_max"),
    favg("score").alias("score_moyen")
)
```

### ❌ À Éviter

```python
from pyspark.sql.functions import count, min, max, avg

# Plus tard:
count = df.count()  # ERREUR: écrase la fonction count

# Ensuite:
df.select(count("*"))  # TypeError!
```

## Résumé des Fichiers Modifiés

| Fichier | Modification | Status |
|---------|--------------|--------|
| `jupyter/notebooks/03_Transform_Gold_STAR_SCHEMA.ipynb` | Import `F` + remplacement fonctions | ✅ |
| `spark/jobs/03_transform_gold.py` | Ajout alias `spark_avg` | ✅ |
| `/home/jovyan/data/gold/` | Nettoyage permissions | ✅ |

## Pour Aller Plus Loin

### Si tu veux régénérer toute la couche Gold proprement:

```bash
# 1. Nettoyer Gold
docker exec -u root chu_jupyter bash -c \
  "rm -rf /home/jovyan/data/gold/* && \
   chown -R jovyan:users /home/jovyan/data/gold"

# 2. Lancer le pipeline complet
# Option A: Notebook
http://localhost:8888
# Exécuter 03_Transform_Gold_STAR_SCHEMA.ipynb

# Option B: Airflow
http://localhost:8080
# Trigger DAG: chu_pipeline_split

# Option C: Script direct
docker exec chu_airflow_webserver bash -c \
  "cd /opt/spark-apps && \
   PYSPARK_PYTHON=python3 PYSPARK_DRIVER_PYTHON=python3 \
   python 03_transform_gold.py"  # Sans --task = ALL
```

## État Actuel

✅ **dim_temps**: Créé avec succès (4,748 lignes)
✅ **Permissions**: Corrigées pour jovyan
✅ **Notebook**: Imports corrigés avec F
✅ **Script**: Imports corrigés avec aliases
✅ **DAGs**: Variables Python ajoutées

**Prêt pour**: Exécuter tout le pipeline Gold sans erreurs

---

**Auteurs**: Nejma MOUALHI | Brieuc OLIVIERI | Nicolas TAING
**Date**: 24 octobre 2025
**Version**: 2.2 (fix TypeError + permissions Gold)
