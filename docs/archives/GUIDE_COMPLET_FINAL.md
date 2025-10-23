# 🎯 GUIDE COMPLET FINAL - Livrable 2 CHU Data Lakehouse

**Date** : 2025-10-22
**Statut** : ✅ Tous les scripts corrigés - Prêt pour exécution

---

## 📋 RÉSUMÉ DES CORRECTIONS

### ✅ Corrections appliquées aux notebooks

1. **Notebook 03 - Cellule 4** : dim_temps SANS partitionnement
2. **Notebook 05 - Cellule 2** : Config `convertMetastoreParquet=false`
3. **Notebook 05 - Cellule 4** : dim_temps SANS `PARTITIONED BY`
4. **Notebook 05 - Cellule 6** : Réparation uniquement fait_consultation
5. **Superset Container** : PyHive installé

### 🔧 Problèmes résolus

- ❌ "Column in converted table has different data type" → ✅ Config Spark corrigée
- ❌ "Path is a directory, which is not supported" → ✅ Partitionnement supprimé
- ❌ "Could not load database driver" → ✅ PyHive installé
- ❌ Spark SQL multi-statement → ✅ DROP et CREATE séparés

---

## 🚀 PLAN D'ACTION IMMÉDIAT (12 MINUTES)

### ÉTAPE 1 : Régénérer Gold Layer (5 min)

**Objectif** : Recréer dim_temps SANS partitionnement

1. Ouvrir http://localhost:8888
2. Ouvrir **03_Transform_Gold_STAR_SCHEMA.ipynb**
3. **Kernel** → **Restart Kernel** (important !)
4. **Run** → **Run All Cells**
5. Attendre ~3-4 minutes

**Vérification** : Cellule 4 doit afficher :
```
💾 Sauvegardé: /home/jovyan/data/gold/dim_temps (sans partitionnement)
   ℹ️  Changé: Pas de partitionnement pour compatibilité Hive/Superset
```

**IMPORTANT** : Le Restart Kernel est crucial pour recréer les fichiers Parquet correctement.

---

### ÉTAPE 2 : Créer tables Hive (2 min)

**Objectif** : Créer les 6 tables Spark SQL avec les bons schémas

1. Ouvrir **05_Setup_Superset.ipynb**
2. **Kernel** → **Restart Kernel** (important !)
3. **Run** → **Run All Cells**
4. Attendre ~1-2 minutes

**Vérification** : Cellule de comptage doit afficher :
```
📊 COMPTAGE DES LIGNES
============================================================
  dim_temps                 :      4,748 lignes  ✅
  dim_patient               :    100,000 lignes  ✅
  dim_diagnostic            :     15,490 lignes  ✅
  dim_professionnel         :  1,048,575 lignes  ✅
  dim_etablissement         :        200 lignes  ✅
  fait_consultation         :  1,027,157 lignes  ✅
============================================================
  TOTAL                     :  2,191,422 lignes

✅ Toutes les tables sont accessibles !
```

**AUCUNE ERREUR** ne doit apparaître, notamment pas d'❌.

**Tests SQL** : Les 3 tests doivent afficher des résultats :
- TEST 1 : 9 lignes (2015-2023)
- TEST 2 : 15 lignes (top diagnostics)
- TEST 3 : 200 lignes (établissements)

---

### ÉTAPE 3 : Configurer Superset (5 min)

**Objectif** : Connecter Superset à la Gold Layer via Spark Thrift Server

#### 3.1 Vérifier Thrift Server (30 sec)

```bash
docker exec chu_spark_master bash -c "jps | grep -i thrift"
```

**Si rien** : Démarrer le Thrift Server
```bash
docker exec chu_spark_master bash -c '$SPARK_HOME/sbin/start-thriftserver.sh --master spark://spark-master:7077 --hiveconf hive.server2.thrift.port=10000'
```

Attendre 10 secondes.

#### 3.2 Vérifier PyHive (30 sec)

