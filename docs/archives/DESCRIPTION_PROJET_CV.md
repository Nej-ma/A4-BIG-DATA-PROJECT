# 📝 DESCRIPTION PROJET POUR CV/PORTFOLIO

**Projet académique Big Data - CESI FISA A4**
**Année** : 2025-2026

---

## 🎯 VERSION COURTE (pour CV)

### CHU Data Lakehouse - Architecture ETLT & Analyse de Données de Santé

**Contexte** : Projet académique Big Data visant à concevoir et implémenter un data lakehouse pour l'analyse de données de santé publique (25M+ lignes).

**Technologies** : Apache Spark, PostgreSQL, MinIO (S3), Docker, Jupyter, Python (PySpark), SQL, Architecture Medallion (Bronze/Silver/Gold), Star Schema.

**Réalisations** :
- Conception et implémentation d'un pipeline ETLT (Extract-Transform-Load-Transform) traitant 29M de lignes de données de santé
- Mise en place d'une architecture Medallion (Bronze/Silver/Gold) avec anonymisation RGPD (SHA-256)
- Création d'un modèle dimensionnel en étoile (Star Schema) : 5 dimensions et 3 tables de faits
- Optimisation des performances avec partitionnement temporel et format Parquet (10x compression vs CSV)
- Orchestration avec Docker (7 services : Spark, PostgreSQL, MinIO, Jupyter, Airflow, Superset)
- Enrichissement géographique des données (intégration référentiel départements/régions)

**Compétences développées** : Architecture Big Data, Data Engineering, SQL avancé, PySpark, RGPD, Modélisation dimensionnelle, DevOps (Docker).

---

## 📄 VERSION DÉTAILLÉE (pour portfolio/entretien)

### Titre du projet
**Data Lakehouse pour l'Analyse de Données de Santé Publique - Architecture ETLT & Conformité RGPD**

---

### Contexte et Objectifs

#### Contexte académique
- **Formation** : CESI FISA A4 - Spécialisation Big Data
- **Durée** : 6 mois (Septembre 2025 - Février 2026)
- **Équipe** : 3 personnes (Nejma MOUALHI, Brieuc OLIVIERI, Nicolas TAING)
- **Type** : Projet fil rouge - Livrable 2/3

#### Problématique métier
Concevoir un système d'analyse de données de santé publique capable de :
- Traiter et stocker de gros volumes de données hétérogènes (CSV, bases relationnelles)
- Garantir la conformité RGPD (anonymisation des données sensibles)
- Fournir des analyses décisionnelles rapides (consultations, décès, satisfaction patients)
- Permettre des analyses géographiques (par région/département)

#### Objectifs techniques
1. **Ingestion** : Extraire 29M+ lignes depuis sources hétérogènes (PostgreSQL + CSV)
2. **Transformation** : Nettoyer, anonymiser (RGPD) et modéliser les données
3. **Stockage** : Implémenter une architecture Medallion optimisée (Bronze/Silver/Gold)
4. **Performance** : Partitionnement temporel et compression Parquet pour requêtes rapides
5. **Visualisation** : Préparer les données pour dashboards BI (Superset)

---

### Architecture Technique

#### Stack technologique complète

| Couche | Technologie | Rôle |
|--------|-------------|------|
| **Compute** | Apache Spark 3.4.0 | Moteur de traitement distribué |
| **Langage** | Python (PySpark) | API Spark + logique métier |
| **Storage** | MinIO (S3-compatible) | Data Lake (Bronze/Silver/Gold) |
| **SGBD** | PostgreSQL 15 | Base opérationnelle source |
| **Dev** | Jupyter Lab | Notebooks de développement |
| **Orchestration** | Apache Airflow 2.8 | Workflow automation |
| **Visualisation** | Apache Superset | Dashboards BI |
| **Conteneurisation** | Docker Compose | Infrastructure as Code (7 services) |
| **Format** | Apache Parquet | Stockage columnaire compressé |

#### Architecture Medallion (3 couches)

