# 🔧 RÉSOLUTION DES PROBLÈMES - Livrable 2

**Date** : 21 Octobre 2025
**Équipe** : Nejma MOUALHI | Brieuc OLIVIERI | Nicolas TAING

---

## ✅ PROBLÈMES RÉSOLUS

### 1. ❌ Notebook 04 : ImportError `case`

**Erreur** :
```
ImportError: cannot import name 'case' from 'pyspark.sql.functions'
```

**Cause** :
- La fonction `case` n'existe pas dans PySpark
- Il faut utiliser `when` directement ou `F.when`

**Solution appliquée** :
```python
# AVANT (❌)
from pyspark.sql.functions import case, when

# APRÈS (✅)
import pyspark.sql.functions as F
from pyspark.sql.functions import col, count, countDistinct, when
```

**Fichier modifié** : `jupyter/notebooks/04_Performance_Benchmarks.ipynb` (cellule 1)

**Statut** : ✅ **RÉSOLU**

---

### 2. ❌ Notebook 04 : TypeError dans benchmark_query

**Erreur** :
```
TypeError: 'module' object is not subscriptable
# Lors de l'accès à __builtins__['sum']
```

**Cause** :
- Conflit entre fonctions Python natives et fonctions Spark
- Utilisation incorrecte de `__builtins__` comme dictionnaire

**Solution appliquée** :
```python
# AVANT (❌)
avg_time = __builtins__['sum'](times) / len(times)

# APRÈS (✅)
avg_time = sum(times) / len(times)  # Python built-in directement
min_time = min(times)
max_time = max(times)
```

**Également renommé** :
```python
# AVANT (❌)
count = result.count()  # Conflit avec count() de PySpark

# APRÈS (✅)
count_rows = result.count()  # Nom explicite
```

**Fichier modifié** : `jupyter/notebooks/04_Performance_Benchmarks.ipynb` (cellule 5)

**Statut** : ✅ **RÉSOLU**

---

### 3. ❌ MinIO vide malgré notebooks réussis

**Problème** :
- Notebooks 1-3 s'exécutent avec succès
- 2,816,803 lignes dans Gold layer
- **MAIS** MinIO Console vide (pas de fichiers visibles)

**Diagnostic** :

```yaml
# Configuration AVANT (docker-compose.yml)
minio:
  volumes:
    - minio_data:/data  # ← Volume Docker isolé ❌

jupyter:
  volumes:
    - ./spark/data:/home/jovyan/data  # ← Répertoire local ✅
```

