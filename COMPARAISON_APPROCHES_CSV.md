# 🔄 COMPARAISON : Notre approche vs Code de ton collègue

**Date** : 21 Octobre 2025

---

## 📋 TON COLLÈGUE T'A ENVOYÉ QUOI ?

Ton collègue t'a envoyé un script Python qui traite **PostgreSQL** avec un système de **batching** (découpage en morceaux).

**Son code** :
```python
def process_source_batch(spark, config):
    if source_type == "postgres":
        # Obtenir le nombre total de lignes
        total_rows = get_table_count(spark, source_path)

        if total_rows > BATCH_SIZE:  # BATCH_SIZE = 1M
            # Traiter par batch de 1M lignes
            for batch_num in range(num_batches):
                df_batch = read_postgres_batch(spark, source_path, offset, BATCH_SIZE)
                df_processed = process_dataframe(df_batch, config)
                write_batch_to_minio(df_processed, output_table, batch_num)
```

**Ce que ça fait** :
- Lit PostgreSQL par morceaux de 1M lignes
- Évite de charger toute la table en mémoire d'un coup
- Écrit chaque morceau dans MinIO

---

## ❓ POURQUOI SON CODE NE S'APPLIQUE PAS À TOI ?

### Différence 1 : Source de données

| Ton collègue | Toi |
|--------------|-----|
| Lit **PostgreSQL** (table `deces`) | Lis **CSV** (`deces.csv`) |
| Problème: Table trop grosse en PostgreSQL | Problème: CSV trop gros (25M lignes) |

➡️ **Son code traite PostgreSQL, pas CSV direct !**

---

### Différence 2 : Approche

**Ton collègue** :
```
CSV → PostgreSQL (chargé avant) → Spark (par batch) → Bronze
```

**Toi (meilleure approche)** :
```
CSV → Spark (direct) → Bronze
```

➡️ **Tu lis directement le CSV, pas via PostgreSQL !**

---

## 🎯 POURQUOI NOTRE APPROCHE EST MEILLEURE ?

### 1. **Pas besoin de PostgreSQL intermédiaire**

**Code ton collègue** (2 étapes) :
```python
# Étape 1 : Charger CSV dans PostgreSQL (non montré dans son code)
# COPY deces FROM 'deces.csv' ...

# Étape 2 : Lire PostgreSQL par batch
df_batch = read_postgres_batch(spark, "deces", offset, 1000000)
```

**Notre approche** (1 étape) :
```python
# Lecture CSV directe
df = spark.read.csv("deces.csv")
```

➡️ **Pas besoin de PostgreSQL = plus simple et plus rapide**

---

### 2. **Spark gère déjà le "batching" automatiquement**

**Code ton collègue** (batching manuel) :
```python
# Découpe manuelle en morceaux
for batch_num in range(num_batches):
    offset = batch_num * 1000000
    df_batch = read_postgres_batch(spark, table, offset, 1000000)
```

**Notre approche** (batching automatique Spark) :
```python
# Spark découpe automatiquement en partitions
df = spark.read.csv("deces.csv")
df = df.repartition(20)  # 25M ÷ 20 = 1.25M par partition

# Spark traite chaque partition en parallèle automatiquement
```

➡️ **Spark fait le batching tout seul = moins de code**

---

### 3. **CSV → Parquet plus efficace que PostgreSQL → Parquet**

**Code ton collègue** :
```
CSV (3 GB)
  → PostgreSQL (index + overhead = 5 GB)
  → Spark read JDBC (lent)
  → Parquet (300 MB)
```

**Notre approche** :
```
CSV (3 GB)
  → Spark read CSV (rapide)
  → Parquet (300 MB)
```

➡️ **Moins d'étapes = plus rapide**

---

## 📊 COMPARAISON DÉTAILLÉE

| Aspect | Code ton collègue | Notre approche |
|--------|-------------------|----------------|
| **Source** | PostgreSQL | CSV direct |
| **Étape intermédiaire** | PostgreSQL | Aucune |
| **Batching** | Manuel (boucle for) | Automatique (Spark) |
| **Complexité** | ~200 lignes | ~30 lignes |
| **Performance** | Moyenne (JDBC lent) | Rapide (CSV natif) |
| **Gestion mémoire** | Manuelle | Automatique |
| **Crash risqué ?** | Non (batching manuel) | Non (Spark gère) |