```
┌────────────────────────────────────────────────────────┐
│  SOURCES (Hétérogènes)                                 │
│  • PostgreSQL : 13 tables (Patient, Consultation...)   │
│  • CSV : 4 fichiers (Établissements, Décès, Satisf.)  │
│  • Volume : 29M lignes brutes                          │
└────────────────────────────────────────────────────────┘
                        ↓ EXTRACT
┌────────────────────────────────────────────────────────┐
│  BRONZE LAYER (Raw Data)                               │
│  • Format : Parquet non partitionné                    │
│  • Rôle : Données brutes "as-is"                       │
│  • Volume : 29M lignes                                 │
└────────────────────────────────────────────────────────┘
                        ↓ TRANSFORM T1 (Conformité)
┌────────────────────────────────────────────────────────┐
│  SILVER LAYER (Cleaned & Anonymized)                   │
│  • Anonymisation : SHA-256 (noms, prénoms, emails...)  │
│  • Nettoyage : Formats dates, typage, validation       │
│  • Conformité : RGPD/HDS                               │
│  • Volume : 29M lignes nettoyées                       │
└────────────────────────────────────────────────────────┘
                        ↓ TRANSFORM T2 (Business)
┌────────────────────────────────────────────────────────┐
│  GOLD LAYER (Star Schema - Analytics-Ready)           │
│  • Modèle : Star Schema (5 dimensions, 3 faits)       │
│  • Partitionnement : Temporel (année/mois)            │
│  • Enrichissement : Géographique (régions/départements)│
│  • Volume : 2.8M lignes agrégées                       │
└────────────────────────────────────────────────────────┘
```

---

### Réalisations Détaillées

#### 1. Pipeline ETLT (Extract-Transform-Load-Transform)

**Extract (Notebook 01)**
- Extraction de **17 sources de données** :
  - 13 tables PostgreSQL (Patient : 100K, Consultation : 1M+, Professionnels : 1M+)
  - 4 fichiers CSV (Établissements : 416K, Décès : 25M, Satisfaction : 1K, Départements : 101)
- Lecture optimisée avec **Apache Spark** (parallélisation automatique)
- Sauvegarde en **Parquet** (compression ~10x vs CSV)
- **Résultat** : 29M lignes ingérées en Bronze layer

**Transform T1 - Conformité (Notebook 02)**
- **Anonymisation RGPD** :
  - Hash SHA-256 sur colonnes PII (noms, prénoms, emails, téléphones, NSS)
  - Impossible de ré-identifier les personnes
- **Nettoyage des données** :
  - Formats dates uniformes (yyyy-MM-dd)
  - Typage correct (integer, double, date)
  - Gestion valeurs nulles et doublons
- **Résultat** : 12 tables Silver conformes RGPD

**Load**
- Écriture en **Parquet compressé** (Snappy)
- Stockage dans MinIO (S3-compatible)

**Transform T2 - Modèle Métier (Notebook 03)**
- **Star Schema** pour analyses décisionnelles :
  - **5 Dimensions** :
    - `dim_temps` : Calendrier 2013-2025 (4,748 jours)
    - `dim_patient` : 100K patients anonymisés
    - `dim_diagnostic` : 15K codes CIM-10 + **catégories**
    - `dim_professionnel` : 1M+ professionnels de santé
    - `dim_etablissement` : 416K établissements + **enrichissement géographique** (région/département)
  - **3 Tables de Faits** (mesures) :
    - `fait_consultation` : 1M+ consultations (partitionné année/mois)
    - `fait_deces` : 620K décès 2019 (partitionné année/mois)
    - `fait_satisfaction` : 8 évaluations hôpitaux 2019
- **Partitionnement temporel** pour requêtes rapides (filtres sur année/mois)
- **Résultat** : 2.8M lignes prêtes pour BI

---

#### 2. Optimisations Implémentées

| Optimisation | Technologie | Gain |
|--------------|-------------|------|
| **Format Parquet** | Stockage columnaire | 10x compression vs CSV |
| **Partitionnement** | Année/Mois | Requêtes 10x plus rapides |
| **Adaptive Query Execution** | Spark SQL | Optimisation automatique |
| **Repartitionnement** | Spark | 20 partitions pour CSV 25M lignes |
| **Broadcast Join** | Spark | Jointures optimisées (petites tables) |

---

#### 3. Conformité RGPD/HDS

**Principes appliqués** :
- **Pseudonymisation** : Hash SHA-256 irréversible
- **Minimisation** : Suppression données non nécessaires
- **Séparation** : Layer Silver dédié à la conformité (avant stockage long terme)

**Données anonymisées** :
- Noms, prénoms
- Emails, téléphones
- Numéros de sécurité sociale
- Numéros d'acte de décès

**Données conservées** (non sensibles) :
- Âge, sexe, groupe sanguin
- Ville, code postal (géographie large)
- Dates de consultation/décès

---

#### 4. Enrichissement Géographique

**Problématique** : Permettre des analyses par région/département

**Solution** :
- Intégration d'un **référentiel géographique** (101 départements français)
- **Extraction du code département** depuis code postal (2 premiers chiffres)
- **Jointure avec dimension établissement** :
  ```python
  dim_etablissement.join(df_departements,
      substring(code_postal, 1, 2) == num_departement)
  ```