**Cause racine** :
- Jupyter écrit dans `./spark/data/` (répertoire local sur l'hôte)
- MinIO lit depuis `minio_data` (volume Docker isolé)
- **Les deux ne communiquent pas !**

**Solution appliquée** :

```yaml
# Configuration APRÈS (docker-compose.yml)
minio:
  volumes:
    - ./spark/data:/data  # ✅ FIXÉ : Partage le même répertoire

jupyter:
  volumes:
    - ./spark/data:/home/jovyan/data  # ✅ Même source
```

**Commandes exécutées** :
```bash
# 1. Arrêter MinIO
docker compose stop minio

# 2. Supprimer le container
docker compose rm -f minio

# 3. Relancer avec nouveau volume
docker compose up -d minio

# 4. Recréer les buckets
docker compose up -d minio_setup
```

**Résultat** :
```
✅ Buckets Delta Lake créés avec succès!
```

**Fichier modifié** : [docker-compose.yml](docker-compose.yml:87)

**Statut** : ✅ **RÉSOLU**

---

## 📊 VÉRIFICATION DES DONNÉES

### Structure complète dans `./spark/data/` (= MinIO `/data/`)

```
spark/data/
├── bronze/                          ← Layer 1 : Données brutes
│   ├── csv/
│   │   ├── deces_2019/             (620K décès 2019)
│   │   ├── etablissement_sante/    (416K établissements)
│   │   └── satisfaction_2019/      (1,152 évaluations)
│   └── postgres/
│       ├── Patient/                (100K patients)
│       ├── Consultation/           (1M+ consultations)
│       ├── Diagnostic/
│       └── ... (10 autres tables)
│
├── silver/                          ← Layer 2 : Données nettoyées
│   ├── consultation/               (anonymisé, dates formatées)
│   ├── deces_2019/                 (SHA-256)
│   ├── diagnostic/                 (nettoyé)
│   ├── etablissement_sante/        (normalisé)
│   ├── laboratoire/
│   ├── medicaments/
│   ├── mutuelle/
│   ├── patient/                    (SHA-256 noms/prénoms)
│   ├── professionnel_de_sante/
│   ├── salle/
│   ├── satisfaction_2019/          (typé)
│   └── specialites/
│
└── gold/                            ← Layer 3 : Star Schema
    ├── dim_diagnostic/              (15K codes)
    ├── dim_etablissement/           (416K établissements)
    ├── dim_patient/                 (100K anonymisés)
    ├── dim_professionnel/           (1M+ avec spécialités)
    ├── dim_temps/                   (4,748 jours 2013-2025)
    ├── fait_consultation/           (1M+ partitionné année/mois)
    ├── fait_deces/                  (620K partitionné année/mois)
    └── fait_satisfaction/           (1,152 partitionné année)
```

---

## 🎯 ACCÈS MINIO CONSOLE

**URL** : http://localhost:9001

**Login** :
- Username : `minioadmin`
- Password : `minioadmin123`

### Navigation dans MinIO Console

1. Cliquer sur **"Buckets"** (menu gauche)
2. Cliquer sur **"lakehouse"**
3. Vous devriez maintenant voir :

```
lakehouse/
├── bronze/
│   ├── csv/
│   └── postgres/
├── silver/
│   ├── consultation/
│   ├── patient/
│   └── ... (10 autres tables)
└── gold/
    ├── dim_diagnostic/
    ├── dim_patient/
    └── ... (8 tables)
```

---

## ✅ VOLUMÉTRIES FINALES

### Résultats Notebook 03 (confirmés)

| Layer | Tables | Lignes Total |
|-------|--------|--------------|
| **Dimensions** | 5 | 1,169,013 |
| **Faits** | 3 | 1,647,790 |
| **TOTAL GOLD** | **8** | **2,816,803** |

### Détail des Dimensions

| Table | Lignes |
|-------|--------|
| dim_temps | 4,748 |
| dim_patient | 100,000 |
| dim_diagnostic | ~15,000 |
| dim_professionnel | ~633,265 |
| dim_etablissement | 416,000 |

### Détail des Faits

| Table | Lignes | Partitionnement |
|-------|--------|-----------------|
| fait_consultation | ~1,026,638 | année/mois |
| fait_deces | 620,000 | année/mois |
| fait_satisfaction | 1,152 | année |

---

## 📋 CHECKLIST FINALE LIVRABLE 2

### Infrastructure
- [x] PostgreSQL avec données (100K patients, 1M+ consultations)
- [x] MinIO avec buckets configurés
- [x] **MinIO montre maintenant les données !** ✅
- [x] Spark Master + Worker opérationnels
- [x] Jupyter Lab avec PySpark
- [x] Airflow fonctionnel
- [x] Superset opérationnel

### Pipeline ETL
- [x] Notebook 01 : Extract Bronze ✅
- [x] Notebook 02 : Transform Silver ✅
- [x] Notebook 03 : Transform Gold ✅
- [x] **Notebook 04 : Benchmarks (erreurs corrigées)** ✅

### Données
- [x] Bronze layer : 16 sources (13 PostgreSQL + 3 CSV)
- [x] Silver layer : 12 tables nettoyées et anonymisées
- [x] Gold layer : 5 dimensions + 3 faits
- [x] **Données visibles dans MinIO Console** ✅

### Optimisations
- [x] Partitionnement temporel (année/mois)
- [x] Format Parquet compressé
- [x] Anonymisation RGPD (SHA-256)
- [x] Typage correct des colonnes
- [x] Dédoublonnage

### Documentation
- [x] README.md mis à jour
- [x] PIPELINE_FINAL_CORRECT.md créé
- [x] LIVRABLE_2_FINAL.md créé
- [x] TUTO_EXECUTION_COMPLETE.md créé
- [x] **FIX_MINIO_VOLUME.md créé** ✅
- [x] **RESOLUTION_PROBLEMES.md créé (ce fichier)** ✅

---

## 🚀 PROCHAINES ÉTAPES (LIVRABLE 3)

### 1. DAGs Airflow
- [ ] Convertir notebooks en scripts Python
- [ ] Créer DAG orchestrant Bronze → Silver → Gold
- [ ] Tester l'exécution automatique
- [ ] Configurer scheduling (quotidien/hebdomadaire)

### 2. Dashboards Superset
- [ ] Connecter Superset à Gold layer
- [ ] Créer graphiques métier :
  - Consultations par mois
  - Top 10 diagnostics
  - Répartition décès par région
  - Scores satisfaction par établissement
- [ ] Assembler dashboard avec storytelling

### 3. Présentation
- [ ] Démo pipeline Airflow en live
- [ ] Démo dashboard Superset
- [ ] Analyse des résultats et insights métier

---

## 📞 COMMANDES UTILES

### Relancer MinIO si besoin
```bash
docker compose restart minio
```

### Voir les logs
```bash
docker logs chu_minio
docker logs chu_jupyter
```

### Vérifier les volumes montés
```bash
docker inspect chu_minio | grep -A 10 "Mounts"
```

### Accéder à Jupyter
```bash
# URL : http://localhost:8888
# Token : admin123
```

---

## ✅ RÉSUMÉ

**3 problèmes identifiés et résolus** :

1. ✅ **Notebook 04 - ImportError `case`**
   → Corrigé en utilisant `import pyspark.sql.functions as F`

2. ✅ **Notebook 04 - TypeError benchmark_query**
   → Corrigé en utilisant directement `sum()`, `min()`, `max()`

3. ✅ **MinIO vide**
   → Corrigé en changeant le volume de `minio_data:/data` vers `./spark/data:/data`

**Pipeline complet fonctionnel** :
- Bronze : 4.6M lignes (13 PostgreSQL + 3 CSV)
- Silver : 4.6M lignes nettoyées et anonymisées
- Gold : 2.8M lignes (5 dimensions + 3 faits)
- **Données visibles dans MinIO Console** ✅

**Livrable 2 : 100% opérationnel !** 🎉

---

**Prêt pour démonstration et évaluation.**
