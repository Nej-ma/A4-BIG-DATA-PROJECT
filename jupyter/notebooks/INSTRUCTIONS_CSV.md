# 🚀 Instructions pour l'ingestion CSV

## ✅ Configuration terminée

J'ai augmenté la mémoire Spark à **8GB** pour gérer les 25 millions de lignes de décès.

## 📓 Notebook à utiliser

**UTILISEZ** : `02_Ingestion_Bronze_CSV.ipynb` (l'original)

**Modifiez la cellule Spark** pour ajouter la config mémoire :

```python
# Configuration Spark AVEC MÉMOIRE
spark = SparkSession.builder \
    .appName("CHU_Bronze_CSV") \
    .config("spark.driver.memory", "8g") \
    .config("spark.executor.memory", "8g") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()
```

## ⚡ Si ça plante quand même

**Option 1** : Filtrer seulement 2019 pour les décès

Modifiez la config du fichier décès :

```python
"deces": {
    "path": "/home/jovyan/DATA_2024/DECES EN FRANCE/deces.csv",
    "sep": ",",
    "description": "Décès en France"
},
```

Devient :

```python
"deces_2019": {
    "path": "/home/jovyan/DATA_2024/DECES EN FRANCE/deces.csv",
    "sep": ",",
    "description": "Décès en France 2019",
    "filter_year": 2019  # Ajouter cette ligne
},
```

Et dans la fonction d'ingestion, ajoutez AVANT le `.count()` :

```python
# Filtrage par année si spécifié
if "filter_year" in config:
    year_filter = config["filter_year"]
    df = df.filter(year(to_date(col("date_deces"))) == year_filter)
```

**Option 2** : Utilisez `02_Ingestion_Bronze_CSV_OPTIMISE.ipynb`

Ce notebook a déjà tout configuré avec filtrage 2019.

## 💡 Recommandation

**Pour le Livrable 2**, vous n'avez PAS BESOIN de TOUS les décès.

Les besoins utilisateurs demandent :
- "Nombre de décès par localisation et année **2019**"

Donc filtrer seulement 2019 est **parfaitement acceptable** et même **recommandé** !

Ça réduit de 25M lignes à ~600K lignes (beaucoup plus raisonnable).

## 🎯 Ce qui est important

1. ✅ **Notebook 01** (PostgreSQL) - DÉJÀ FAIT
2. ⭐ **Notebook 03** (Gold Star Schema) - LE PLUS IMPORTANT
3. ⚡ **Notebook 04** (Benchmarks) - Pour démontrer les performances

Le notebook 02 (CSV) est un **bonus**, pas une obligation.
