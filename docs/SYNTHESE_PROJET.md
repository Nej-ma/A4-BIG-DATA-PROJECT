# 📊 SYNTHÈSE TECHNIQUE - CHU Data Lakehouse

**Projet**: CHU Data Lakehouse (Bronze → Silver → Gold)
**Équipe**: Nejma MOUALHI | Brieuc OLIVIERI | Nicolas TAING
**Formation**: CESI FISA A4 - Big Data
**Date**: Octobre 2025

---

## 🎯 Objectif du Projet

Créer un Data Lakehouse complet pour analyser les données de santé d'un CHU, avec:
- Architecture médaillon (Bronze/Silver/Gold)
- Conformité RGPD (pseudonymisation/anonymisation)
- Star Schema pour analyse BI
- Visualisation via Apache Superset

---

## 🏗️ Architecture Technique

### Stack Technologique

| Composant | Technologie | Version | Rôle |
|-----------|-------------|---------|------|
| **Processing** | Apache Spark | 3.5.0 | Traitement distribué PySpark |
| **Storage** | MinIO | latest | Object storage S3-compatible |
| **Database** | PostgreSQL | 14 | Source + Gold layer export |
| **Notebooks** | Jupyter Lab | latest | Développement interactif |
| **BI Tool** | Apache Superset | latest | Visualisation et dashboards |
| **Orchestration** | Docker Compose | - | Gestion containers |

### Infrastructure Docker

```yaml
Services:
- chu_postgres (port 5432) - Base de données relationnelle
- chu_spark_master (port 7077) - Spark cluster master
- chu_spark_worker - Spark worker node
- chu_jupyter (port 8888) - Interface notebooks
- chu_superset (port 8088) - Interface BI
- chu_minio (port 9000, 9001) - Object storage

Volumes:
- spark/data/ - Lakehouse (Bronze/Silver/Gold)
- postgres/data/ - Base PostgreSQL persistante
- jupyter/notebooks/ - Scripts PySpark
```

---

## 📊 Sources de Données

### 1. PostgreSQL (13 tables)

| Table | Lignes | Description |
|-------|--------|-------------|
| **Patient** | ~300K | Patients du CHU |
| **Consultation** | ~1M | Consultations médicales 2015-2023 |
| **AAAA** | 82,216 | Hospitalisations (patient + diagnostic) |
| **date** | 82,216 | Dates entrée/sortie hospitalisations |
| **Diagnostic** | 15,442 | Codes CIM-10 diagnostics |
| **Professionnel_de_sante** | ~200K | Médecins et personnel |
| **Prescription** | ~1M | Prescriptions médicaments |
| **Medicaments** | ~3K | Référentiel médicaments |
| **Laboratoire** | ~500K | Analyses laboratoire |
| **Adher** | ~300K | Adhérents mutuelles |
| **Mutuelle** | ~150 | Organismes mutuelles |
| **Specialites** | ~50 | Spécialités médicales |
| **Salle** | ~500 | Salles et équipements |

### 2. Fichiers CSV (4 sources)

| Fichier | Lignes | Description |
|---------|--------|-------------|
| **deces.csv** | 25M (filtré 2019: 620K) | Décès INSEE |
| **departements.csv** | 101 | Référentiel départements |
| **etablissement_sante.csv** | ~3K | Établissements santé France |
| **satisfaction_esatis48h_2019.csv** | 8 | Scores satisfaction E-Satis |

---

## 🔄 Architecture Médaillon

### Bronze Layer (Données Brutes)

**Objectif**: Ingestion sans transformation

**Format**: Parquet compressé (snappy)

**Structure**:
```
spark/data/bronze/
├── postgres/
│   ├── Patient/ingestion_date=2025-10-22/
│   ├── Consultation/ingestion_date=2025-10-22/
│   ├── AAAA/ingestion_date=2025-10-22/
│   ├── date/ingestion_date=2025-10-22/
│   └── ... (10 autres tables)
└── csv/
    ├── deces_2019/
    ├── departements/
    ├── etablissement_sante/
    └── satisfaction_esatis48h_2019/
```