- **Colonnes ajoutées** :
  - `libelle_departement` (ex: "Rhône")
  - `libelle_region` (ex: "Auvergne-Rhône-Alpes")
  - `abv_region` (ex: "ARA")

**Résultat** : Analyses géographiques possibles (consultations par région, satisfaction par département, etc.)

---

#### 5. Benchmarks & Performance (Notebook 04)

**Requêtes testées** :
1. Consultations par mois (avec partitionnement)
2. Top 10 diagnostics par catégorie CIM-10
3. Consultations par professionnel
4. Analyse temporelle (trends)
5. Jointures multi-tables
6. Agrégations complexes

**Métriques mesurées** :
- Temps d'exécution moyen (3 runs)
- Nombre de lignes retournées
- Impact du partitionnement

**Graphiques générés** :
- Volumétrie par table
- Temps d'extraction par source
- Distribution dimensions vs faits

---

### Modèle de Données Final (Star Schema)

```sql
-- DIMENSIONS (Attributs descriptifs)

dim_temps (
    id_temps STRING PRIMARY KEY,  -- Format: yyyyMMdd
    date DATE,
    annee INT,
    mois INT,
    trimestre INT,
    jour_semaine STRING,
    est_weekend BOOLEAN
)

dim_patient (
    id_patient INT PRIMARY KEY,
    nom_hash STRING,           -- SHA-256
    prenom_hash STRING,        -- SHA-256
    sexe STRING,
    age INT,
    ville STRING,
    code_postal STRING,
    groupe_sanguin STRING
)

dim_diagnostic (
    code_diag STRING PRIMARY KEY,
    libelle STRING,
    categorie STRING          -- A=Infectieux, C=Cancer, etc. (CIM-10)
)

dim_professionnel (
    id_prof STRING PRIMARY KEY,
    nom STRING,
    prenom STRING,
    code_specialite STRING,
    nom_specialite STRING
)

dim_etablissement (
    finess STRING PRIMARY KEY,
    nom STRING,
    ville STRING,
    code_postal STRING,
    code_departement STRING,
    libelle_departement STRING,  -- Enrichissement géographique
    libelle_region STRING,        -- Enrichissement géographique
    abv_region STRING             -- Enrichissement géographique
)

-- FAITS (Mesures & Événements)

fait_consultation (
    id_consultation BIGINT PRIMARY KEY,
    id_patient INT,           -- FK → dim_patient
    id_prof STRING,           -- FK → dim_professionnel
    code_diag STRING,         -- FK → dim_diagnostic
    id_temps STRING,          -- FK → dim_temps
    date_consultation DATE,
    heure_debut TIMESTAMP,
    heure_fin TIMESTAMP,
    motif STRING,
    annee INT,                -- Partitionnement
    mois INT                  -- Partitionnement
)
PARTITIONED BY (annee, mois)

fait_deces (
    id_deces BIGINT PRIMARY KEY,
    nom_hash STRING,          -- SHA-256
    prenom_hash STRING,       -- SHA-256
    sexe STRING,
    date_naissance DATE,
    date_deces DATE,
    age_deces INT,
    lieu_naissance STRING,
    id_temps STRING,          -- FK → dim_temps
    annee INT,                -- Partitionnement
    mois INT                  -- Partitionnement
)
PARTITIONED BY (annee, mois)

fait_satisfaction (
    id_satisfaction BIGINT PRIMARY KEY,
    finess STRING,            -- FK → dim_etablissement
    score_global DOUBLE,
    score_accueil DOUBLE,
    score_pec_medical DOUBLE,
    taux_recommandation DOUBLE,
    nb_repondants INT,
    annee INT                 -- Partitionnement
)
PARTITIONED BY (annee)
```

---

### Cas d'Usage & Analyses Métier

#### 1. Analyse des consultations par catégorie de diagnostic

**Question métier** : Quelles sont les principales catégories de maladies traitées ?

**Requête SQL** :
```sql
SELECT
    d.categorie,
    CASE d.categorie
        WHEN 'A' THEN 'Maladies infectieuses'
        WHEN 'C' THEN 'Tumeurs malignes'
        WHEN 'I' THEN 'Système circulatoire'
        WHEN 'J' THEN 'Système respiratoire'
        WHEN 'M' THEN 'Système ostéo-articulaire'
    END as type_maladie,
    COUNT(*) as nb_consultations,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as pourcentage
FROM fait_consultation f
JOIN dim_diagnostic d ON f.code_diag = d.code_diag
WHERE d.categorie IS NOT NULL
GROUP BY d.categorie
ORDER BY nb_consultations DESC
```

