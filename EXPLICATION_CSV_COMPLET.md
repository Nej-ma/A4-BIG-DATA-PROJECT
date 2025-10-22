# 📄 POURQUOI CHARGER LE CSV `deces.csv` EN ENTIER ?

**Date** : 21 Octobre 2025
**Question** : "Pourquoi on filtre pas deces? On peut pas prendre deces.csv en entier?"

---

## ✅ RÉPONSE : ON CHARGE MAINTENANT LE CSV COMPLET !

### 🔄 Changement appliqué dans Notebook 01

**Avant** :
```python
# Filtrage année 2019 uniquement
df_deces_2019 = df_deces_full.filter(year(to_date(col("date_deces"))) == 2019)
# Résultat : 620K lignes (97.5% de réduction ❌)
```

**Maintenant** :
```python
# Chargement INTÉGRAL (toutes les années)
df_deces_full = spark.read.csv(f"{DATA_DIR}/DECES EN FRANCE/deces.csv")
df_deces_full = df_deces_full.repartition(20)  # Optimisation
# Résultat : 25M lignes (100% des données ✅)
```

---

## 🎯 POURQUOI C'EST MIEUX ?

### 1. **Bronze = Données BRUTES (principe Data Lake)**

```
┌──────────────────────────────────────┐
│         BRONZE LAYER                 │
│  = "Raw Zone" (zone brute)           │
├──────────────────────────────────────┤
│  ✅ Tout garder tel quel             │
│  ❌ AUCUN filtrage                   │
│  ❌ AUCUNE transformation            │
└──────────────────────────────────────┘
```

**Définition officielle** (Databricks, AWS, Azure) :
> "Bronze layer contains raw data as-is from the source"

➡️ Si le CSV a 25M lignes, Bronze DOIT avoir 25M lignes.

---

### 2. **Éviter CSV → PostgreSQL** (c'était ta question)

**Mauvaise approche** :
```
CSV (25M lignes)
  → Charger dans PostgreSQL (CREATE TABLE + COPY)
  → Lire depuis PostgreSQL (JDBC)
  → Écrire dans Bronze
```

**Problèmes** :
- ❌ Étape inutile (CSV → PostgreSQL)
- ❌ PostgreSQL surchargé
- ❌ Plus lent (2 étapes au lieu de 1)

**Bonne approche** (actuelle) :
```
CSV (25M lignes)
  → Lire directement avec Spark
  → Écrire dans Bronze (Parquet compressé)
```

**Avantages** :
- ✅ 1 seule étape
- ✅ Spark optimisé pour CSV
- ✅ Plus rapide
- ✅ PostgreSQL reste pour données opérationnelles

---

### 3. **Flexibilité analyses futures**

**Si Bronze filtré (620K lignes 2019)** :
```python
# ❌ Impossible d'analyser 2020
# ❌ Impossible d'analyser tendance 2015-2024
# ❌ Impossible de comparer avant/après COVID
# ❌ Il faut RE-CHARGER le CSV source
```

**Si Bronze complet (25M lignes)** :
```python
# ✅ Analyse 2019
df_2019 = df.filter(year(col("date_deces")) == 2019)

# ✅ Analyse COVID 2020-2021
df_covid = df.filter(year(col("date_deces")).isin([2020, 2021]))

# ✅ Tendance décennale
df_decade = df.groupBy(year(col("date_deces"))).count()

# ✅ Pic canicule 2003
df_canicule = df.filter(
    (year(col("date_deces")) == 2003) & (month(col("date_deces")) == 8)
)
```

---

## 🚀 "MAIS 25M LIGNES, ÇA VA PAS CRASHER ?"

### ✅ NON, grâce à :

#### 1. **Parquet + Compression**
```
CSV brut : ~3 GB
Parquet Snappy : ~300 MB (10x plus compact ✅)
```