**Métadonnées ajoutées**:
- `ingestion_timestamp` (timestamp)
- `ingestion_date` (date YYYY-MM-DD)

**Volumétrie**: ~4M lignes, ~2 minutes d'ingestion

---

### Silver Layer (Données Nettoyées)

**Objectif**: Nettoyage + Pseudonymisation RGPD

**Transformations appliquées**:

1. **Pseudonymisation SHA-256** (réversible avec sel):
   ```python
   # Hash PII avec sel constant
   hash_udf = udf(lambda x: hashlib.sha256(
       (str(x) + SALT).encode()
   ).hexdigest(), StringType())

   df_clean = df_raw.withColumn(
       "nom_hash", hash_udf(col("nom"))
   ).drop("nom")
   ```

2. **Formatage dates**:
   - Unification format: `yyyy-MM-dd`
   - Conversion types: string → date/timestamp

3. **Nettoyage valeurs**:
   - Suppression nulls critiques
   - Trim espaces
   - Normalisation casse

4. **Suppression colonnes sensibles**:
   - Adresses complètes
   - Numéros sécurité sociale
   - Emails personnels

**Structure**:
```
spark/data/silver/
├── patient_clean/
├── consultation_clean/
├── hospitalisation_clean/
├── diagnostic_clean/
├── professionnel_clean/
├── prescription_clean/
├── laboratoire_clean/
├── adher_clean/
├── mutuelle_clean/
├── deces_2019_clean/
├── departements_clean/
├── etablissement_sante_clean/
└── satisfaction_clean/
```

**Volumétrie**: ~3.5M lignes, ~3 minutes de traitement

---

### Gold Layer (Star Schema)

**Objectif**: Modèle dimensionnel pour analyse BI

**Architecture**: Star Schema avec 5 dimensions et 4 faits

#### Dimensions (5)

##### 1. dim_temps
```sql
Colonnes:
- id_temps (PK, format yyyyMMdd)
- date_complete
- annee, mois, jour
- nom_mois, nom_jour_semaine
- trimestre, semestre
- est_weekend (boolean)

Partitionnement: annee
Volumétrie: ~4,500 dates (2013-2025)
```

##### 2. dim_patient
```sql
Colonnes:
- id_patient_hash (PK, SHA-256)
- age_groupe (tranches: 0-18, 19-30, etc.)
- sexe
- departement_residence
- statut_mutuelle (adhérent/non)

Anonymisation:
- Nom/prénom hashés
- Adresse supprimée
- Date naissance → groupe d'âge

Volumétrie: ~300K patients
```

##### 3. dim_diagnostic
```sql
Colonnes:
- code_diag (PK, code CIM-10)
- libelle
- categorie
- gravite

Volumétrie: 15,442 diagnostics
```

##### 4. dim_professionnel
```sql
Colonnes:
- id_professionnel_hash (PK, SHA-256)
- specialite
- type_professionnel (médecin, infirmier, etc.)
- annees_experience_groupe

Anonymisation:
- Nom/prénom hashés
- Identifiants RPPS pseudonymisés

Volumétrie: ~200K professionnels
```

##### 5. dim_etablissement
```sql
Colonnes:
- code_etablissement (PK, FINESS)
- nom_etablissement
- type_etablissement (CHU, clinique, etc.)
- departement
- region
- capacite_lits

Volumétrie: ~3K établissements
```

---

#### Tables de Faits (4)

##### 1. fait_consultation
```sql
Clés étrangères:
- id_temps (FK → dim_temps)
- id_patient (FK → dim_patient)
- id_professionnel (FK → dim_professionnel)
- code_diag (FK → dim_diagnostic)

Mesures:
- nb_consultations (COUNT)
- duree_consultation_minutes

Partitionnement: annee, mois
Volumétrie: 1,027,157 consultations (2015-2023)
```

##### 2. fait_hospitalisation (DÉCOUVERT!)
```sql
Source: Tables AAAA + date (jointure par position)

Clés étrangères:
- id_temps_entree (FK → dim_temps)
- id_temps_sortie (FK → dim_temps)
- id_patient (FK → dim_patient)
- code_diag (FK → dim_diagnostic)

Mesures:
- nb_hospitalisations (COUNT)
- duree_sejour_jours (date_sortie - date_entree)
- duree_moyenne_sejour (AVG)

Partitionnement: annee, mois (date entrée)
Volumétrie: 82,216 hospitalisations (2013-2025)
Durée moyenne: ~1 jour
```

