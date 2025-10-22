# 🔧 CORRECTIONS FINALES - Pipeline Complet

**Date** : 22 Octobre 2025

---

## ✅ PROBLÈMES RÉSOLUS

### 1. Ajout departements-francais.csv ✅
- Copié dans `/DATA_2024/departements-francais.csv`
- Ajouté cellule dans Notebook 01 pour extraction

### 2. Données déplacées vers lakehouse ✅
- **Annulé** : Remettre dans `/home/jovyan/data/`
- Raison : Les notebooks pointent vers `/home/jovyan/data/`, pas `/home/jovyan/data/lakehouse/`

---

## ❌ PROBLÈMES À CORRIGER

### 1. Notebook 04 - Erreur `categorie` manquante

**Erreur** :
```
AnalysisException: A column or function parameter with name `d`.`categorie` cannot be resolved.
Did you mean one of the following? [`d`.`code_diag`]
```

**Cause** :
La table `dim_diagnostic` n'a que 2 colonnes :
- `code_diag`
- `libelle`

Mais la requête SQL utilise `d.categorie` qui n'existe pas.

**Solution** :
Ajouter une colonne `categorie` dans `dim_diagnostic` en extrayant la première lettre du code :
```python
# Dans Notebook 03, cellule dim_diagnostic
dim_diagnostic = df_diagnostic_silver.select(
    col("Code_diag").alias("code_diag"),
    col("Diagnostic").alias("libelle"),
    # Ajouter catégorie (première lettre du code)
    col("Code_diag").substr(1, 1).alias("categorie")
).dropDuplicates(["code_diag"])
```

**Catégories CIM-10** :
- A : Maladies infectieuses
- B : Maladies infectieuses (suite)
- C : Tumeurs malignes
- D : Tumeurs bénignes
- E : Maladies endocriniennes
- F : Troubles mentaux
- G : Maladies du système nerveux
- etc.

---

### 2. Notebook 03 - Enrichir dim_etablissement avec départements

**Objectif** :
Ajouter les colonnes région/département à `dim_etablissement` via jointure avec `departements`.

**Solution** :
```python
# Lire départements depuis Bronze
df_dept = spark.read.parquet(f"{SILVER_BASE}/../bronze/csv/departements")

# Extraire code département depuis code postal (2 premiers chiffres)
from pyspark.sql.functions import substring

dim_etablissement = dim_etablissement.withColumn(
    "code_departement",
    substring(col("code_postal"), 1, 2)
)

# Jointure avec départements
dim_etablissement_enrichi = dim_etablissement.join(
    df_dept.select(
        col("num_departement"),
        col("libelle_departement"),
        col("libelle_region"),
        col("abv_region")
    ),
    dim_etablissement["code_departement"] == df_dept["num_departement"],
    "left"
)
```

---

## 🚀 PLAN D'ACTION

### Étape 1 : Fix Notebook 03 (dim_diagnostic + categorie)

**Modifier cellule 6** (dim_diagnostic) :
```python
dim_diagnostic = df_diagnostic_silver.select(
    col("Code_diag").alias("code_diag"),
    col("Diagnostic").alias("libelle"),
    col("Code_diag").substr(1, 1).alias("categorie")  # ← AJOUT
).dropDuplicates(["code_diag"])
```

---

### Étape 2 : Fix Notebook 03 (dim_etablissement + départements)

**Modifier cellule 8** (dim_etablissement) :
```python
# Lire établissements
df_etab_silver = spark.read.parquet(f"{SILVER_BASE}/etablissement_sante")

# Lire départements depuis Bronze
df_dept = spark.read.parquet("/home/jovyan/data/bronze/csv/departements")

# Extraire code département
from pyspark.sql.functions import substring

dim_etablissement = df_etab_silver.select(
    col("finess_site").alias("finess"),
    col("siret_site").alias("siret"),
    col("raison_sociale").alias("nom"),
    col("commune").alias("ville"),
    col("code_postal"),
    col("telephone"),
    col("email"),
    substring(col("code_postal"), 1, 2).alias("code_departement")  # ← AJOUT
).filter(
    col("finess").isNotNull()
).dropDuplicates(["finess"])

# Enrichir avec région/département
dim_etablissement = dim_etablissement.join(
    df_dept.select(
        col("num_departement"),
        col("libelle_departement"),
        col("libelle_region"),
        col("abv_region")
    ),
    dim_etablissement["code_departement"] == df_dept["num_departement"],
    "left"
)

print(f"✅ {dim_etablissement.count():,} établissements (enrichis avec régions)")
dim_etablissement.show(5, truncate=False)

dim_etablissement.write \
    .mode("overwrite") \
    .parquet(f"{GOLD_OUTPUT}/dim_etablissement")
```

---

### Étape 3 : Relancer les notebooks dans l'ordre

```bash
# Dans Jupyter (http://localhost:8888)

# 1. Notebook 01 (avec départements)
# Cell → Run All
# Résultat attendu : 17 tables (16 + departements)

# 2. Notebook 02 (Silver)
# Cell → Run All
# Résultat attendu : 12 tables Silver

# 3. Notebook 03 (Gold - MODIFIÉ)
# Cell → Run All
# Résultat attendu :
#   - dim_diagnostic avec 3 colonnes (code_diag, libelle, categorie)
#   - dim_etablissement avec 12 colonnes (+ région/département)

# 4. Notebook 04 (Benchmarks)
# Cell → Run All
# Résultat attendu : Benchmarks sans erreur
```

---

## ✅ RÉSULTAT ATTENDU

### Gold Layer final

| Table | Lignes | Colonnes | Ajouts |
|-------|--------|----------|--------|
| dim_temps | 4,748 | 9 | - |
| dim_patient | 100,000 | 10 | - |
| **dim_diagnostic** | 15,490 | **3** | **+ categorie** ✅ |
| dim_professionnel | 1,048,575 | 5 | - |
| **dim_etablissement** | 416,000 | **12** | **+ région/département** ✅ |
| fait_consultation | 1,027,157 | 13 | - |
| fait_deces | 620,625 | 15 | - |
| fait_satisfaction | 8 | 16 | - |

---

## 🎯 NOUVELLES ANALYSES POSSIBLES

### 1. Top diagnostics par catégorie

```sql
SELECT
    d.categorie,
    COUNT(*) as nb_consultations
FROM fait_consultation f
JOIN dim_diagnostic d ON f.code_diag = d.code_diag
WHERE d.categorie IS NOT NULL
GROUP BY d.categorie
ORDER BY nb_consultations DESC
```

### 2. Consultations par région

```sql
SELECT
    e.libelle_region,
    COUNT(*) as nb_consultations
FROM fait_consultation f
JOIN dim_etablissement e ON f.finess = e.finess
GROUP BY e.libelle_region
ORDER BY nb_consultations DESC
```

### 3. Satisfaction par département

```sql
SELECT
    e.libelle_departement,
    AVG(s.score_global) as score_moyen
FROM fait_satisfaction s
JOIN dim_etablissement e ON s.finess = e.finess
WHERE e.libelle_departement IS NOT NULL
GROUP BY e.libelle_departement
ORDER BY score_moyen DESC
```

---

**Prêt à appliquer les corrections !**
