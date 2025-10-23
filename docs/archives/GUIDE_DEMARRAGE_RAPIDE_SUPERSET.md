# 🚀 GUIDE DÉMARRAGE RAPIDE - SUPERSET

**Temps estimé** : 10 minutes

---

## 📋 CHECKLIST PRÉALABLE

Avant de commencer, vérifier que :

- ✅ Docker containers en cours d'exécution :
  ```bash
  docker ps
  ```
  Vous devez voir `chu_superset` et `chu_spark_master` avec status `Up`

- ✅ Notebooks 01-02-03 exécutés avec succès (données Gold créées)

- ✅ Spark Thrift Server démarré :
  ```bash
  docker exec chu_spark_master ps aux | grep -i thrift
  ```
  Si vide, démarrer avec :
  ```bash
  docker exec chu_spark_master bash -c '$SPARK_HOME/sbin/start-thriftserver.sh --master spark://spark-master:7077 --hiveconf hive.server2.thrift.port=10000 --hiveconf hive.server2.thrift.bind.host=0.0.0.0'
  ```

---

## 🎯 ÉTAPE 1 : Créer les tables Spark SQL (2 min)

### Ouvrir Jupyter Lab

🌐 http://localhost:8888

### Exécuter le notebook 05_Setup_Superset.ipynb