##### 3. fait_deces
```sql
Source: CSV INSEE filtré 2019

Clés étrangères:
- id_temps (FK → dim_temps)
- id_patient_hash (hors dim_patient, anonyme)

Mesures:
- nb_deces (COUNT)
- age_deces
- age_moyen_deces (AVG)

Anonymisation complète:
- Hashing irréversible
- Pas de lien direct avec dim_patient
- Agrégations uniquement

Partitionnement: annee, mois
Volumétrie: 620,625 décès (2019 uniquement)
```

##### 4. fait_satisfaction
```sql
Source: E-Satis 2019

Clés étrangères:
- id_temps (FK → dim_temps)
- code_etablissement (FK → dim_etablissement)

Mesures:
- score_satisfaction (0-100)
- nb_repondants
- score_moyen (AVG)

Partitionnement: annee
Volumétrie: 8 établissements (2019)
```

---

## 🔐 Conformité RGPD

### Stratégie par Layer

| Layer | Approche | Réversibilité | Accès |
|-------|----------|---------------|-------|
| **Bronze** | Données brutes | Oui (originales) | Restreint |
| **Silver** | Pseudonymisation (SHA-256 + sel) | Oui (avec sel) | Contrôlé |
| **Gold** | Anonymisation (agrégation) | Non | Ouvert BI |

### Techniques Appliquées

#### Pseudonymisation (Silver)
```python
SALT = "CHU_SECRET_KEY_2025"

def pseudonymize(value):
    return hashlib.sha256(
        (str(value) + SALT).encode()
    ).hexdigest()

# Application
df = df.withColumn("nom_hash", pseudonymize_udf(col("nom")))
```

#### Anonymisation (Gold)
1. **Suppression identifiants directs**: Nom, prénom, adresse
2. **Généralisation**: Date naissance → groupe d'âge
3. **Agrégations**: Statistiques au lieu de lignes individuelles
4. **K-anonymat**: Groupes de minimum K patients

---

## 📈 Performances

### Temps d'Exécution

| Notebook | Étape | Temps | Volumétrie |
|----------|-------|-------|------------|
| **01 - Bronze** | Extraction PostgreSQL | ~1.5 min | 13 tables, ~3M lignes |
| **01 - Bronze** | Extraction CSV (2019) | ~0.5 min | 4 fichiers, 620K lignes |
| **02 - Silver** | Nettoyage | ~2 min | 13 tables, ~3.5M lignes |
| **02 - Silver** | Pseudonymisation | ~1 min | SHA-256 sur 500K PII |
| **03 - Gold** | Dimensions | ~1 min | 5 dimensions, ~525K lignes |
| **03 - Gold** | Faits | ~2 min | 4 faits, ~2.9M lignes |
| **06 - Export** | PostgreSQL export | ~3 min | 9 tables Gold |
| **TOTAL** | Pipeline complet | **~11 min** | Bronze → PostgreSQL |

### Optimisations Appliquées

1. **Filtrage précoce**: Décès 2019 uniquement (98% réduction: 25M → 620K)
2. **Partitionnement**: Par année/mois (pruning automatique)
3. **Compression**: Snappy parquet (ratio ~5:1)
4. **Repartitioning**: Équilibrage partitions Spark
5. **Broadcast joins**: Pour petites dimensions (<10MB)

---

## 🎓 Conformité Livrable 1

### Exigences Livrables

✅ **4 Tables de Faits**:
1. fait_consultation
2. fait_hospitalisation
3. fait_deces
4. fait_satisfaction

✅ **5 Dimensions minimum**:
1. dim_temps
2. dim_patient
3. dim_diagnostic
4. dim_professionnel
5. dim_etablissement

✅ **Star Schema**: Modèle dimensionnel complet

✅ **RGPD**: Pseudonymisation Silver + Anonymisation Gold

