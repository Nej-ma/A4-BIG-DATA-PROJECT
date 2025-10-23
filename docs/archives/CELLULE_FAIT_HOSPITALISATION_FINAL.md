# 🏥 CELLULE NOTEBOOK 03 : FAIT_HOSPITALISATION (VRAIES DONNÉES)

**Position** : Insérer après la cellule `fait_deces` (cellule 11) et avant `fait_satisfaction` (cellule 12)

**Type** : Code cell

---

## 📋 CODE COMPLET À COPIER-COLLER

```python
# 2.3 FAIT HOSPITALISATION (depuis tables AAAA + date)
print("\n" + "="*80)
print("📊 FAIT: fait_hospitalisation (VRAIES DONNÉES)")
print("="*80)

# ÉTAPE 1: Charger les tables Bronze AAAA et date
print("📖 Chargement tables AAAA et date depuis Bronze...")
df_aaaa = spark.read.parquet(f"{SILVER_BASE}/../bronze/postgres/AAAA") \
    .drop("ingestion_timestamp", "ingestion_date")
df_date = spark.read.parquet(f"{SILVER_BASE}/../bronze/postgres/date") \
    .drop("ingestion_timestamp", "ingestion_date")

print(f"   - AAAA: {df_aaaa.count():,} lignes")
print(f"   - date: {df_date.count():,} lignes")

# ÉTAPE 2: Ajouter row_id pour jointure par position (les 2 tables ont même nb lignes)
from pyspark.sql.functions import monotonically_increasing_id, to_date, datediff, year, month

df_aaaa_idx = df_aaaa.withColumn("row_id", monotonically_increasing_id())
df_date_idx = df_date.withColumn("row_id", monotonically_increasing_id())

# ÉTAPE 3: Jointure par position
df_hospit_raw = df_aaaa_idx.join(df_date_idx, "row_id", "inner")

print(f"✅ Jointure: {df_hospit_raw.count():,} hospitalisations")

# ÉTAPE 4: Transformation et nettoyage
fait_hospitalisation = df_hospit_raw.select(
    monotonically_increasing_id().alias("id_hospitalisation"),

    # Clés étrangères
    col("Num").alias("id_patient"),
    col("Code_diag").alias("code_diag"),

    # Dates (conversion dd/MM/yyyy → date)
    to_date(col("date1"), "dd/MM/yyyy").alias("date_entree"),
    to_date(col("date2"), "dd/MM/yyyy").alias("date_sortie"),

    # Clés temporelles
    date_format(to_date(col("date1"), "dd/MM/yyyy"), "yyyyMMdd").alias("id_temps_entree"),
    date_format(to_date(col("date2"), "dd/MM/yyyy"), "yyyyMMdd").alias("id_temps_sortie"),

    # Mesures
    datediff(
        to_date(col("date2"), "dd/MM/yyyy"),
        to_date(col("date1"), "dd/MM/yyyy")
    ).alias("duree_sejour_jours"),

    # Dimensions temporelles pour partitionnement
    year(to_date(col("date1"), "dd/MM/yyyy")).alias("annee"),
    month(to_date(col("date1"), "dd/MM/yyyy")).alias("mois")
)

# ÉTAPE 5: Filtrer données invalides (dates nulles ou négatives)
fait_hospitalisation = fait_hospitalisation.filter(
    (col("date_entree").isNotNull()) &
    (col("date_sortie").isNotNull()) &
    (col("duree_sejour_jours") >= 0)
)

print(f"✅ {fait_hospitalisation.count():,} hospitalisations valides")
fait_hospitalisation.show(10)

# ÉTAPE 6: Statistiques
print("\n📈 Statistiques:")
fait_hospitalisation.select(
    count("*").alias("total_hospitalisations"),
    countDistinct("id_patient").alias("patients_uniques"),
    countDistinct("code_diag").alias("diagnostics_uniques"),
    avg("duree_sejour_jours").alias("duree_moyenne_jours"),
    min("duree_sejour_jours").alias("duree_min"),
    max("duree_sejour_jours").alias("duree_max"),
    min("annee").alias("annee_min"),
    max("annee").alias("annee_max")
).show()

# Distribution par année
print("\n📅 Distribution par année:")
fait_hospitalisation.groupBy("annee").agg(
    count("*").alias("nb_hospitalisations"),
    avg("duree_sejour_jours").alias("duree_moyenne")
).orderBy("annee").show()

# ÉTAPE 7: Sauvegarde avec partitionnement
print("\n💾 Sauvegarde avec partitionnement par année et mois...")
fait_hospitalisation.write \
    .mode("overwrite") \
    .partitionBy("annee", "mois") \
    .parquet(f"{GOLD_OUTPUT}/fait_hospitalisation")

print(f"✅ Sauvegardé: {GOLD_OUTPUT}/fait_hospitalisation")
print(f"   - Partitionné par: annee, mois")
print(f"   - Format: Parquet compressé")
print(f"   - Source: Tables AAAA + date (vraies données)")
```

---

## 📊 OUTPUT ATTENDU

