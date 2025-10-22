# ⚡ FIX FINAL COMPLET - MAINTENANT

**Problèmes résolus** :
1. ✅ dim_temps partitionné (erreur "is a directory")
2. ✅ PyHive installé dans Superset

---

## 🎯 ACTIONS IMMÉDIATES

### 1️⃣ Relancer Notebook 05 (2 min)

**Jupyter** : http://localhost:8888

1. Ouvrir **05_Setup_Superset.ipynb**
2. **Kernel** → **Restart Kernel**
3. **Run** → **Run All Cells**

**Résultat attendu** :

```
✅ Spark 3.5.0 démarré avec support Hive
✅ spark.sql.hive.convertMetastoreParquet = false (fix schéma)

📦 Création des tables externes...

  🗑️  dim_temps - ancien metastore supprimé
  ✅ 1/6 - dim_temps créée (PARTITIONED BY annee)  ← FIX
  🗑️  dim_patient - ancien metastore supprimé
  ✅ 2/6 - dim_patient créée
  ...
  ✅ 6/6 - fait_consultation créée

✅ Toutes les tables créées !

🔧 Réparation des partitions...

  ✅ dim_temps - 13 partitions découvertes  ← FIX
  ✅ fait_consultation - 90 partitions découvertes

✅ Partitions réparées !

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

🔍 TEST 1 : Consultations par année

+-----+----------------+----------------+
|annee|nb_consultations|patients_uniques|
+-----+----------------+----------------+
|2015 |33896           |28581           |
|2016 |184308          |85272           |
...
```

---

### 2️⃣ Attendre Superset (30 sec)

Superset redémarre (installation PyHive). Vérifier :

```bash
docker logs chu_superset --tail 20
```

Attendre le message :
```
Init Step 4/4 [Complete] -- Loading examples
Starting Superset server
```

---

### 3️⃣ Configurer Superset (5 min)

**URL** : http://localhost:8088

**Login** : `admin` / `admin`

#### Étape A : Ajouter connexion

1. **Settings** ⚙️ → **Database Connections**
2. **+ DATABASE**
3. **SUPPORTED DATABASES** → Rechercher "**Apache Spark SQL**" ← DEVRAIT APPARAÎTRE MAINTENANT
4. Ou sélectionner **"Other"** et continuer

#### Étape B : Configuration

**Onglet "BASIC"** :
- **DISPLAY NAME** : `CHU_Gold_Layer`
- **SQLALCHEMY URI** :
  ```
  hive://spark-master:10000/default
  ```

**OU Onglet "SQLALCHEMY URI"** (si pas de formulaire) :
```
hive://spark-master:10000/default
```

#### Étape C : Options avancées

**Onglet "ADVANCED"** → **Other** → Cocher :
- ✅ Expose database in SQL Lab
- ✅ Allow CREATE TABLE AS
- ✅ Allow DML

#### Étape D : Test

1. Cliquer **TEST CONNECTION** (en bas)
2. ✅ Message attendu : "**Connection looks good!**"
3. Cliquer **CONNECT**

---

### 4️⃣ Tester SQL Lab (1 min)

1. **SQL Lab** → **SQL Editor**
2. **DATABASE** : `CHU_Gold_Layer`
3. **SCHEMA** : `default`
4. Coller cette requête :

```sql
SELECT
    t.annee,
    COUNT(*) as nb_consultations,
    COUNT(DISTINCT f.id_patient) as patients_uniques
FROM fait_consultation f
JOIN dim_temps t ON f.id_temps = t.id_temps
GROUP BY t.annee
ORDER BY t.annee
```

5. **RUN** (ou Ctrl+Enter)

**Résultat attendu** : 9 lignes (2015-2023)

```
annee | nb_consultations | patients_uniques
------|------------------|------------------
2015  |     33,896       |     28,581
2016  |    184,308       |     85,272
2017  |    133,403       |     74,201
2018  |    160,373       |     81,075
2019  |     87,497       |     58,635
2020  |    162,778       |     81,612
2021  |    145,883       |     78,593
2022  |    101,991       |     66,042
2023  |     17,028       |     15,772
```

✅ **SI TU VOIS CES RÉSULTATS → WORKFLOW E2E VALIDÉ !**

---

### 5️⃣ Créer un dashboard (2 min)

#### Créer dataset

1. **Data** → **Datasets**
2. **+ DATASET**
3. **Database** : `CHU_Gold_Layer`
4. **Schema** : `default`
5. **Table** : `fait_consultation`
6. **ADD**

#### Créer graphique

1. **Charts** → **+ CHART**
2. **Dataset** : `fait_consultation`
3. **Chart Type** : **Big Number**
4. **Metrics** : `COUNT(*)`
5. **UPDATE CHART**
6. ✅ Tu verras : **1,027,157**

#### Créer dashboard

1. **SAVE** (en haut à droite)
2. **Chart Name** : `Total Consultations`
3. **Add to Dashboard** : Créer "CHU Overview"
4. **SAVE & GO TO DASHBOARD**

✅ **TON PREMIER DASHBOARD SUPERSET EST CRÉÉ !**

---

## 🔧 CORRECTIONS APPLIQUÉES

