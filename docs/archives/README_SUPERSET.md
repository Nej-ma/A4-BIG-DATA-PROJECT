# 🎨 SUPERSET - Configuration rapide

## 🎯 Objectif

Connecter Apache Superset au Data Lakehouse Gold pour créer des dashboards analytiques.

---

## ⚡ QUICK START (10 MINUTES)

### Étape 1 : Préparer les tables Spark SQL (2 min)

1. Ouvrir http://localhost:8888
2. **notebooks/05_Setup_Superset.ipynb**
3. **Kernel** → **Restart Kernel**
4. **Run** → **Run All Cells**
5. ✅ Vérifier : ~2.2M lignes total, aucune erreur

**Si erreur "Column in converted table"** : Voir [FIX_RAPIDE_MAINTENANT.md](FIX_RAPIDE_MAINTENANT.md)

---

### Étape 2 : Configurer Superset (5 min)

1. Ouvrir http://localhost:8088
2. Login : `admin` / `admin`
3. **Settings** ⚙️ → **Database Connections** → **+ DATABASE**
4. Sélectionner **Apache Spark SQL**
5. **SQLAlchemy URI** :
   ```
   hive://spark-master:10000/default
   ```
6. **Display Name** : `CHU_Gold_Layer`
7. **TEST CONNECTION** → ✅ "Connection looks good!"
8. **CONNECT**

---

### Étape 3 : Tester SQL Lab (1 min)

1. **SQL Lab** → **SQL Editor**
2. **DATABASE** : `CHU_Gold_Layer`
3. Copier-coller :
   ```sql
   SELECT t.annee, COUNT(*) as nb
   FROM fait_consultation f
   JOIN dim_temps t ON f.id_temps = t.id_temps
   GROUP BY t.annee
   ORDER BY t.annee
   ```
4. **RUN**
5. ✅ Résultat attendu : 9 lignes (2015-2023)

---

### Étape 4 : Créer un dashboard (2 min)

1. **Data** → **Datasets** → **+ DATASET**
   - Database: `CHU_Gold_Layer`
   - Table: `fait_consultation`
   - **ADD**

2. **Charts** → **+ CHART**
   - Dataset: `fait_consultation`
   - Chart Type: **Big Number**
   - Metric: `COUNT(*)`
   - **UPDATE CHART**

3. **SAVE** → Dashboard: `CHU Overview`

✅ **Workflow E2E complet validé !**

---

## 📚 DOCUMENTATION

| Document                               | Description                    | Temps  |
|----------------------------------------|--------------------------------|--------|
| [FIX_RAPIDE_MAINTENANT.md](FIX_RAPIDE_MAINTENANT.md) | Fix erreur metastore           | 2 min  |
| [GUIDE_DEMARRAGE_RAPIDE_SUPERSET.md](GUIDE_DEMARRAGE_RAPIDE_SUPERSET.md) | Guide complet étape par étape  | 10 min |
| [TUTORIEL_SUPERSET.md](TUTORIEL_SUPERSET.md) | Documentation détaillée        | -      |
| [FIX_SUPERSET_SCHEMA_CONFLICT.md](FIX_SUPERSET_SCHEMA_CONFLICT.md) | Troubleshooting schéma         | -      |

---

## 🆘 PROBLÈMES COURANTS

### ❌ "Column in converted table has different data type"

**Solution** : [FIX_RAPIDE_MAINTENANT.md](FIX_RAPIDE_MAINTENANT.md)

**Quick fix** :
```
Jupyter → 05_Setup_Superset.ipynb
→ Kernel → Restart Kernel
→ Run All Cells
```

---

### ❌ "Connection refused" dans Superset

**Cause** : Thrift Server pas démarré

**Fix** :
```bash
docker exec chu_spark_master bash -c '$SPARK_HOME/sbin/start-thriftserver.sh --master spark://spark-master:7077 --hiveconf hive.server2.thrift.port=10000'
```

Attendre 10 secondes, puis tester la connexion Superset.

---

### ❌ "Table not found" dans SQL Lab

**Cause** : Tables Spark SQL pas créées

**Fix** : Exécuter Notebook 05_Setup_Superset.ipynb

---

## 📊 TABLES DISPONIBLES

| Table               | Lignes      | Description                          |
|---------------------|-------------|--------------------------------------|
| dim_temps           | 4,748       | Dimension temporelle                 |
| dim_patient         | 100,000     | Patients anonymisés (SHA-256)        |
| dim_diagnostic      | 15,490      | Diagnostics CIM-10 + catégorie       |
| dim_professionnel   | 1,048,575   | Professionnels de santé              |
| dim_etablissement   | 200         | Établissements + région/département  |
| fait_consultation   | 1,027,157   | Consultations (partitionné)          |

**Total** : ~2.2M lignes

---

## 🎯 WORKFLOW E2E

```
CSV/PostgreSQL
      ↓
Bronze Layer (17 tables, 29M lignes)
      ↓
Silver Layer (12 tables, nettoyé + RGPD)
      ↓
Gold Layer (8 tables, Star Schema)
      ↓
Spark SQL (6 tables Hive)
      ↓
Thrift Server (port 10000)
      ↓
Apache Superset (dashboards)
```

**État actuel** :
- ✅ Bronze, Silver, Gold : Opérationnels
- ✅ Spark SQL + Thrift : Configurés
- ⏳ Superset : En cours de configuration

---

## ✅ CHECKLIST VALIDATION

- [ ] Notebook 05 exécuté sans erreur
- [ ] Comptage ~2.2M lignes (sans ❌)
- [ ] Connexion Superset testée
- [ ] SQL Lab exécute une requête
- [ ] 1 dataset créé
- [ ] 1 graphique créé
- [ ] 1 dashboard créé

---

## 🎓 POUR TA SOUTENANCE

**Points à démontrer** :

1. ✅ Architecture Bronze/Silver/Gold
2. ✅ ETLT pattern complet
3. ✅ Optimisations (Parquet, partitionnement)
4. ✅ RGPD (anonymisation SHA-256)
5. ✅ Enrichissements (géographie, CIM-10)
6. ✅ Star Schema (5 dims + 3 faits)
7. ✅ Benchmarks < 16s
8. ✅ **Visualisation E2E avec Superset**

**Workflow démontré** :
```
Données sources → Notebooks Jupyter → Spark → Gold Layer → Superset
```

---

**🚀 COMMENCER MAINTENANT : [FIX_RAPIDE_MAINTENANT.md](FIX_RAPIDE_MAINTENANT.md)**