```bash
docker exec chu_superset pip show pyhive
```

**Si erreur** : Installer PyHive
```bash
docker exec chu_superset pip install pyhive
docker restart chu_superset
```

Attendre 20-30 secondes que Superset redémarre.

#### 3.3 Connexion Superset (2 min)

1. Ouvrir http://localhost:8088
2. Login : `admin` / `admin`
3. **Settings** ⚙️ → **Database Connections**
4. **+ DATABASE**
5. **SUPPORTED DATABASES** → **Apache Spark SQL**
6. **SQLAlchemy URI** :
   ```
   hive://spark-master:10000/default
   ```
7. **Display Name** : `CHU_Gold_Layer`
8. **ADVANCED** → **Other** → Cocher :
   - ✅ **Expose database in SQL Lab**
   - ✅ **Allow CREATE TABLE AS**
9. **TEST CONNECTION** → ✅ "Connection looks good!"
10. **CONNECT**

---

### ÉTAPE 4 : Tester SQL Lab (1 min)

**Objectif** : Valider que Superset peut interroger les tables Hive

1. **SQL Lab** → **SQL Editor**
2. **DATABASE** : `CHU_Gold_Layer`
3. **SCHEMA** : `default`
4. Copier-coller cette requête :

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

5. **RUN**

**Résultat attendu** : 9 lignes (2015-2023)

```
annee | nb_consultations | patients_uniques
------|------------------|------------------
2015  |     33,896       |     28,581
2016  |    184,308       |     85,272
2017  |    119,632       |     69,857
2018  |    113,894       |     66,892
2019  |    113,861       |     66,853
2020  |    113,849       |     66,859
2021  |    113,867       |     66,867
2022  |    113,867       |     66,842
2023  |    113,883       |     66,856
```

✅ **SI TU VOIS CES RÉSULTATS → WORKFLOW E2E VALIDÉ !**

---

### ÉTAPE 5 : Créer Dashboard (3 min)

**Objectif** : Créer un dashboard Superset pour démonstration

#### 5.1 Créer Dataset (1 min)

1. **Data** → **Datasets** → **+ DATASET**
2. **Database** : `CHU_Gold_Layer`
3. **Schema** : `default`
4. **Table** : `fait_consultation`
5. **ADD**

#### 5.2 Créer Graphique (1 min)

1. **Charts** → **+ CHART**
2. **Dataset** : `fait_consultation`
3. **Chart Type** : **Big Number**
4. **QUERY** → **Metrics** : `COUNT(*)`
5. **UPDATE CHART**

**Résultat attendu** : **1,027,157**

#### 5.3 Créer Dashboard (1 min)

1. **SAVE** (en haut à droite)
2. **Chart Name** : `Total Consultations CHU`
3. **Add to Dashboard** : **Create new dashboard**
   - **Name** : `CHU Overview - Livrable 2`
4. **SAVE & GO TO DASHBOARD**

✅ **TON DASHBOARD EST CRÉÉ !**

---

## 📊 ARCHITECTURE E2E COMPLÈTE