**Insight** : Identifier les spécialités à renforcer

---

#### 2. Cartographie géographique de la santé

**Question métier** : Quelle région a le plus de consultations ? Le meilleur score de satisfaction ?

**Requête SQL** :
```sql
SELECT
    e.libelle_region,
    COUNT(DISTINCT f.id_consultation) as nb_consultations,
    COUNT(DISTINCT f.id_patient) as nb_patients,
    AVG(s.score_global) as score_satisfaction_moyen
FROM fait_consultation f
JOIN dim_etablissement e ON f.finess = e.finess
LEFT JOIN fait_satisfaction s ON e.finess = s.finess
WHERE e.libelle_region IS NOT NULL
GROUP BY e.libelle_region
ORDER BY nb_consultations DESC
```

**Insight** : Identifier les déserts médicaux, planifier investissements

---

#### 3. Analyse mortalité

**Question métier** : Quel est l'âge moyen de décès par département ? Tendance ?

**Requête SQL** :
```sql
SELECT
    e.libelle_departement,
    COUNT(*) as nb_deces,
    AVG(d.age_deces) as age_moyen_deces,
    MIN(d.age_deces) as age_min,
    MAX(d.age_deces) as age_max
FROM fait_deces d
LEFT JOIN dim_etablissement e ON d.code_lieu_deces = e.finess
WHERE e.libelle_departement IS NOT NULL
GROUP BY e.libelle_departement
ORDER BY nb_deces DESC
```

**Insight** : Politiques de santé publique ciblées

---

### Défis Techniques Rencontrés & Solutions

| Défi | Solution Implémentée | Compétence |
|------|----------------------|------------|
| **Volume** : CSV 25M lignes | Repartitionnement Spark (20 partitions) | Optimisation Big Data |
| **Mémoire** : OOM sur gros fichiers | Config Spark (8GB driver/executor) | Tuning performance |
| **RGPD** : Anonymisation | SHA-256 irréversible (PySpark) | Conformité réglementaire |
| **Hétérogénéité** : PostgreSQL + CSV | Architecture Medallion (Bronze) | Data Engineering |
| **Performance** : Requêtes lentes | Partitionnement + Parquet | Optimisation requêtes |
| **Géographie** : Manque région | Enrichissement via référentiel | Data enrichment |
| **Compatibilité** : PySpark imports | Debugging + docs Spark | Résolution problèmes |

---

### Compétences Développées

#### Hard Skills (Techniques)

**Big Data & Traitement Distribué**
- Apache Spark (PySpark API)
- Architecture Medallion (Bronze/Silver/Gold)
- Partitionnement et optimisation de données
- Formats Big Data (Parquet, compression)

**Data Engineering**
- Pipeline ETL/ETLT
- Modélisation dimensionnelle (Star Schema)
- Data quality & validation
- Data enrichment (jointures, agrégations)

**Bases de Données**
- SQL avancé (jointures, window functions, CTEs)
- PostgreSQL (extraction, JDBC)
- MinIO / S3 (object storage)
- Requêtes analytiques optimisées

**Conformité & Sécurité**
- RGPD (anonymisation, pseudonymisation)
- Hash cryptographique (SHA-256)
- Principes de minimisation des données

**DevOps & Infrastructure**
- Docker & Docker Compose
- Orchestration multi-services (7 conteneurs)
- Infrastructure as Code

**Langages & Outils**
- Python (PySpark, pandas, matplotlib)
- SQL (analytique)
- Jupyter Notebooks
- Git (versionning)

#### Soft Skills

- **Travail d'équipe** : Projet collaboratif à 3 (répartition des tâches)
- **Autonomie** : Résolution de problèmes techniques complexes
- **Documentation** : 12 fichiers Markdown (3000+ lignes)
- **Méthodologie** : Architecture ETLT, best practices Big Data
- **Veille technique** : Apache Spark 3.4, nouvelles pratiques Data Engineering

---

### Résultats Quantifiés

| Métrique | Valeur |
|----------|--------|
| **Volume de données traité** | 29M lignes |
| **Sources intégrées** | 17 (13 PostgreSQL + 4 CSV) |
| **Taux de compression** | 10x (CSV → Parquet) |
| **Temps d'exécution pipeline complet** | ~10 minutes |
| **Nombre de tables Gold** | 8 (5 dimensions + 3 faits) |
| **Lignes Gold (prêtes pour BI)** | 2.8M |
| **Gain performance (partitionnement)** | 10x sur requêtes temporelles |
| **Anonymisation** | 100% données PII (SHA-256) |
| **Services Docker** | 7 (Spark, PostgreSQL, MinIO, Jupyter, Airflow, Superset, pgAdmin) |
| **Documentation** | 12 fichiers Markdown, 3000+ lignes |

