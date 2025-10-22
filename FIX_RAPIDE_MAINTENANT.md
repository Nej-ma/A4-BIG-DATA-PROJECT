# ⚡ FIX RAPIDE - MAINTENANT !

## 🎯 TA SITUATION

Tu as exécuté Notebook 05 **avant** mes corrections → metastore Hive conflictuel

**Erreur actuelle** :
```
dim_temps : ❌ Erreur - Column in converted table has different data type...
```

---

## ✅ SOLUTION EN 3 CLICS (2 MINUTES)

### 1️⃣ Ouvrir Jupyter

http://localhost:8888

### 2️⃣ Ouvrir Notebook 05

**notebooks/05_Setup_Superset.ipynb**

### 3️⃣ Restart Kernel

**Kernel** → **Restart Kernel** (dans le menu du haut)

Popup → **Restart**

### 4️⃣ Run All

**Run** → **Run All Cells** (dans le menu)

Ou **Cell** → **Run All**

---

## ✅ RÉSULTAT ATTENDU

### Cellule 2 : Config Spark

```
✅ Spark 3.5.0 démarré avec support Hive
✅ spark.sql.hive.convertMetastoreParquet = false (fix schéma)
```

### Cellule 4 : Création tables

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

### Cellule de comptage : PLUS D'ERREUR

```
📊 COMPTAGE DES LIGNES
============================================================
  dim_temps                 :      4,748 lignes  ← ✅ FIXÉ
  dim_patient               :    100,000 lignes
  dim_diagnostic            :     15,490 lignes
  dim_professionnel         :  1,048,575 lignes
  dim_etablissement         :        200 lignes
  fait_consultation         :  1,027,157 lignes
============================================================
  TOTAL                     :  2,191,422 lignes

✅ Toutes les tables sont accessibles !
```

### Tests SQL : Tous fonctionnent

```
🔍 TEST 1 : Consultations par année

+-----+----------------+----------------+
|annee|nb_consultations|patients_uniques|
+-----+----------------+----------------+
|2015 |33896           |28581           |
|2016 |184308          |85272           |
...
```

---

## ❌ SI ÇA NE MARCHE PAS

### Option A : Nettoyage manuel dans Jupyter

Créer une **nouvelle cellule** au début du Notebook 05 et exécuter :

```python
# NETTOYAGE FORCÉ
tables = ["dim_temps", "dim_patient", "dim_diagnostic",
          "dim_professionnel", "dim_etablissement", "fait_consultation"]

for table in tables:
    try:
        spark.sql(f"DROP TABLE IF EXISTS {table}")
        print(f"✅ {table} supprimée")
    except:
        pass
```

Puis relancer **Run All Cells**.

### Option B : Script Python standalone

Dans un terminal :

```bash
cd /c/Users/littl/Desktop/Big\ DATA/projet_git
python cleanup_tables.py
```

Puis relancer Notebook 05.

### Option C : Nettoyage via beeline

```bash
docker exec -it chu_spark_master beeline -u jdbc:hive2://localhost:10000/default
```

Puis :
```sql
DROP TABLE IF EXISTS dim_temps;
DROP TABLE IF EXISTS dim_patient;
DROP TABLE IF EXISTS dim_diagnostic;
DROP TABLE IF EXISTS dim_professionnel;
DROP TABLE IF EXISTS dim_etablissement;
DROP TABLE IF EXISTS fait_consultation;
!quit
```

Puis relancer Notebook 05.

---

## 🎯 POURQUOI LE RESTART KERNEL EST CRUCIAL

**Sans Restart Kernel** :
- Spark Session est déjà créée avec l'ancienne config
- La nouvelle config `convertMetastoreParquet=false` n'est pas appliquée
- Le conflit persiste

**Avec Restart Kernel** :
- Nouvelle Spark Session créée
- Config `convertMetastoreParquet=false` active
- DROP TABLE supprime le metastore conflictuel
- CREATE TABLE recrée avec le bon schéma
- ✅ Tout fonctionne

---

## ✅ APRÈS LE FIX

Une fois Notebook 05 validé (comptage OK, tests OK), tu peux :

1. **Configurer Superset** (5 min)
   - Voir [GUIDE_DEMARRAGE_RAPIDE_SUPERSET.md](GUIDE_DEMARRAGE_RAPIDE_SUPERSET.md) Étape 2

2. **Tester SQL Lab** (1 min)
   - http://localhost:8088 → SQL Lab

3. **Créer dashboard** (2 min)
   - Charts → Big Number → COUNT(*) → Dashboard

**Total** : 10 minutes pour workflow E2E complet

---

## 📞 SI BLOQUÉ

Si vraiment rien ne marche, envoie-moi les logs de la cellule 4 (création tables).

---

**🚀 ACTION IMMÉDIATE : Kernel → Restart → Run All**

**Temps estimé : 2 minutes**

Vas-y maintenant ! 💪
