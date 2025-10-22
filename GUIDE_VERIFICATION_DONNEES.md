# 🔍 GUIDE - Comment vérifier que les données existent ?

**Date** : 22 Octobre 2025
**Problème** : MinIO Console affiche "This location is empty" alors que les notebooks se sont exécutés avec succès

---

## ❓ POURQUOI MINIO CONSOLE EST VIDE ?

### Problème architectural

**Les notebooks écrivent dans le système de fichiers** :
```
Jupyter → /home/jovyan/data/bronze/ → ./spark/data/bronze/ (host)
```

**MinIO lit depuis son volume monté** :
```
MinIO → /data/ → ./spark/data/ (host)
```

**MinIO Console affiche seulement** :
- Les objets uploadés via l'API S3
- **PAS** les fichiers qui existent sur le disque

➡️ **C'est normal que MinIO Console soit vide !**

---

## ✅ COMMENT VÉRIFIER QUE LES DONNÉES EXISTENT ?

### Méthode 1 : Vérifier sur le disque local (PLUS SIMPLE)

```bash
# Lister les données Bronze
ls ./spark/data/bronze/

# Résultat attendu :
csv/
postgres/

# Vérifier CSV
ls ./spark/data/bronze/csv/

# Résultat attendu :
deces/
deces_2019/
etablissement_sante/
satisfaction_esatis48h_2019/

# Vérifier taille des données
du -sh ./spark/data/bronze/
du -sh ./spark/data/silver/
du -sh ./spark/data/gold/
```

**Sur Windows (PowerShell)** :
```powershell
# Lister les données
dir "C:\Users\littl\Desktop\Big DATA\projet_git\spark\data\bronze"

# Taille des données
(Get-ChildItem -Path ".\spark\data\bronze" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
```

---

### Méthode 2 : Vérifier depuis le container Jupyter

```bash
# Se connecter à Jupyter
docker exec -it chu_jupyter bash

# Lister les données
ls -lh /home/jovyan/data/bronze/
ls -lh /home/jovyan/data/silver/
ls -lh /home/jovyan/data/gold/

# Vérifier taille
du -sh /home/jovyan/data/bronze/
du -sh /home/jovyan/data/silver/
du -sh /home/jovyan/data/gold/
```

---

### Méthode 3 : Vérifier depuis le container MinIO

```bash
# Se connecter à MinIO
docker exec -it chu_minio sh

# Lister les données
ls -lh /data/bronze/
ls -lh /data/silver/
ls -lh /data/gold/

# Compter les fichiers Parquet
find /data/bronze -name "*.parquet" | wc -l
find /data/silver -name "*.parquet" | wc -l
find /data/gold -name "*.parquet" | wc -l
```

---

### Méthode 4 : Vérifier avec Spark (MEILLEURE MÉTHODE)

**Dans Jupyter Notebook** :

```python
# Lire les données Bronze
df_bronze = spark.read.parquet("/home/jovyan/data/bronze/csv/etablissement_sante")
print(f"Établissements en Bronze : {df_bronze.count():,} lignes")
df_bronze.show(5)

# Lire les données Silver
df_silver = spark.read.parquet("/home/jovyan/data/silver/etablissement_sante")
print(f"Établissements en Silver : {df_silver.count():,} lignes")

# Lire les données Gold
df_gold = spark.read.parquet("/home/jovyan/data/gold/dim_etablissement")
print(f"Dimension Établissement : {df_gold.count():,} lignes")
```

---

## 📊 RÉSULTATS ATTENDUS

### Bronze layer

```bash
$ du -sh ./spark/data/bronze/
~500 MB

$ find ./spark/data/bronze -name "*.parquet" | wc -l
~200 fichiers
```

**Contenu** :
- `bronze/postgres/` : 13 tables PostgreSQL
- `bronze/csv/` : 3 fichiers CSV convertis

---

### Silver layer

```bash
$ du -sh ./spark/data/silver/
~450 MB

$ find ./spark/data/silver -name "*.parquet" | wc -l
~150 fichiers
```

**Contenu** :
- 12 tables nettoyées et anonymisées

---

### Gold layer

```bash
$ du -sh ./spark/data/gold/
~200 MB

$ find ./spark/data/gold -name "*.parquet" | wc -l
~100 fichiers
```

**Contenu** :
- 5 dimensions
- 3 faits (partitionnés par année/mois)

---

## 🔧 SI LES DONNÉES N'EXISTENT PAS

### Vérifier que les notebooks se sont bien exécutés

```python
# Dans chaque notebook, vérifier la dernière cellule

# Notebook 01 - Doit afficher :
✅ Tables extraites: 16/16
📊 Total lignes: ~29M

# Notebook 02 - Doit afficher :
✅ Silver layer : 12 tables
📊 Total lignes: ~29M

# Notebook 03 - Doit afficher :
✅ Gold layer : 8 tables
📊 Total lignes: ~2.8M
```

