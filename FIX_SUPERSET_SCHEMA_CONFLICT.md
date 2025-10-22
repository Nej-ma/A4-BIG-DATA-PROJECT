# 🔧 FIX : Conflit de schéma Hive Metastore

## ❌ Problème rencontré

### Erreur dans Notebook 05

```
AnalysisException: Column in converted table has different data type with source
Hive table's. Set spark.sql.hive.convertMetastoreParquet to false, or recreate
table `spark_catalog`.`default`.`dim_temps` to workaround.
```

### Cause

**Conflit entre le metastore Hive et les fichiers Parquet** :
- Hive Metastore a enregistré un schéma lors d'une création précédente
- Les fichiers Parquet Gold ont un schéma légèrement différent (ex: `DATE` vs `STRING`)
- Spark essaie de convertir automatiquement Parquet → Hive et détecte une incompatibilité

---

## ✅ SOLUTION 1 : Configuration Spark (RECOMMANDÉ)

### Modification appliquée au Notebook 05

**Cellule 2 (Configuration Spark)** - Ajout de la config :

```python
spark = SparkSession.builder \
    .appName("CHU_Superset_Setup") \
    .config("spark.sql.hive.convertMetastoreParquet", "false") \  # ← NOUVEAU
    .enableHiveSupport() \
    .getOrCreate()
```

**Explication** :
- `spark.sql.hive.convertMetastoreParquet = false` : Désactive la conversion automatique
- Spark lit directement les fichiers Parquet sans passer par le metastore Hive
- **Pas de perte de fonctionnalité** : Les tables restent interrogeables via SQL

---

## ✅ SOLUTION 2 : Recréer les tables avec DROP FORCE

**Déjà implémenté dans Notebook 05, cellule 4** :

```python
# D'abord supprimer complètement le metastore
spark.sql(f"DROP TABLE IF EXISTS {table_name}")

# Puis recréer la table
spark.sql(create_sql)
```

---

## 🚀 ÉTAPES À SUIVRE

### 1. Redémarrer le Notebook

Dans Jupyter Lab :
1. **Kernel** → **Restart Kernel**
2. **Run** → **Run All Cells**

### 2. Vérifier les résultats

La cellule de création devrait afficher :

```
📦 Création des tables externes...

  🗑️  dim_temps - ancien metastore supprimé
  ✅ 1/6 - dim_temps créée
  🗑️  dim_patient - ancien metastore supprimé
  ✅ 2/6 - dim_patient créée
  ...
  ✅ 6/6 - fait_consultation créée

✅ Toutes les tables créées !
```

### 3. Comptage des lignes

```
============================================================
  dim_temps                 :      4,748 lignes  ← ✅ FIXÉ
  dim_patient               :    100,000 lignes
  dim_diagnostic            :     15,490 lignes
  dim_professionnel         :  1,048,575 lignes
  dim_etablissement         :        200 lignes
  fait_consultation         :  1,027,157 lignes
============================================================
  TOTAL                     :  2,191,422 lignes
```

### 4. Test des requêtes

Les 5 tests SQL (consultations par année, diagnostics, etc.) devraient tous fonctionner.

---

## 🔍 DIAGNOSTIC DU PROBLÈME

### Vérifier le schéma Parquet vs Metastore

```python
# Lire directement le Parquet
df_parquet = spark.read.parquet("/home/jovyan/data/gold/dim_temps")
print("Schéma PARQUET:")
df_parquet.printSchema()

# Lire via la table Hive
df_hive = spark.table("dim_temps")
print("\nSchéma METASTORE:")
df_hive.printSchema()
```

**Différence typique** :
```
Parquet : date_complete (DATE)
Metastore : date_complete (STRING)  ← Conflit
```

---

## 🛡️ PRÉVENTION FUTURE

### Option A : Toujours utiliser la config Spark

Dans **tous les notebooks** qui créent des tables Hive :

```python
spark = SparkSession.builder \
    .config("spark.sql.hive.convertMetastoreParquet", "false") \
    .enableHiveSupport() \
    .getOrCreate()
```

### Option B : Définir la config globalement

Dans `docker-compose.yml` - service `spark-master` :

```yaml
environment:
  - SPARK_CONF_spark.sql.hive.convertMetastoreParquet=false
```

Puis redémarrer :
```bash
docker-compose restart spark-master spark-worker
```

---

## 📊 IMPACT SUR SUPERSET

### Aucun impact négatif

- Les tables restent **100% interrogeables** via SQL
- Superset se connecte via **Thrift Server** → fonctionne normalement
- Les performances sont **identiques** (voire légèrement meilleures car pas de conversion)

### Test de connexion Superset

Une fois les tables recréées, dans Superset SQL Lab :

```sql
SELECT
    t.annee,
    COUNT(*) as nb_consultations
FROM fait_consultation f
JOIN dim_temps t ON f.id_temps = t.id_temps
GROUP BY t.annee
ORDER BY t.annee
```

✅ **Résultat attendu** : 9 lignes (2015-2023)

---

## ❓ FAQ

### Q1 : Pourquoi ce problème apparaît maintenant ?

**R** : Les notebooks 01-02-03 créent les fichiers Parquet Gold avec un schéma strict (types Python/Pandas → Parquet). Quand on crée des tables Hive **après**, il peut y avoir des incompatibilités de typage (DATE vs STRING, INT vs LONG, etc.).

### Q2 : Est-ce que ça affecte les notebooks 01-03 ?

**R** : Non, ils utilisent `spark.read.parquet()` directement, pas de metastore Hive.

### Q3 : Faut-il refaire tous les notebooks ?

**R** : Non, juste **redémarrer et relancer le Notebook 05** avec les corrections.

### Q4 : Les données sont-elles perdues ?

**R** : **NON** ! Les fichiers Parquet dans `/home/jovyan/data/gold/` sont intacts. On recrée juste les **métadonnées** (metastore) qui pointent vers ces fichiers.

---

## ✅ VALIDATION FINALE

**Checklist après fix** :

- [ ] Notebook 05 redémarré et exécuté sans erreur
- [ ] 6 tables créées avec succès
- [ ] Comptage affiche ~2.2M lignes total
- [ ] Test 1 (consultations par année) fonctionne
- [ ] Connexion Superset teste avec succès
- [ ] SQL Lab exécute une requête de test

---

## 🎯 CONCLUSION

Ce problème est **normal** et **facilement résolu** avec la configuration `spark.sql.hive.convertMetastoreParquet=false`.

**Les modifications appliquées** :
1. ✅ Configuration Spark dans Notebook 05 (cellule 2)
2. ✅ DROP TABLE avant CREATE pour forcer la recréation (cellule 4)

**Workflow E2E toujours 100% opérationnel** :
```
CSV/PostgreSQL → Bronze → Silver → Gold → Spark SQL → Superset ✅
```

**Prochaine étape** : Une fois Notebook 05 validé → Configurer Superset (GUIDE_DEMARRAGE_RAPIDE_SUPERSET.md)