---

## 🤔 QUAND UTILISER L'APPROCHE DE TON COLLÈGUE ?

### ✅ Son code est utile si :

1. **Les données sont DÉJÀ dans PostgreSQL**
   ```
   # Si tu as déjà chargé deces.csv dans PostgreSQL
   # Et que tu ne peux pas accéder au CSV original
   ```

2. **Table PostgreSQL énorme (100M+ lignes)**
   ```
   # Batching manuel peut aider si Spark galère
   ```

3. **Mémoire très limitée (< 4 GB)**
   ```
   # Batching manuel donne plus de contrôle
   ```

---

### ❌ Son code N'est PAS utile si :

1. **Tu as accès au CSV original** ✅ (ton cas)
   ```
   # Pourquoi passer par PostgreSQL ?
   ```

2. **Tu as 8 GB+ de mémoire** ✅ (ton cas)
   ```
   # Spark peut gérer 25M lignes sans batching manuel
   ```

3. **Tu veux un pipeline simple** ✅ (ton cas)
   ```
   # Moins de code = moins de bugs
   ```

---

## 🚀 NOTRE SOLUTION FINALE (OPTIMALE)

### Notebook 01 - Cellule 11 (modifiée)

```python
# 3. DÉCÈS COMPLET (SANS FILTRAGE - CSV BRUT INTÉGRAL)
df_deces_full = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .option("mode", "PERMISSIVE") \
    .csv(f"{DATA_DIR}/DECES EN FRANCE/deces.csv")

# Repartitionner pour optimiser (équivalent du batching automatique)
df_deces_full = df_deces_full.repartition(20)

# Ajout métadonnées
df_with_meta = df_deces_full \
    .withColumn("ingestion_timestamp", current_timestamp()) \
    .withColumn("ingestion_date", lit(datetime.now().strftime("%Y-%m-%d")))

# Sauvegarde en Bronze (compression automatique)
output_path = f"{OUTPUT_BASE}/csv/deces"
df_with_meta.write \
    .mode("overwrite") \
    .option("compression", "snappy") \
    .parquet(output_path)

print(f"✅ deces COMPLET OK ({row_count:,} lignes)")
```

---

## 🎓 CE QUE TU RETIENS

### 1. **CSV direct > PostgreSQL intermédiaire**

```python
# ❌ MAUVAIS (2 étapes)
CSV → PostgreSQL → Spark → Parquet

# ✅ BON (1 étape)
CSV → Spark → Parquet
```

---

### 2. **Spark gère le batching automatiquement**

```python
# ❌ MAUVAIS (batching manuel)
for batch in batches:
    df = read_batch(offset, limit)

# ✅ BON (Spark gère)
df = spark.read.csv("file.csv")
df = df.repartition(20)  # Spark découpe automatiquement
```

---

### 3. **Bronze = TOUT garder (pas de filtrage)**

```python
# ❌ MAUVAIS (filtrage dans Bronze)
df_2019 = df.filter(year(col("date")) == 2019)

# ✅ BON (Bronze brut complet)
df_all = df  # TOUTES les années
# Filtrage dans Silver/Gold
```

---

### 4. **Optimisations Spark suffisent**

```python
# Configuration déjà optimale :
.config("spark.driver.memory", "8g")               # ✅
.config("spark.executor.memory", "8g")             # ✅
.config("spark.sql.adaptive.enabled", "true")      # ✅
.option("compression", "snappy")                   # ✅
.repartition(20)                                   # ✅
```

---

## ✅ RÉSUMÉ

### Code de ton collègue :
- ✅ Bon pour PostgreSQL
- ✅ Bon pour batching manuel
- ❌ Pas nécessaire pour CSV direct
- ❌ Plus complexe que nécessaire

### Notre approche :
- ✅ CSV direct (pas de PostgreSQL)
- ✅ Batching automatique Spark
- ✅ Plus simple (30 lignes vs 200)
- ✅ Plus rapide (1 étape vs 2)
- ✅ Conforme Data Lake

---

**Conclusion** : Ton collègue avait un problème PostgreSQL, toi tu as un problème CSV. **Notre solution est mieux adaptée à ton cas.** ✅