#### 2. **Spark = Lazy Evaluation**
```python
# Ceci ne charge PAS 25M lignes en mémoire :
df = spark.read.parquet("bronze/csv/deces/")

# Seul le filtrage charge en mémoire :
df_2019 = df.filter(year(col("date_deces")) == 2019)  # 620K seulement
```

#### 3. **Repartitionnement**
```python
df.repartition(20)  # 25M ÷ 20 = 1.25M par partition
```

Chaque partition = ~1.25M lignes = gérable.

#### 4. **Mémoire Spark augmentée**
```python
# Notebook 01, cellule 2
.config("spark.driver.memory", "8g")    # ✅
.config("spark.executor.memory", "8g")  # ✅
```

---

## 📊 COMPARAISON

| Aspect | Filtré (avant) | Complet (maintenant) |
|--------|----------------|----------------------|
| **Lignes Bronze** | 620K (2019) | 25M (toutes années) |
| **Stockage** | ~50 MB | ~300 MB |
| **Conforme Data Lake** | ❌ Non | ✅ Oui |
| **Analyses futures** | ❌ Limitées | ✅ Illimitées |
| **Performance** | ⚡ Très rapide | ⚡ Rapide |
| **Crash risqué ?** | Non | Non |

---

## 🎓 OÙ FAIRE LE FILTRAGE ALORS ?

### ❌ PAS dans Bronze (layer brut)

```python
# ❌ MAUVAIS
# Bronze doit rester brut
```

### ⚠️ POSSIBLE dans Silver (si besoin)

```python
# Notebook 02 - Silver
# Si vraiment besoin de limiter le volume
df_deces_recent = df_deces_bronze.filter(
    year(col("date_deces")) >= 2015  # Garder 2015-2024 seulement
)
```

### ✅ RECOMMANDÉ dans Gold (filtrage métier)

```python
# Notebook 03 - Gold
# Filtrage métier par année
fait_deces_2019 = df_deces_silver \
    .filter(year(col("date_deces")) == 2019) \
    .join(dim_temps, ...) \
    .select(...)
```

---

## 🔄 LE FLUX COMPLET

```
CSV deces.csv (25M lignes, toutes années)
         ↓
    ✅ NOTEBOOK 01 - Bronze
    • Lecture CSV INTÉGRAL (25M lignes)
    • AUCUN filtrage
    • Écriture Parquet compressé
         ↓
📦 BRONZE: bronze/csv/deces/ (25M lignes)
         ↓
    ✅ NOTEBOOK 02 - Silver
    • Anonymisation SHA-256
    • Formats dates
    • POSSIBILITÉ de filtrer (ex: >= 2015)
         ↓
📦 SILVER: silver/deces/ (25M ou moins selon filtrage)
         ↓
    ✅ NOTEBOOK 03 - Gold
    • Création fait_deces
    • Filtrage métier (2019)
    • Join avec dimensions
         ↓
⭐ GOLD: gold/fait_deces/ (620K lignes 2019 partitionné)
```

---

## ✅ RÉSUMÉ FINAL

### Ta question :
> "On peut pas prendre deces.csv en entier?"

### Ma réponse :
**✅ OUI, on DOIT prendre le CSV en entier !**

**Pourquoi ?**
1. ✅ Bronze = données brutes (principe Data Lake)
2. ✅ Flexibilité analyses futures
3. ✅ Performance OK (Parquet + Spark)
4. ✅ Pas besoin CSV → PostgreSQL
5. ✅ Filtrage dans Silver/Gold (pas Bronze)

**Changement appliqué** :
- ✅ Notebook 01, cellule 11 modifiée
- ✅ Charge maintenant 25M lignes (pas 620K)
- ✅ Optimisé avec repartitionnement

**Prochaine exécution** :
```bash
# Jupyter (http://localhost:8888)
# Exécuter Notebook 01
# Résultat : 25M lignes dans bronze/csv/deces/
```

---

**Conclusion** : ✅ **CSV complet = meilleure pratique Data Lake**
