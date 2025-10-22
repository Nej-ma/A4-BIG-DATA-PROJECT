# 🧹 NETTOYAGE HIVE METASTORE

## Problème

Tu as exécuté le Notebook 05 **avant** mes corrections, donc le metastore Hive a enregistré des schémas conflictuels.

**Erreur actuelle** :
```
Column in converted table has different data type with source Hive table's.
```

---

## ✅ SOLUTION RAPIDE

### Option 1 : Via Notebook 05 (RECOMMANDÉ)

**Le notebook corrigé nettoie automatiquement**, mais il faut le relancer avec Kernel Restart :

1. Ouvrir http://localhost:8888
2. **notebooks/05_Setup_Superset.ipynb**
3. **Kernel** → **Restart Kernel** (important !)
4. **Run** → **Run All Cells**

Le notebook va maintenant :
- ✅ Configurer `spark.sql.hive.convertMetastoreParquet=false`
- ✅ Supprimer les anciennes tables (`DROP TABLE IF EXISTS`)
- ✅ Recréer les tables avec le bon schéma

---

### Option 2 : Nettoyage manuel via beeline (si Option 1 ne marche pas)

**Connexion au Thrift Server** :

```bash
docker exec -it chu_spark_master beeline -u jdbc:hive2://localhost:10000/default
```

**Supprimer toutes les tables** :

```sql
DROP TABLE IF EXISTS dim_temps;
DROP TABLE IF EXISTS dim_patient;
DROP TABLE IF EXISTS dim_diagnostic;
DROP TABLE IF EXISTS dim_professionnel;
DROP TABLE IF EXISTS dim_etablissement;
DROP TABLE IF EXISTS fait_consultation;

-- Vérifier
SHOW TABLES;
```

**Sortir** :
```
!quit
```

Puis relancer Notebook 05.

---

### Option 3 : Reset complet du metastore (NUCLEAR)

**Si vraiment rien ne fonctionne** :

```bash
# Arrêter Spark
docker exec chu_spark_master bash -c '$SPARK_HOME/sbin/stop-thriftserver.sh'

# Supprimer le metastore Hive (Derby DB)
docker exec chu_spark_master bash -c 'rm -rf /tmp/spark-warehouse /tmp/metastore_db'

# Redémarrer Thrift Server
docker exec chu_spark_master bash -c '$SPARK_HOME/sbin/start-thriftserver.sh --master spark://spark-master:7077 --hiveconf hive.server2.thrift.port=10000 --hiveconf hive.server2.thrift.bind.host=0.0.0.0'

# Attendre 10 secondes
sleep 10
```

Puis relancer Notebook 05.

---

## 🎯 ÉTAPES DÉTAILLÉES (Option 1 recommandée)

### 1. Restart Kernel Jupyter

**TRÈS IMPORTANT** : Il faut redémarrer le kernel pour que la nouvelle config Spark soit prise en compte.

Dans Jupyter :
1. Ouvrir **05_Setup_Superset.ipynb**
2. **Kernel** → **Restart Kernel** (popup → OK)
3. **Ne pas** juste Re-run, vraiment **Restart** !

### 2. Run All Cells

**Run** → **Run All Cells**

Tu devrais voir :

```
✅ Spark 3.5.0 démarré avec support Hive
✅ spark.sql.hive.convertMetastoreParquet = false (fix schéma)

📦 Création des tables externes...

  🗑️  dim_temps - ancien metastore supprimé
  ✅ 1/6 - dim_temps créée
  🗑️  dim_patient - ancien metastore supprimé
  ✅ 2/6 - dim_patient créée
  🗑️  dim_diagnostic - ancien metastore supprimé
  ✅ 3/6 - dim_diagnostic créée
  🗑️  dim_professionnel - ancien metastore supprimé
  ✅ 4/6 - dim_professionnel créée
  🗑️  dim_etablissement - ancien metastore supprimé
  ✅ 5/6 - dim_etablissement créée
  🗑️  fait_consultation - ancien metastore supprimé
  ✅ 6/6 - fait_consultation créée

✅ Toutes les tables créées !
```