```
Sources de données
    ├─ CSV deces.csv (25M lignes)
    ├─ CSV etablissement_sante.csv (200 lignes)
    ├─ CSV satisfaction_esatis48h_2019.csv
    └─ PostgreSQL (13 tables)
           ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    BRONZE LAYER (Notebook 01)
    17 tables | ~29M lignes
    Format: Parquet partitionné
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    SILVER LAYER (Notebook 02)
    12 tables | Nettoyées + RGPD
    Anonymisation SHA-256
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    GOLD LAYER (Notebook 03) ✅ FIXÉ
    8 tables | Star Schema | ~2.2M lignes

    Dimensions (5):
    ├─ dim_temps (4,748) ← SANS partitionnement
    ├─ dim_patient (100,000)
    ├─ dim_diagnostic (15,490) + CIM-10
    ├─ dim_professionnel (1,048,575)
    └─ dim_etablissement (200) + géographie

    Faits (3):
    ├─ fait_consultation (1,027,157) partitionné annee/mois
    ├─ fait_deces (25M)
    └─ fait_satisfaction (3,638)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    SPARK SQL TABLES (Notebook 05) ✅ FIXÉ
    6 tables Hive externes

    ├─ dim_temps (SANS PARTITIONED BY) ← FIX
    ├─ dim_patient
    ├─ dim_diagnostic
    ├─ dim_professionnel
    ├─ dim_etablissement
    └─ fait_consultation (PARTITIONED BY annee, mois)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    SPARK THRIFT SERVER
    Port 10000 | JDBC/ODBC
    PyHive driver ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    APACHE SUPERSET
    Connexion: hive://spark-master:10000/default

    ├─ SQL Lab (requêtes ad-hoc)
    ├─ Datasets (6 tables)
    ├─ Charts (visualisations)
    └─ Dashboards (analytique métier)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🎯 CHECKLIST VALIDATION COMPLÈTE

### Bronze Layer ✅
- [x] 17 tables créées
- [x] CSV complet deces.csv (25M lignes)
- [x] PostgreSQL (13 tables)
- [x] Départements français ajoutés

### Silver Layer ✅
- [x] 12 tables nettoyées
- [x] Anonymisation SHA-256 (RGPD)
- [x] Typage strict

### Gold Layer ✅ FIXÉ
- [x] 8 tables Star Schema
- [x] dim_diagnostic + catégorie CIM-10
- [x] dim_etablissement + région/département
- [x] dim_temps SANS partitionnement ← **FIX APPLIQUÉ**
- [x] fait_consultation partitionné (90 partitions)

### Optimisations ✅
- [x] Format Parquet (~10x compression)
- [x] Partitionnement temporel (année/mois)
- [x] Spark AQE activé
- [x] Benchmarks < 16s (Notebook 04)

### Superset ✅ CORRIGÉ
- [x] Thrift Server démarré
- [x] PyHive installé
- [x] Notebook 05 créé et corrigé
- [ ] Notebook 03 régénéré (à faire - 5 min)
- [ ] Notebook 05 validé (à faire - 2 min)
- [ ] Connexion Superset configurée (à faire - 5 min)
- [ ] Dashboard créé (à faire - 3 min)

**Total temps restant** : 15 minutes

---

## 📚 DOCUMENTATION CRÉÉE

| Document | Description | Usage |
|----------|-------------|-------|
| [ETAPES_FINALES_SUPERSET.md](ETAPES_FINALES_SUPERSET.md) | Guide complet avec tous les fixes | ⭐ GUIDE PRINCIPAL |
| [TUTORIEL_SUPERSET.md](TUTORIEL_SUPERSET.md) | Tutorial détaillé (600 lignes) | Apprentissage approfondi |
| [GUIDE_DEMARRAGE_RAPIDE_SUPERSET.md](GUIDE_DEMARRAGE_RAPIDE_SUPERSET.md) | Quick start 10 min | Démarrage rapide |
| [FIX_RAPIDE_MAINTENANT.md](FIX_RAPIDE_MAINTENANT.md) | Fix erreur metastore | Troubleshooting |
| [README_SUPERSET.md](README_SUPERSET.md) | Vue d'ensemble | Introduction |
| [INDEX_DOCUMENTATION.md](INDEX_DOCUMENTATION.md) | Index de tous les docs | Navigation |

---

## 🎓 POUR TON CV / PORTFOLIO

### Description courte (CV)

> **Data Lakehouse CHU - Architecture Medallion (Bronze/Silver/Gold)**
> Pipeline ETLT complet avec Apache Spark (PySpark) : ingestion multi-sources (CSV 25M lignes + PostgreSQL), transformations et anonymisation RGPD (SHA-256), modélisation dimensionnelle (Star Schema), optimisations (Parquet, partitionnement), et visualisation BI avec Apache Superset via Spark SQL/Thrift Server.
> Stack : Spark 3.5.0, Docker, Jupyter, MinIO, PostgreSQL, Superset

### Points clés à mentionner

1. **Architecture Medallion** : Bronze (raw) → Silver (cleaned) → Gold (dimensional)
2. **Scale** : 29M lignes sources → 2.2M lignes Gold après transformations
3. **RGPD** : Anonymisation SHA-256 des données sensibles
4. **Enrichissements** : Catégories CIM-10, géolocalisation département/région
5. **Optimisations** : Parquet (compression 10x), partitionnement temporel, Spark AQE
6. **End-to-End** : Sources → Spark → Data Lake → BI (Superset)

### Technologies maîtrisées

- **Big Data** : Apache Spark 3.5.0, PySpark, Spark SQL
- **Storage** : MinIO S3, Parquet columnar format
- **Databases** : PostgreSQL, Hive Metastore
- **BI** : Apache Superset, Spark Thrift Server
- **DevOps** : Docker, Docker Compose
- **Data Quality** : RGPD compliance, data anonymization

---

## 🆘 PROBLÈMES COURANTS

### ❌ Erreur "Column in converted table" persiste après Restart Kernel

**Solution** : Nettoyer manuellement le metastore

```python
# Dans Notebook 05, créer une nouvelle cellule au début
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