---

### Vérifier les logs Spark

```python
# Dans Jupyter Notebook
# Cellule après l'écriture Parquet

# Si erreur, Spark affiche :
❌ ERROR: ...

# Si succès, Spark affiche :
💾 Sauvegardé: /home/jovyan/data/bronze/...
⏱️  Temps: X.XXs
✅ [table] OK
```

---

## 🎯 UTILISER LE FICHIER departements-francais.csv

### 1. Ajouter à Notebook 01 (Extract Bronze)

```python
# PARTIE 2 : Extract CSV
# Ajouter après satisfaction et deces

# 4. DÉPARTEMENTS FRANÇAIS
result = ingest_csv_file(
    name="departements",
    file_path="/home/jovyan/departements-francais.csv",
    separator=";"
)
results.append(result)
```

---

### 2. Utiliser dans Notebook 03 (Gold - Enrichissement géographique)

```python
# Enrichir dim_etablissement avec région/département

# Lire départements
df_departements = spark.read.parquet("/home/jovyan/data/bronze/csv/departements")

# Enrichir établissements
df_etablissement_enrichi = df_etablissement.join(
    df_departements,
    df_etablissement["code_departement"] == df_departements["num_departement"],
    "left"
).select(
    "id_etablissement",
    "nom_etablissement",
    "commune",
    "num_departement",
    "libelle_departement",  # ← Nom du département
    "libelle_region",        # ← Nom de la région
    "abv_region"             # ← Abréviation région (ARA, BFC, etc.)
)

# Sauvegarder
df_etablissement_enrichi.write \
    .mode("overwrite") \
    .parquet("/home/jovyan/data/gold/dim_etablissement")

print(f"✅ dim_etablissement enrichie avec régions/départements")
```

---

## 📊 EXEMPLE : Analyses géographiques possibles

### 1. Consultations par région

```python
# Dans Notebook 03 ou 04
fait_consultation.join(dim_etablissement, "id_etablissement") \
    .groupBy("libelle_region") \
    .count() \
    .orderBy("count", ascending=False) \
    .show()

# Résultat :
+------------------------+--------+
|      libelle_region    |  count |
+------------------------+--------+
| Île-de-France          | 250000 |
| Auvergne-Rhône-Alpes   | 180000 |
| Provence-Alpes-Côte... | 150000 |
+------------------------+--------+
```

---

### 2. Décès par département

```python
# Joindre deces avec établissements (via commune)
fait_deces.join(dim_etablissement, "commune") \
    .groupBy("libelle_departement") \
    .count() \
    .orderBy("count", ascending=False) \
    .show(10)
```

---

### 3. Satisfaction par région

```python
# Moyenne satisfaction par région
fait_satisfaction.join(dim_etablissement, "id_etablissement") \
    .groupBy("libelle_region") \
    .agg(avg("score_satisfaction").alias("satisfaction_moyenne")) \
    .orderBy("satisfaction_moyenne", ascending=False) \
    .show()
```

---

## ✅ CHECKLIST FINALE

- [ ] Vérifier que `./spark/data/bronze/` contient des dossiers
- [ ] Vérifier que `./spark/data/silver/` contient des dossiers
- [ ] Vérifier que `./spark/data/gold/` contient des dossiers
- [ ] Vérifier la taille des données (Bronze ~500MB, Silver ~450MB, Gold ~200MB)
- [ ] Compter les fichiers Parquet (Bronze ~200, Silver ~150, Gold ~100)
- [ ] Tester la lecture avec Spark dans Jupyter
- [ ] Ajouter `departements-francais.csv` au pipeline
- [ ] Enrichir `dim_etablissement` avec régions/départements

---

## 🎯 CONCLUSION

### MinIO Console vide = NORMAL

Les notebooks écrivent dans le **système de fichiers local** (`/home/jovyan/data/`), pas via l'**API S3 de MinIO**.

➡️ **C'est un choix d'architecture** : plus simple et plus rapide pour le développement.

---

### Comment vérifier que ça marche ?

**✅ MÉTHODE RECOMMANDÉE** :

```python
# Dans Jupyter Notebook
# Cellule de test

# Lire Bronze
df = spark.read.parquet("/home/jovyan/data/bronze/csv/etablissement_sante")
print(f"✅ Bronze OK : {df.count():,} lignes")

# Lire Silver
df = spark.read.parquet("/home/jovyan/data/silver/etablissement_sante")
print(f"✅ Silver OK : {df.count():,} lignes")

# Lire Gold
df = spark.read.parquet("/home/jovyan/data/gold/dim_etablissement")
print(f"✅ Gold OK : {df.count():,} lignes")
```

**Si ces 3 lignes s'affichent, tes données sont bien là !** ✅

---

**Pour le département enrichment, veux-tu que je modifie les notebooks pour ajouter `departements-francais.csv` ?**