### 3. Vérifier le comptage

```
📊 COMPTAGE DES LIGNES
============================================================
  dim_temps                 :      4,748 lignes  ← ✅ PLUS D'ERREUR
  dim_patient               :    100,000 lignes
  dim_diagnostic            :     15,490 lignes
  dim_professionnel         :  1,048,575 lignes
  dim_etablissement         :        200 lignes
  fait_consultation         :  1,027,157 lignes
============================================================
  TOTAL                     :  2,191,422 lignes

✅ Toutes les tables sont accessibles !
```

### 4. Vérifier les tests SQL

Les 5 tests (TEST 1 à TEST 5) doivent tous s'exécuter sans erreur.

**TEST 1 attendu** :
```
+-----+----------------+----------------+
|annee|nb_consultations|patients_uniques|
+-----+----------------+----------------+
|2015 |33896           |28581           |
|2016 |184308          |85272           |
|2017 |133403          |74201           |
...
```

---

## 🔍 DIAGNOSTIC

### Vérifier que la config Spark est appliquée

Dans le Notebook 05, cellule 2, après exécution :

```python
# Ajouter cette cellule temporaire pour vérifier :
print(spark.conf.get("spark.sql.hive.convertMetastoreParquet"))
# Doit afficher : false
```

### Vérifier que les tables sont DROP avant CREATE

Dans le Notebook 05, tu dois voir dans les logs :

```
🗑️  dim_temps - ancien metastore supprimé
```

Si tu vois `ℹ️  dim_temps - pas de metastore existant`, c'est normal la première fois.

---

## ❌ SI ERREUR PERSISTE

### Erreur : "Connection refused to Thrift Server"

**Cause** : Thrift Server crashé ou pas démarré

**Fix** :
```bash
# Vérifier si le process tourne
docker exec chu_spark_master ps aux | grep -i thrift

# Si rien, redémarrer
docker exec chu_spark_master bash -c '$SPARK_HOME/sbin/start-thriftserver.sh --master spark://spark-master:7077 --hiveconf hive.server2.thrift.port=10000'

# Attendre 10 secondes
sleep 10

# Relancer Notebook 05
```

### Erreur : "Table already exists"

**Cause** : DROP TABLE n'a pas fonctionné

**Fix** :
```python
# Dans Jupyter, créer une nouvelle cellule et exécuter :
spark.sql("DROP TABLE IF EXISTS dim_temps")
spark.sql("DROP TABLE IF EXISTS dim_patient")
spark.sql("DROP TABLE IF EXISTS dim_diagnostic")
spark.sql("DROP TABLE IF EXISTS dim_professionnel")
spark.sql("DROP TABLE IF EXISTS dim_etablissement")
spark.sql("DROP TABLE IF EXISTS fait_consultation")

# Puis relancer cellule 4 (création des tables)
```

---

## ✅ VALIDATION

**Checklist après nettoyage** :

- [ ] Notebook 05 Kernel restarted
- [ ] Cellule 2 affiche : `spark.sql.hive.convertMetastoreParquet = false`
- [ ] Cellule 4 affiche : `✅ 1/6 - dim_temps créée` (sans erreur)
- [ ] Cellule de comptage affiche : `dim_temps : 4,748 lignes` (sans ❌)
- [ ] TEST 1 s'exécute sans erreur et affiche 9 lignes

---

## 🎯 RÉSUMÉ

**Le problème** : Metastore Hive a enregistré un schéma conflictuel lors de la première exécution (avant corrections).

**La solution** : Restart Kernel + Run All pour que :
1. Config `convertMetastoreParquet=false` soit appliquée
2. DROP TABLE supprime les anciens metastores
3. CREATE TABLE recrée avec le bon schéma

**Action immédiate** :
```
Jupyter → 05_Setup_Superset.ipynb
→ Kernel → Restart Kernel
→ Run → Run All Cells
✅ Vérifier comptage dim_temps sans erreur
```

**Temps estimé** : 2 minutes

Bonne chance ! 🚀