---

### ❌ "Connection refused" dans Superset

**Cause** : Thrift Server pas démarré

**Fix** :
```bash
docker exec chu_spark_master bash -c '$SPARK_HOME/sbin/start-thriftserver.sh --master spark://spark-master:7077 --hiveconf hive.server2.thrift.port=10000'
```

---

### ❌ Apache Spark SQL n'apparaît pas dans Superset

**Cause** : PyHive pas installé

**Fix** :
```bash
docker exec chu_superset pip install pyhive
docker restart chu_superset
```

---

### ❌ dim_temps affiche encore "Path is a directory"

**Cause** : Notebook 03 pas régénéré après modification

**Fix** : Exécuter Notebook 03 avec **Kernel → Restart Kernel** puis **Run All**

Cela va recréer les fichiers Parquet SANS partitionnement.

---

## 🎯 RÉSUMÉ EXÉCUTIF

### Où tu en es

✅ **Complété** :
- Architecture complète Bronze/Silver/Gold
- Notebooks 01-04 validés
- Corrections appliquées aux notebooks 03 et 05
- Documentation exhaustive créée
- PyHive installé dans Superset

⏳ **À faire** (12 minutes) :
1. Régénérer Gold Layer (Notebook 03)
2. Créer tables Hive (Notebook 05)
3. Configurer Superset
4. Créer dashboard de démonstration

### Prochaine action IMMÉDIATE

1. **MAINTENANT** : http://localhost:8888
2. **Ouvrir** : 03_Transform_Gold_STAR_SCHEMA.ipynb
3. **Kernel → Restart Kernel**
4. **Run → Run All Cells**
5. **Attendre** : 3-4 minutes
6. **Vérifier** : "sans partitionnement" dans la sortie de la cellule 4

---

## ✅ VALIDATION FINALE

Après avoir suivi TOUTES les étapes, tu dois avoir :

1. ✅ Notebook 03 exécuté → dim_temps sans partitionnement
2. ✅ Notebook 05 exécuté → 2.2M lignes comptées sans erreur
3. ✅ Superset connecté → "Connection looks good!"
4. ✅ SQL Lab fonctionnel → Requête retourne 9 lignes
5. ✅ Dashboard créé → Big Number affiche 1,027,157

**ALORS** : 🎉 **LIVRABLE 2 100% COMPLET ET VALIDÉ !**

---

**🚀 COMMENCE MAINTENANT : Notebook 03 → Kernel Restart → Run All**

**Temps total restant : 12-15 minutes**

**Bon courage ! 💪**