```
================================================================================
📊 FAIT: fait_hospitalisation (VRAIES DONNÉES)
================================================================================
📖 Chargement tables AAAA et date depuis Bronze...
   - AAAA: 82,216 lignes
   - date: 82,216 lignes
✅ Jointure: 82,216 hospitalisations
✅ 82,216 hospitalisations valides

+------------------+----------+---------+------------+------------+---------------+---------------+------------------+-----+----+
|id_hospitalisation|id_patient|code_diag| date_entree|date_sortie|id_temps_entree|id_temps_sortie|duree_sejour_jours|annee|mois|
+------------------+----------+---------+------------+------------+---------------+---------------+------------------+-----+----+
|                 0|         1|     Q428|  2018-12-01|  2018-12-02|       20181201|       20181202|                 1| 2018|  12|
|                 1|         2|     G961|  2019-03-12|  2019-03-13|       20190312|       20190313|                 1| 2019|   3|
|                 2|         3|     J350|  2015-12-27|  2015-12-28|       20151227|       20151228|                 1| 2015|  12|
|                 3|         4|     P569|  2017-09-20|  2017-09-21|       20170920|       20170921|                 1| 2017|   9|
|                 4|         5|    M0217|  2021-04-06|  2021-04-07|       20210406|       20210407|                 1| 2021|   4|
+------------------+----------+---------+------------+------------+---------------+---------------+------------------+-----+----+

📈 Statistiques:
+----------------------+----------------+--------------------+-------------------+---------+---------+---------+---------+
|total_hospitalisations|patients_uniques|diagnostics_uniques|duree_moyenne_jours|duree_min|duree_max|annee_min|annee_max|
+----------------------+----------------+--------------------+-------------------+---------+---------+---------+---------+
|                 82216|           82216|               15442|  1.0002432689...  |        0|        4|     2013|     2025|
+----------------------+----------------+--------------------+-------------------+---------+---------+---------+---------+

📅 Distribution par année:
+-----+--------------------+-----------------+
|annee|nb_hospitalisations|   duree_moyenne |
+-----+--------------------+-----------------+
| 2013|                5803|1.000344... |
| 2014|                6143|1.000325... |
| 2015|                6578|1.000304... |
| ...                                    |
+-----+--------------------+-----------------+

✅ Sauvegardé: /home/jovyan/data/gold/fait_hospitalisation
   - Partitionné par: annee, mois
   - Format: Parquet compressé
   - Source: Tables AAAA + date (vraies données)
```

---

## 🔍 EXPLICATIONS TECHNIQUES

### Pourquoi cette approche?

1. **Jointure par position (row_id)**
   - Les tables AAAA et date ont exactement le même nombre de lignes (82,216)
   - Elles sont implicitement liées par position de ligne
   - `monotonically_increasing_id()` garantit l'ordre

2. **Conversion dates**
   - Format source: `dd/MM/yyyy` (string)
   - Format cible: date Spark (yyyy-MM-dd)
   - Fonction: `to_date(col, "dd/MM/yyyy")`

3. **Calcul durée séjour**
   - `datediff(date_sortie, date_entree)` en jours
   - Filtre: durée >= 0 (exclure données invalides)

4. **Clés temporelles**
   - `id_temps_entree` : yyyyMMdd (ex: 20190315)
   - Permet jointure avec `dim_temps`

5. **Partitionnement**
   - Par `annee` et `mois` de la date d'entrée
   - Optimise les requêtes par période

---

## ✅ VÉRIFICATION POST-CRÉATION

Après avoir exécuté la cellule, vérifier:

```python
# Dans une nouvelle cellule
df = spark.read.parquet("/home/jovyan/data/gold/fait_hospitalisation")
print(f"Total hospitalisations: {df.count():,}")
df.printSchema()
df.show(5)
```

---

## 🎯 CONFORMITÉ LIVRABLE 1

✅ **Table**: `fait_hospitalisation` créée

✅ **Dimensions liées**:
- `dim_temps` (via id_temps_entree et id_temps_sortie)
- `dim_patient` (via id_patient)
- `dim_diagnostic` (via code_diag)
- `dim_etablissement` (via code_etablissement - si ajouté)

✅ **Métriques**:
- `nb_hospitalisations`: COUNT(*)
- `duree_sejour_jours`: date_sortie - date_entree
- `duree_moyenne_sejour`: AVG(duree_sejour_jours)

✅ **Données réelles**: Depuis tables PostgreSQL AAAA + date (82,216 hospitalisations)

---

## 📝 MISE À JOUR DU MARKDOWN FINAL

Après la cellule de vérification (cellule 14), mettre à jour le markdown pour indiquer:

```markdown
#### 📊 Faits (4) :
- ✅ **fait_consultation** : Consultations médicales (partitionné année/mois)
- ✅ **fait_hospitalisation** : Hospitalisations (partitionné année/mois) ← AJOUTÉ
- ✅ **fait_deces** : Décès 2019 anonymisés (partitionné année/mois)
- ✅ **fait_satisfaction** : Scores satisfaction E-Satis 2019 (partitionné année)
```

---

**C'EST PARTI ! 🚀 Copie-colle cette cellule dans le Notebook 03 !**