1. **notebooks/** → **05_Setup_Superset.ipynb**
2. **Kernel** → **Restart & Run All**
3. Attendre que toutes les cellules soient exécutées (~1 min)

### ✅ Vérifier le résultat

La dernière cellule doit afficher :
```
✅ Toutes les tables sont accessibles !

  dim_temps                 :      4,748 lignes
  dim_patient               :    100,000 lignes
  dim_diagnostic            :        100 lignes
  dim_professionnel         :    100,000 lignes
  dim_etablissement         :      3,500 lignes
  fait_consultation         :  1,027,157 lignes
  ────────────────────────────────────────────
  TOTAL                     :  1,235,505 lignes
```

---

## 🎨 ÉTAPE 2 : Configurer Superset (5 min)

### 2.1 Ouvrir Superset

🌐 http://localhost:8088

**Identifiants** :
- Username: `admin`
- Password: `admin`

### 2.2 Ajouter la connexion Database

1. Cliquer sur **⚙️ Settings** (en haut à droite)
2. **Database Connections**
3. **+ DATABASE** (bouton bleu)

### 2.3 Configurer la connexion

**Méthode recommandée** : SQLAlchemy URI

1. Sélectionner **"SUPPORTED DATABASES"** → **"Apache Spark SQL"**
2. Onglet **"SQLALCHEMY URI"**
3. Copier-coller cette URI :
   ```
   hive://spark-master:10000/default
   ```
4. **Display Name** : `CHU_Gold_Layer`
5. Cocher :
   - ✅ Expose database in SQL Lab
   - ✅ Allow CREATE TABLE AS
   - ✅ Allow DML
6. Cliquer **TEST CONNECTION**
7. ✅ Si "Connection looks good!" → Cliquer **CONNECT**

### ⚠️ Si erreur de connexion

**Erreur** : "Could not connect to database"

**Solutions** :

1. **Vérifier que Thrift Server tourne** :
   ```bash
   docker exec chu_spark_master ps aux | grep thrift
   ```

2. **Essayer une URI alternative** :
   ```
   hive://spark-master:10000/default?auth=NOSASL
   ```

3. **Redémarrer Thrift Server** :
   ```bash
   docker exec chu_spark_master bash -c '$SPARK_HOME/sbin/stop-thriftserver.sh'
   docker exec chu_spark_master bash -c '$SPARK_HOME/sbin/start-thriftserver.sh --master spark://spark-master:7077'
   ```

---

## 📊 ÉTAPE 3 : Tester SQL Lab (1 min)

### 3.1 Ouvrir SQL Lab

Menu principal → **SQL Lab** → **SQL Editor**

### 3.2 Sélectionner la base de données

Dans la barre supérieure :
- **DATABASE** : `CHU_Gold_Layer`
- **SCHEMA** : `default`

### 3.3 Exécuter une requête test

Copier-coller dans l'éditeur :

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

Cliquer **RUN** (ou Ctrl+Entrée)

### ✅ Résultat attendu

```
annee | nb_consultations | patients_uniques
------|------------------|------------------
2015  |     33,896       |     28,581
2016  |    184,308       |     85,272
2017  |    133,403       |     74,201
...
```

**Si vous voyez ces résultats → PARFAIT !** Superset est connecté au Data Lakehouse.

---

## 🎨 ÉTAPE 4 : Créer votre premier graphique (2 min)

### 4.1 Créer un Dataset

1. Menu **Data** → **Datasets**
2. **+ DATASET**
3. **Database** : `CHU_Gold_Layer`
4. **Schema** : `default`
5. **Table** : `fait_consultation`
6. **ADD**

### 4.2 Créer un graphique

1. Menu **Charts** → **+ CHART**
2. **Dataset** : `fait_consultation`
3. **Chart Type** : **Big Number with Trendline**
4. **Configuration** :
   - **METRIC** : `COUNT(*)`
   - **TIME COLUMN** : (laisser vide pour l'instant)
5. Cliquer **UPDATE CHART**

### ✅ Résultat

Vous devriez voir : **1,027,157** (nombre total de consultations)

### 4.3 Sauvegarder

1. Cliquer **SAVE** (en haut à droite)
2. **Chart Name** : `Total Consultations`
3. **Add to Dashboard** : Créer un nouveau dashboard "CHU Overview"
4. **SAVE & GO TO DASHBOARD**

---

## 📈 ÉTAPE 5 : Exemples de visualisations rapides

### 5.1 Consultations par année (Bar Chart)

**SQL personnalisé** (Data → SQL Lab → **Save as Dataset**) :

```sql
SELECT
    t.annee,
    COUNT(*) as nb_consultations
FROM fait_consultation f
JOIN dim_temps t ON f.id_temps = t.id_temps
GROUP BY t.annee
ORDER BY t.annee
```

**Chart Type** : Bar Chart
- **X-AXIS** : `annee`
- **METRICS** : `SUM(nb_consultations)`

### 5.2 Top Diagnostics (Pie Chart)

```sql
SELECT
    d.categorie,
    CASE d.categorie
        WHEN 'A' THEN 'Maladies infectieuses'
        WHEN 'C' THEN 'Tumeurs'
        WHEN 'I' THEN 'Cardiovasculaires'
        WHEN 'J' THEN 'Respiratoires'
        WHEN 'M' THEN 'Musculo-squelettiques'
        WHEN 'O' THEN 'Grossesse'
        WHEN 'S' THEN 'Traumatismes'
        ELSE 'Autres'
    END as libelle,
    COUNT(*) as nb_consultations
FROM fait_consultation f
JOIN dim_diagnostic d ON f.code_diag = d.code_diag
WHERE d.categorie IS NOT NULL
GROUP BY d.categorie
ORDER BY nb_consultations DESC
LIMIT 8
```

**Chart Type** : Pie Chart
- **DIMENSIONS** : `libelle`
- **METRIC** : `SUM(nb_consultations)`

### 5.3 Répartition Homme/Femme (Donut Chart)

```sql
SELECT
    p.sexe,
    COUNT(*) as nb_consultations
FROM fait_consultation f
JOIN dim_patient p ON f.id_patient = p.id_patient
GROUP BY p.sexe
```

**Chart Type** : Pie Chart (ou Donut)
- **DIMENSIONS** : `sexe`
- **METRIC** : `SUM(nb_consultations)`

---

## 🎯 ÉTAPE 6 : Dashboard complet (optionnel)

Voir **TUTORIEL_SUPERSET.md** pour créer un dashboard avancé avec :

- 📊 KPIs (Total consultations, Patients, Coût moyen)
- 📈 Évolutions temporelles
- 🗺️ Cartes géographiques (par région)
- 🏥 Top établissements
- 👨‍⚕️ Top spécialités
- 📋 Tableaux détaillés

---

## ❌ TROUBLESHOOTING

### Problème 1 : "No database found"

**Cause** : Connexion database pas configurée

**Solution** : Reprendre Étape 2.2

---

### Problème 2 : "Table not found"

**Cause** : Tables Spark SQL pas créées

**Solution** : Exécuter Notebook 05_Setup_Superset.ipynb (Étape 1)

---

### Problème 3 : "Connection timeout"

**Cause** : Thrift Server pas démarré

**Solution** :
```bash
docker exec chu_spark_master bash -c '$SPARK_HOME/sbin/start-thriftserver.sh --master spark://spark-master:7077 --hiveconf hive.server2.thrift.port=10000'
```

Attendre 10 secondes puis tester la connexion.

---

### Problème 4 : Tables vides (0 lignes)

**Cause** : Partitions pas réparées pour `fait_consultation`

**Solution** : Dans SQL Lab, exécuter :
```sql
MSCK REPAIR TABLE fait_consultation;
```

---

### Problème 5 : Superset ne démarre pas

**Solution** :
```bash
docker-compose restart superset
docker logs chu_superset --tail 50
```

---

## ✅ CHECKLIST FINALE

Avant de déclarer le workflow complet validé :

- [ ] Superset accessible sur http://localhost:8088
- [ ] Connexion `CHU_Gold_Layer` créée et testée
- [ ] SQL Lab exécute des requêtes avec succès
- [ ] Au moins 1 dataset créé (fait_consultation)
- [ ] Au moins 1 graphique créé
- [ ] Au moins 1 dashboard créé

---

## 📚 POUR ALLER PLUS LOIN

### Documentation complète

Voir **TUTORIEL_SUPERSET.md** pour :
- Création des 6 datasets (dimensions + fait)
- 15+ exemples de visualisations
- Dashboards avancés avec filtres
- Requêtes métier (taux hospitalisation, satisfaction, etc.)
- Export PDF et partage

### Workflow complet E2E

```
┌──────────────┐
│ CSV Files    │ ──┐
│ PostgreSQL   │   │
└──────────────┘   │
                   ▼
         ┌──────────────────┐
         │ Jupyter Notebook │
         │ 01_Extract       │ ──► Bronze Layer (Parquet)
         └──────────────────┘
                   │
                   ▼
         ┌──────────────────┐
         │ 02_Transform     │ ──► Silver Layer (Cleaned + RGPD)
         └──────────────────┘
                   │
                   ▼
         ┌──────────────────┐
         │ 03_Transform     │ ──► Gold Layer (Star Schema)
         └──────────────────┘
                   │
                   ▼
         ┌──────────────────┐
         │ 05_Setup         │ ──► Spark SQL Tables
         └──────────────────┘
                   │
                   ▼
         ┌──────────────────┐
         │ Superset         │ ──► Dashboards & Analytics
         └──────────────────┘
```

**🎓 Projet 100% fonctionnel pour Livrable 2 !**

---

## 🆘 AIDE

Si problème persistant :

1. Vérifier les logs :
   ```bash
   docker logs chu_superset --tail 100
   docker logs chu_spark_master --tail 100
   ```

2. Vérifier les tables Spark :
   ```bash
   docker exec chu_spark_master spark-sql -e "SHOW TABLES"
   ```

3. Tester Thrift Server manuellement :
   ```bash
   docker exec -it chu_spark_master beeline -u jdbc:hive2://localhost:10000/default
   ```

Bonne chance ! 🚀