---

### Livrables du Projet

1. **Code source** : 4 notebooks Jupyter (Extract, Transform Silver, Transform Gold, Benchmarks)
2. **Infrastructure** : docker-compose.yml (7 services)
3. **Modèle de données** : Star Schema (5 dimensions, 3 faits)
4. **Documentation** : 12 fichiers Markdown (architecture, guides, troubleshooting)
5. **Données** : 2.8M lignes dans Gold layer (prêtes pour BI)
6. **Benchmarks** : Rapport de performance avec graphiques

---

### Prochaines Étapes (Livrable 3)

1. **Automatisation** : Conversion notebooks → scripts Python + DAGs Airflow
2. **Visualisation** : Dashboards Superset (KPIs métier)
3. **Présentation** : Démo live + storytelling data-driven

---

## 💡 CONSEILS POUR ENTRETIEN

### Questions probables

**"Parle-moi de ton projet Big Data"**
> *"J'ai conçu et implémenté un data lakehouse pour analyser 29 millions de lignes de données de santé publique. J'ai utilisé Apache Spark pour le traitement distribué, avec une architecture Medallion (Bronze/Silver/Gold) garantissant la conformité RGPD via anonymisation SHA-256. Le modèle final en étoile (Star Schema) permet des analyses décisionnelles rapides grâce au partitionnement temporel et au format Parquet, avec un gain de performance de 10x sur les requêtes. L'infrastructure complète est orchestrée avec Docker (7 services)."*

**"Quel a été ton plus grand défi ?"**
> *"Le traitement du fichier CSV de 25 millions de lignes de décès. Initialement, Spark saturait la mémoire. J'ai résolu le problème en repartitionnant les données (20 partitions), en augmentant la mémoire allouée (8GB), et en appliquant une compression Parquet qui a réduit la taille de 10x. Cela m'a appris l'importance du tuning Spark et de l'optimisation des formats de stockage."*

**"Comment as-tu géré la conformité RGPD ?"**
> *"J'ai implémenté une couche Silver dédiée à la conformité, appliquant un hash SHA-256 irréversible sur toutes les données personnelles identifiables (noms, prénoms, emails, téléphones, NSS). J'ai également appliqué le principe de minimisation en ne conservant que les données nécessaires aux analyses (âge et non date de naissance exacte, ville et non adresse complète). Cela garantit qu'il est impossible de ré-identifier les personnes tout en permettant les analyses statistiques."*

**"Pourquoi une architecture Medallion ?"**
> *"L'architecture Medallion (Bronze/Silver/Gold) permet de séparer les responsabilités : Bronze pour l'ingestion brute (historique immuable), Silver pour la conformité et le nettoyage (RGPD), et Gold pour les modèles métier (Star Schema optimisé pour BI). Cela facilite la maintenance, le debugging, et permet de retraiter les données depuis n'importe quelle couche en cas d'erreur."*

**"Comment as-tu optimisé les performances ?"**
> *"Trois optimisations principales : 1) Format Parquet columnaire compressé (10x plus compact que CSV), 2) Partitionnement temporel par année/mois (requêtes 10x plus rapides car Spark ne lit que les partitions nécessaires), 3) Adaptive Query Execution de Spark qui optimise automatiquement les jointures et agrégations. J'ai mesuré l'impact avec des benchmarks sur 6 requêtes SQL."*

---

## 🎯 VERSION ULTRA-COURTE (1 minute pitch)

> *"Dans le cadre de ma formation Big Data, j'ai développé un data lakehouse pour analyser 29 millions de lignes de données de santé publique. J'ai utilisé **Apache Spark** pour le traitement distribué et implémenté une **architecture Medallion** (Bronze/Silver/Gold) avec **anonymisation RGPD** (SHA-256). Le projet inclut un **modèle en étoile** (Star Schema) avec 5 dimensions et 3 tables de faits, optimisé avec **partitionnement temporel** et **format Parquet** pour des performances 10x supérieures. L'infrastructure complète est orchestrée avec **Docker** (7 services : Spark, PostgreSQL, MinIO, Jupyter, Airflow, Superset). Ce projet m'a permis de maîtriser le **Data Engineering**, la **conformité réglementaire**, et les **optimisations Big Data**."*

---

**Bonne chance pour ton CV et tes entretiens !** 🚀