✅ **Export PostgreSQL**: 9 tables dans schema `gold`

✅ **Visualisation BI**: Apache Superset connecté

---

## 🔍 Découvertes Techniques

### 1. Tables AAAA + date (Hospitalisation)

**Problème initial**: Pas de table évidente d'hospitalisation

**Investigation**:
- Analyse systématique des 13 tables PostgreSQL
- Découverte de 2 tables avec exactement 82,216 lignes
- AAAA: Patient (Num) + Diagnostic (Code_diag)
- date: Dates entrée (date1) + sortie (date2)

**Solution**: Jointure par position (row_id)
```python
df_aaaa_idx = df_aaaa.withColumn("row_id", monotonically_increasing_id())
df_date_idx = df_date.withColumn("row_id", monotonically_increasing_id())
df_hospit = df_aaaa_idx.join(df_date_idx, "row_id", "inner")
```

✅ Validation: 100% match sur Patient.Id_patient et Diagnostic.Code_diag

### 2. Filtrage Décès 2019

**Problème initial**: 25M lignes causaient timeout (3+ minutes)

**Analyse**:
- Livrable 1 demande analyse 2019
- 98% des données inutiles (1919-2018, 2020-2023)

**Solution**: Filtrage précoce
```python
df_deces = df_deces_raw.filter(col("date_deces").startswith("2019"))
```

**Résultat**: 620K lignes, 40 secondes (-85% temps)

### 3. Erreur Colonne "datdec"

**Erreur**: `UNRESOLVED_COLUMN: datdec`

**Cause**: CSV utilise `date_deces` pas `datdec`

**Fix**: Lecture schéma CSV avant filtrage
```python
# Afficher colonnes disponibles
df_deces_raw.printSchema()
# Colonnes: [nom, prenom, sexe, date_naissance, date_deces, ...]

# Utiliser le bon nom
df_filtered = df_deces_raw.filter(col("date_deces").startswith("2019"))
```

---

## 📊 Requêtes SQL Utiles

### Statistiques Globales
```sql
-- Volume par table de fait
SELECT
    'fait_consultation' as table_name,
    COUNT(*) as total_lignes,
    MIN(annee) as annee_min,
    MAX(annee) as annee_max
FROM gold.fait_consultation
UNION ALL
SELECT 'fait_hospitalisation', COUNT(*), MIN(annee), MAX(annee)
FROM gold.fait_hospitalisation
UNION ALL
SELECT 'fait_deces', COUNT(*), MIN(annee), MAX(annee)
FROM gold.fait_deces
UNION ALL
SELECT 'fait_satisfaction', COUNT(*), MIN(annee), MAX(annee)
FROM gold.fait_satisfaction;
```

### Analyse Consultations
```sql
-- Consultations par spécialité et année
SELECT
    p.specialite,
    t.annee,
    COUNT(*) as nb_consultations,
    COUNT(DISTINCT c.id_patient) as patients_uniques,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY t.annee), 2) as pct_annee
FROM gold.fait_consultation c
JOIN gold.dim_professionnel p ON c.id_professionnel = p.id_professionnel_hash
JOIN gold.dim_temps t ON c.id_temps = t.id_temps
GROUP BY p.specialite, t.annee
ORDER BY t.annee DESC, nb_consultations DESC;
```

### Analyse Hospitalisations
```sql
-- Durée moyenne séjour par diagnostic
SELECT
    d.categorie,
    d.libelle,
    COUNT(*) as nb_hospitalisations,
    ROUND(AVG(h.duree_sejour_jours), 2) as duree_moyenne_jours,
    MIN(h.duree_sejour_jours) as duree_min,
    MAX(h.duree_sejour_jours) as duree_max
FROM gold.fait_hospitalisation h
JOIN gold.dim_diagnostic d ON h.code_diag = d.code_diag
GROUP BY d.categorie, d.libelle
HAVING COUNT(*) >= 100
ORDER BY nb_hospitalisations DESC
LIMIT 20;
```

