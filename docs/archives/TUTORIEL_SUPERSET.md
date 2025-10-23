# 🎨 TUTORIEL SUPERSET - CHU Data Lakehouse

**Objectif** : Connecter Apache Superset au Data Lakehouse et créer des dashboards analytiques

**Auteurs** : Nejma MOUALHI | Brieuc OLIVIERI | Nicolas TAING

---

## 📋 TABLE DES MATIÈRES

1. [Accès à Superset](#1-accès-à-superset)
2. [Configuration de la connexion Spark SQL](#2-configuration-de-la-connexion-spark-sql)
3. [Création des datasets](#3-création-des-datasets)
4. [Création de visualisations](#4-création-de-visualisations)
5. [Création d'un dashboard](#5-création-dun-dashboard)
6. [Exemples de requêtes métier](#6-exemples-de-requêtes-métier)

---

## 1. ACCÈS À SUPERSET

### 1.1 Ouvrir Superset dans le navigateur

🌐 **URL** : http://localhost:8088

### 1.2 Se connecter

**Identifiants par défaut** :
- **Username** : `admin`
- **Password** : `admin`

![Login Screen](https://superset.apache.org/img/screenshots/login.png)

✅ **Vérification** : Vous devez voir le tableau de bord Superset avec :
- Menu en haut : Data, Charts, Dashboards, SQL Lab
- Liste des exemples de dashboards (si installation par défaut)

---

## 2. CONFIGURATION DE LA CONNEXION SPARK SQL

### 2.1 Accéder aux paramètres de connexion

1. Cliquer sur **Settings** (⚙️ en haut à droite)
2. Sélectionner **Database Connections**
3. Cliquer sur **+ DATABASE** (bouton bleu en haut à droite)

### 2.2 Sélectionner Apache Spark SQL

Dans la fenêtre "Connect a database" :

1. **SUPPORTED DATABASES** → Rechercher "**Apache Spark SQL**"
2. Cliquer sur l'icône **Apache Spark SQL**

### 2.3 Configuration de la connexion

#### Option A : Via l'interface graphique (recommandé)

**Onglet "BASIC"** :
```
HOST: spark-master
PORT: 10000
DATABASE NAME: default
USERNAME: (laisser vide)
PASSWORD: (laisser vide)
```

**Display Name** : `CHU_Gold_Layer`

**Additional Settings** :
- ✅ Expose database in SQL Lab
- ✅ Allow CREATE TABLE AS
- ✅ Allow DML

#### Option B : Via SQLAlchemy URI (avancé)

Si l'option A ne fonctionne pas, utiliser directement l'URI :

```
hive://spark-master:10000/default
```

**Ou avec PyHive** :
```
hive://spark-master:10000/default?auth=NOSASL
```

### 2.4 Tester la connexion

1. Cliquer sur **TEST CONNECTION** en bas
2. ✅ Vous devez voir : "**Connection looks good!**"
3. Cliquer sur **CONNECT**

---

## 3. CRÉATION DES DATASETS

### 3.1 Accéder à SQL Lab

1. Menu principal → **SQL Lab** → **SQL Editor**
2. Sélectionner la base **CHU_Gold_Layer**

### 3.2 Charger les tables Gold depuis les fichiers Parquet

Dans SQL Lab, exécuter ces commandes pour créer des **tables externes Spark SQL** :

```sql
-- 1. DIMENSION TEMPS
CREATE EXTERNAL TABLE IF NOT EXISTS dim_temps (
    id_temps STRING,
    date_complete DATE,
    annee INT,
    mois INT,
    jour INT,
    jour_semaine INT,
    nom_jour STRING,
    trimestre INT,
    semaine_annee INT
)
STORED AS PARQUET
LOCATION '/home/jovyan/data/gold/dim_temps';

-- 2. DIMENSION PATIENT
CREATE EXTERNAL TABLE IF NOT EXISTS dim_patient (
    id_patient STRING,
    sexe STRING,
    ville STRING,
    code_postal STRING,
    date_naissance DATE,
    age INT,
    tranche_age STRING
)
STORED AS PARQUET
LOCATION '/home/jovyan/data/gold/dim_patient';

-- 3. DIMENSION DIAGNOSTIC
CREATE EXTERNAL TABLE IF NOT EXISTS dim_diagnostic (
    code_diag STRING,
    libelle STRING,
    categorie STRING
)
STORED AS PARQUET
LOCATION '/home/jovyan/data/gold/dim_diagnostic';

-- 4. DIMENSION PROFESSIONNEL
CREATE EXTERNAL TABLE IF NOT EXISTS dim_professionnel (
    id_prof STRING,
    nom_specialite STRING,
    ville STRING,
    code_postal STRING
)
STORED AS PARQUET
LOCATION '/home/jovyan/data/gold/dim_professionnel';

-- 5. DIMENSION ETABLISSEMENT
CREATE EXTERNAL TABLE IF NOT EXISTS dim_etablissement (
    finess STRING,
    siret STRING,
    nom STRING,
    ville STRING,
    code_postal STRING,
    telephone STRING,
    email STRING,
    code_departement STRING,
    libelle_departement STRING,
    libelle_region STRING,
    abv_region STRING
)
STORED AS PARQUET
LOCATION '/home/jovyan/data/gold/dim_etablissement';

-- 6. FAIT CONSULTATION (partitionné)
CREATE EXTERNAL TABLE IF NOT EXISTS fait_consultation (
    id_consultation STRING,
    id_temps STRING,
    id_patient STRING,
    code_diag STRING,
    id_prof STRING,
    cout DECIMAL(10,2),
    duree_minutes INT,
    urgence BOOLEAN,
    annee INT,
    mois INT
)
PARTITIONED BY (annee INT, mois INT)
STORED AS PARQUET
LOCATION '/home/jovyan/data/gold/fait_consultation';

-- Réparer les partitions (important!)
MSCK REPAIR TABLE fait_consultation;
```

### 3.3 Vérifier les tables créées

```sql
SHOW TABLES;
```

✅ Vous devez voir 6 tables :
- dim_temps
- dim_patient
- dim_diagnostic
- dim_professionnel
- dim_etablissement
- fait_consultation

### 3.4 Tester une requête

```sql
SELECT
    t.annee,
    COUNT(*) as nb_consultations,
    COUNT(DISTINCT f.id_patient) as patients_uniques
FROM fait_consultation f
JOIN dim_temps t ON f.id_temps = t.id_temps
GROUP BY t.annee
ORDER BY t.annee;
```

✅ **Résultat attendu** : 9 lignes (années 2015-2023)

### 3.5 Enregistrer les datasets

Pour chaque table, aller dans **Data** → **Datasets** → **+ DATASET** :

1. **Database** : CHU_Gold_Layer
2. **Schema** : default
3. **Table** : Sélectionner la table (ex: `dim_patient`)
4. Cliquer **ADD**

Répéter pour toutes les 6 tables.

---

## 4. CRÉATION DE VISUALISATIONS

### 4.1 Créer un graphique : Consultations par année

1. Menu **Charts** → **+ CHART**
2. **Dataset** : `fait_consultation`
3. **Chart Type** : **Bar Chart**

**Configuration** :
- **TIME COLUMN** : `annee` (ou créer une jointure avec dim_temps)
- **METRICS** : `COUNT(*)`
- **GROUP BY** : Aucun (déjà groupé par année)
- **FILTERS** : Aucun

Cliquer **UPDATE CHART** → **SAVE**

**Nom** : `Consultations par année`

### 4.2 Top 10 Diagnostics (Pie Chart)

1. **+ CHART** → Dataset: `fait_consultation`
2. **Chart Type** : **Pie Chart**

**Configuration** :
```
DIMENSIONS : code_diag (ou jointure avec dim_diagnostic.libelle)
METRIC : COUNT(*)
SORT BY : metric descending
ROW LIMIT : 10
```

### 4.3 Consultations par sexe et âge (Heatmap)

1. **+ CHART** → Dataset: `fait_consultation` (avec jointure)
2. **Chart Type** : **Heatmap**

**SQL personnalisé** (via Virtual Dataset) :
```sql
SELECT
    p.sexe,
    p.tranche_age,
    COUNT(*) as nb_consultations
FROM fait_consultation f
JOIN dim_patient p ON f.id_patient = p.id_patient
GROUP BY p.sexe, p.tranche_age
```

Enregistrer comme **Virtual Dataset** puis créer le Heatmap.

### 4.4 Évolution mensuelle 2019 (Line Chart)

1. **Chart Type** : **Line Chart**
2. **SQL** :
```sql
SELECT
    CONCAT(t.annee, '-', LPAD(t.mois, 2, '0')) as mois_annee,
    COUNT(*) as nb_consultations
FROM fait_consultation f
JOIN dim_temps t ON f.id_temps = t.id_temps
WHERE t.annee = 2019
GROUP BY t.annee, t.mois
ORDER BY t.mois
```

### 4.5 Top Spécialités (Bar Chart horizontal)

```sql
SELECT
    prof.nom_specialite,
    COUNT(*) as nb_consultations,
    COUNT(DISTINCT f.id_patient) as patients_differents
FROM fait_consultation f
JOIN dim_professionnel prof ON f.id_prof = prof.id_prof
WHERE prof.nom_specialite IS NOT NULL
GROUP BY prof.nom_specialite
ORDER BY nb_consultations DESC
LIMIT 10
```

---

## 5. CRÉATION D'UN DASHBOARD

### 5.1 Créer un nouveau dashboard

1. Menu **Dashboards** → **+ DASHBOARD**
2. **Title** : `CHU - Vue d'ensemble des consultations`
3. **Owners** : admin

### 5.2 Ajouter les graphiques

1. Cliquer sur **EDIT DASHBOARD** (crayon en haut à droite)
2. Onglet **CHARTS** (à gauche)
3. **Glisser-déposer** les graphiques créés précédemment
4. **Organiser** la disposition en grille

**Exemple de layout** :
```
+------------------------+------------------------+
|  Consultations/année   |   Top 10 Diagnostics  |
|     (Bar Chart)        |      (Pie Chart)       |
+------------------------+------------------------+
|           Évolution mensuelle 2019             |
|                 (Line Chart)                    |
+------------------------+------------------------+
|  Heatmap Sexe/Âge     |   Top Spécialités     |
+------------------------+------------------------+
```

### 5.3 Ajouter des filtres dashboard

1. **EDIT DASHBOARD** → **FILTERS** (onglet en haut)
2. Ajouter un filtre **Date Range** sur `dim_temps.annee`
3. Ajouter un filtre **Sexe** sur `dim_patient.sexe`
4. Appliquer aux graphiques concernés

### 5.4 Sauvegarder et publier

1. Cliquer **SAVE**
2. Tester les filtres en mode visualisation
3. Partager le lien : `http://localhost:8088/superset/dashboard/1/`

---

## 6. EXEMPLES DE REQUÊTES MÉTIER

### 6.1 Taux de consultation par établissement (2019)

```sql
SELECT
    e.nom as etablissement,
    e.ville,
    e.libelle_region as region,
    COUNT(*) as nb_consultations,
    COUNT(DISTINCT f.id_patient) as patients_uniques,
    ROUND(AVG(f.cout), 2) as cout_moyen
FROM fait_consultation f
JOIN dim_temps t ON f.id_temps = t.id_temps
JOIN dim_etablissement e ON f.id_prof IN (
    SELECT id_prof FROM dim_professionnel WHERE code_postal = e.code_postal
)
WHERE t.annee = 2019
GROUP BY e.nom, e.ville, e.libelle_region
ORDER BY nb_consultations DESC
LIMIT 20;
```

### 6.2 Taux de consultation par catégorie CIM-10

```sql
SELECT
    d.categorie,
    CASE d.categorie
        WHEN 'A' THEN 'Maladies infectieuses'
        WHEN 'C' THEN 'Tumeurs'
        WHEN 'E' THEN 'Maladies endocriniennes'
        WHEN 'I' THEN 'Maladies cardiovasculaires'
        WHEN 'J' THEN 'Maladies respiratoires'
        WHEN 'M' THEN 'Maladies musculo-squelettiques'
        WHEN 'O' THEN 'Grossesse et accouchement'
        WHEN 'S' THEN 'Traumatismes'
        ELSE 'Autres'
    END as libelle_categorie,
    COUNT(*) as nb_consultations,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as pourcentage
FROM fait_consultation f
JOIN dim_diagnostic d ON f.code_diag = d.code_diag
WHERE d.categorie IS NOT NULL
GROUP BY d.categorie
ORDER BY nb_consultations DESC;
```

### 6.3 Évolution des consultations urgentes vs normales

```sql
SELECT
    t.annee,
    t.trimestre,
    SUM(CASE WHEN f.urgence = true THEN 1 ELSE 0 END) as consultations_urgentes,
    SUM(CASE WHEN f.urgence = false THEN 1 ELSE 0 END) as consultations_normales,
    ROUND(SUM(CASE WHEN f.urgence = true THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as taux_urgence
FROM fait_consultation f
JOIN dim_temps t ON f.id_temps = t.id_temps
GROUP BY t.annee, t.trimestre
ORDER BY t.annee, t.trimestre;
```

### 6.4 Analyse géographique : Consultations par région

```sql
SELECT
    e.libelle_region as region,
    e.abv_region,
    COUNT(*) as nb_consultations,
    COUNT(DISTINCT f.id_patient) as patients_uniques,
    ROUND(AVG(f.cout), 2) as cout_moyen,
    ROUND(AVG(f.duree_minutes), 0) as duree_moyenne_min
FROM fait_consultation f
JOIN dim_professionnel prof ON f.id_prof = prof.id_prof
JOIN dim_etablissement e ON prof.code_postal = e.code_postal
WHERE e.libelle_region IS NOT NULL
GROUP BY e.libelle_region, e.abv_region
ORDER BY nb_consultations DESC;
```

### 6.5 Profil patients : Distribution par âge et sexe

```sql
SELECT
    p.sexe,
    p.tranche_age,
    COUNT(DISTINCT p.id_patient) as nb_patients,
    COUNT(*) as nb_consultations,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT p.id_patient), 1) as consultations_par_patient
FROM fait_consultation f
JOIN dim_patient p ON f.id_patient = p.id_patient
GROUP BY p.sexe, p.tranche_age
ORDER BY p.sexe, p.tranche_age;
```

---

## 7. DASHBOARD AVANCÉ : KPI CHU

### 7.1 Créer des métriques clés (Big Number)

**Chart Type** : **Big Number**

#### KPI 1 : Total consultations
```sql
SELECT COUNT(*) FROM fait_consultation
```

#### KPI 2 : Patients uniques
```sql
SELECT COUNT(DISTINCT id_patient) FROM fait_consultation
```

#### KPI 3 : Coût total
```sql
SELECT SUM(cout) FROM fait_consultation
```

#### KPI 4 : Durée moyenne
```sql
SELECT AVG(duree_minutes) FROM fait_consultation
```

### 7.2 Layout dashboard KPI

```
+----------+----------+----------+----------+
|   Total  | Patients |   Coût   |  Durée   |
|1,027,157 |  100,000 | 5.2M €   | 45 min   |
+----------+----------+----------+----------+
|                                           |
|        Graphique évolution annuelle       |
|                                           |
+-------------------------------------------+
|  Top Diagnostics  |  Top Spécialités     |
+-------------------------------------------+
```

---

## 8. TROUBLESHOOTING

### 8.1 Erreur "Connection refused"

**Solution** : Vérifier que Spark Thrift Server est démarré

```bash
docker exec -it chu_spark_master /bin/bash
$SPARK_HOME/sbin/start-thriftserver.sh --master spark://spark-master:7077
```

### 8.2 Tables vides après création

**Solution** : Exécuter `MSCK REPAIR TABLE` pour les tables partitionnées

```sql
MSCK REPAIR TABLE fait_consultation;
```

### 8.3 Performances lentes

**Solutions** :
1. Ajouter des filtres sur les années (partitions)
2. Limiter les résultats (LIMIT 1000)
3. Utiliser des vues matérialisées pour les requêtes complexes

### 8.4 Superset ne démarre pas

```bash
# Recréer Superset
docker-compose restart superset

# Vérifier les logs
docker logs chu_superset --tail 100
```

---

## 9. EXPORT ET PARTAGE

### 9.1 Exporter un dashboard en PDF

1. Ouvrir le dashboard
2. Cliquer sur **...** (3 points) → **Download as PDF**

### 9.2 Partager un dashboard

1. **EDIT DASHBOARD** → **PUBLISH**
2. Copier l'URL : `http://localhost:8088/superset/dashboard/1/`

### 9.3 Scheduler des rapports (Superset 2.0+)

1. Dashboard → **...** → **Email Reports**
2. Configurer la fréquence (quotidien, hebdomadaire)
3. Ajouter destinataires

---

## ✅ CHECKLIST VALIDATION

- [ ] Superset accessible sur http://localhost:8088
- [ ] Connexion `CHU_Gold_Layer` configurée
- [ ] 6 tables créées (5 dimensions + 1 fait)
- [ ] `MSCK REPAIR TABLE` exécuté
- [ ] Au moins 5 graphiques créés
- [ ] 1 dashboard complet avec filtres
- [ ] KPIs affichés correctement
- [ ] Export PDF fonctionnel

---

## 📚 RESSOURCES

- **Documentation Superset** : https://superset.apache.org/docs/intro
- **Galerie de graphiques** : https://superset.apache.org/docs/using-superset/exploring-data
- **Apache Spark SQL** : https://spark.apache.org/sql/

---

**🎓 Projet prêt pour la démonstration Livrable 2 !**

**Workflow complet validé** :
```
CSV/PostgreSQL → Jupyter (Bronze) → Silver → Gold → Superset Dashboards
```