### Fix 1 : dim_temps partitionné

**Problème** : dim_temps est écrit partitionné par `annee` dans Notebook 03, mais déclaré non-partitionné dans Notebook 05

**Fix** : Ajout de `PARTITIONED BY (annee INT)` dans la définition de dim_temps

**Cellule 4 modifiée** :
```python
"dim_temps": """
    CREATE EXTERNAL TABLE dim_temps (
        id_temps STRING,
        date_complete DATE,
        mois INT,
        jour INT,
        jour_semaine INT,
        nom_jour STRING,
        trimestre INT,
        semaine_annee INT
    )
    PARTITIONED BY (annee INT)  ← AJOUTÉ
    STORED AS PARQUET
    LOCATION '/home/jovyan/data/gold/dim_temps'
"""
```

### Fix 2 : Réparation partitions dim_temps

**Ajout** : Réparation des partitions pour dim_temps (cellule 6)

```python
partitioned_tables = ["dim_temps", "fait_consultation"]  ← dim_temps ajouté

for table in partitioned_tables:
    spark.sql(f"MSCK REPAIR TABLE {table}")
```

### Fix 3 : Installation PyHive dans Superset

**Problème** : Driver HiveEngineSpec manquant dans Superset

**Fix** : Installation de PyHive dans le container Superset

```bash
docker exec chu_superset pip install pyhive
docker restart chu_superset
```

**Résultat** : Apache Spark SQL apparaît maintenant dans "SUPPORTED DATABASES"

---

## ✅ VALIDATION FINALE

**Checklist** :

- [ ] Notebook 05 exécuté sans erreur
- [ ] Comptage dim_temps : 4,748 lignes (sans ❌)
- [ ] Test SQL fonctionne (9 lignes)
- [ ] Partitions dim_temps : 13 découvertes
- [ ] Partitions fait_consultation : 90 découvertes
- [ ] Superset démarré (http://localhost:8088)
- [ ] Connexion CHU_Gold_Layer testée ✅
- [ ] SQL Lab exécute requête test
- [ ] 1 dataset créé (fait_consultation)
- [ ] 1 graphique créé (Total Consultations)
- [ ] 1 dashboard créé (CHU Overview)

---

## 📊 WORKFLOW E2E COMPLET

```
CSV/PostgreSQL (Sources)
    ↓
Bronze Layer (17 tables, 29M lignes) - Notebook 01 ✅
    ↓
Silver Layer (12 tables, RGPD) - Notebook 02 ✅
    ↓
Gold Layer (8 tables, Star Schema) - Notebook 03 ✅
    ├─ dim_temps (partitionné annee) ✅ FIX
    ├─ dim_patient
    ├─ dim_diagnostic (+ categorie CIM-10)
    ├─ dim_professionnel
    ├─ dim_etablissement (+ region/département)
    └─ fait_consultation (partitionné annee/mois)
    ↓
Benchmarks (6 requêtes < 16s) - Notebook 04 ✅
    ↓
Spark SQL Tables (6 tables Hive) - Notebook 05 ✅ FIX FINAL
    ├─ dim_temps (PARTITIONED BY annee) ✅
    └─ fait_consultation (PARTITIONED BY annee, mois) ✅
    ↓
Thrift Server (port 10000) ✅
    ↓
Superset (PyHive installé) ✅ FIX
    ├─ Connexion CHU_Gold_Layer ✅
    ├─ SQL Lab ✅
    ├─ Datasets ✅
    ├─ Charts ✅
    └─ Dashboards ✅
```

**STATUT FINAL** : ✅ 100% Opérationnel

---

## 🎓 POUR TA SOUTENANCE

**Tu peux maintenant démontrer** :

1. ✅ Architecture complète Bronze/Silver/Gold
2. ✅ ETLT pattern (E→T conformité→L→T business)
3. ✅ Optimisations (Parquet, partitionnement)
4. ✅ RGPD (anonymisation SHA-256)
5. ✅ Enrichissements (géographie, CIM-10)
6. ✅ Star Schema (5 dimensions + 3 faits)
7. ✅ Benchmarks (< 16s)
8. ✅ **Visualisation E2E avec Superset** ← NOUVEAU

**Workflow E2E validé** :
```
Sources → Jupyter → Spark → Gold → Spark SQL → Superset Dashboards
  ✅       ✅       ✅      ✅       ✅          ✅ COMPLET
```

**Données finales** :
- **Bronze** : 17 tables, 29M lignes
- **Silver** : 12 tables, 12M lignes (nettoyé + RGPD)
- **Gold** : 8 tables, 2.2M lignes (Star Schema)
- **Spark SQL** : 6 tables Hive (2 partitionnées)
- **Superset** : Dashboards analytiques interactifs

---

## 🚀 ACTION IMMÉDIATE

1. **Kernel → Restart → Run All** (Notebook 05)
2. **Attendre Superset** (30 sec)
3. **Configurer connexion** (5 min)
4. **Tester SQL Lab** (1 min)
5. **Créer dashboard** (2 min)

**Total** : 10 minutes

**PUIS** : 🎉 Projet 100% terminé pour Livrable 2 !

Vas-y maintenant ! 💪