### Analyse Décès 2019
```sql
-- Décès par mois et tranche d'âge
SELECT
    t.mois,
    t.nom_mois,
    CASE
        WHEN d.age_deces < 18 THEN '0-17 ans'
        WHEN d.age_deces < 65 THEN '18-64 ans'
        WHEN d.age_deces < 85 THEN '65-84 ans'
        ELSE '85+ ans'
    END as tranche_age,
    COUNT(*) as nb_deces,
    ROUND(AVG(d.age_deces), 1) as age_moyen
FROM gold.fait_deces d
JOIN gold.dim_temps t ON d.id_temps = t.id_temps
GROUP BY t.mois, t.nom_mois, tranche_age
ORDER BY t.mois, tranche_age;
```

---

## 🎨 Dashboards Superset Recommandés

### Dashboard 1: Vue d'Ensemble CHU
- KPI: Total consultations, hospitalisations, taux occupation
- Graphique: Évolution consultations par mois (2015-2023)
- Camembert: Répartition consultations par spécialité
- Tableau: Top 10 diagnostics

### Dashboard 2: Analyse Hospitalisations
- KPI: Durée moyenne séjour, nb hospitalisations
- Graphique: Durée séjour par catégorie diagnostic
- Heatmap: Hospitalisations par mois/année
- Tableau: Statistiques par diagnostic

### Dashboard 3: Mortalité 2019
- KPI: Total décès, âge moyen décès
- Graphique: Évolution mensuelle décès 2019
- Pyramide: Répartition par tranche d'âge
- Carte: Décès par département

### Dashboard 4: Satisfaction E-Satis
- KPI: Score moyen satisfaction
- Graphique: Comparaison établissements
- Tableau: Détails par établissement

---

## 🚀 Améliorations Futures

### Court Terme
1. Ajouter `dim_medicament` et `fait_prescription`
2. Créer `fait_laboratoire` pour analyses bio
3. Implémenter Quality Checks (Great Expectations)
4. Ajouter logging structuré (JSON)

### Moyen Terme
1. Migration vers Databricks ou Snowflake
2. Orchestration Airflow pour pipeline automatique
3. CDC (Change Data Capture) pour Bronze incrémental
4. Data Catalog (Apache Atlas)

### Long Terme
1. Machine Learning: Prédiction durée hospitalisation
2. Real-time streaming (Kafka + Spark Structured Streaming)
3. Data Mesh: Domaines métier séparés
4. MLOps: Modèles en production

---

## 📚 Ressources et Références

### Documentation Technique
- Apache Spark 3.5: https://spark.apache.org/docs/3.5.0/
- PostgreSQL 14: https://www.postgresql.org/docs/14/
- Apache Superset: https://superset.apache.org/docs/

### Conformité RGPD
- CNIL: Guide pseudonymisation
- RGPD Article 4(5): Définition pseudonymisation
- K-anonymat: Sweeney, L. (2002)

### Architecture Data
- Data Lakehouse (Databricks): https://databricks.com/blog/2020/01/30/what-is-a-data-lakehouse.html
- Medallion Architecture: Bronze/Silver/Gold layers
- Kimball Dimensional Modeling: The Data Warehouse Toolkit

---

## ✅ Checklist Validation Projet

**Fonctionnalités**:
- [x] Pipeline Bronze/Silver/Gold opérationnel
- [x] 4 tables de faits créées et peuplées
- [x] 5 dimensions créées et peuplées
- [x] Star Schema complet et cohérent
- [x] Pseudonymisation Silver (SHA-256)
- [x] Anonymisation Gold (agrégations)
- [x] Export PostgreSQL fonctionnel
- [x] Superset connecté et requêtes testées

**Documentation**:
- [x] Guide d'utilisation complet
- [x] Synthèse technique (ce document)
- [x] Troubleshooting guide
- [x] Requêtes SQL exemples
- [x] Architecture diagrammes

**Qualité Code**:
- [x] Notebooks commentés et structurés
- [x] Gestion erreurs (try/except)
- [x] Logs informatifs
- [x] Code reproductible

**Livrables**:
- [x] Docker Compose fonctionnel
- [x] Notebooks exécutables
- [x] Données Gold dans PostgreSQL
- [x] Documentation consolidée

---

**🎉 Projet Livrable 2 - COMPLET ET VALIDÉ**
