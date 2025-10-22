-- ========================================
-- SCRIPT DE CRÉATION DES TABLES SPARK SQL
-- Pour Superset - CHU Data Lakehouse
-- ========================================

-- 1. DIMENSION TEMPS
DROP TABLE IF EXISTS dim_temps;
CREATE EXTERNAL TABLE dim_temps (
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
DROP TABLE IF EXISTS dim_patient;
CREATE EXTERNAL TABLE dim_patient (
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
DROP TABLE IF EXISTS dim_diagnostic;
CREATE EXTERNAL TABLE dim_diagnostic (
    code_diag STRING,
    libelle STRING,
    categorie STRING
)
STORED AS PARQUET
LOCATION '/home/jovyan/data/gold/dim_diagnostic';

-- 4. DIMENSION PROFESSIONNEL
DROP TABLE IF EXISTS dim_professionnel;
CREATE EXTERNAL TABLE dim_professionnel (
    id_prof STRING,
    nom_specialite STRING,
    ville STRING,
    code_postal STRING
)
STORED AS PARQUET
LOCATION '/home/jovyan/data/gold/dim_professionnel';

-- 5. DIMENSION ETABLISSEMENT
DROP TABLE IF EXISTS dim_etablissement;
CREATE EXTERNAL TABLE dim_etablissement (
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
DROP TABLE IF EXISTS fait_consultation;
CREATE EXTERNAL TABLE fait_consultation (
    id_consultation STRING,
    id_temps STRING,
    id_patient STRING,
    code_diag STRING,
    id_prof STRING,
    cout DECIMAL(10,2),
    duree_minutes INT,
    urgence BOOLEAN
)
PARTITIONED BY (annee INT, mois INT)
STORED AS PARQUET
LOCATION '/home/jovyan/data/gold/fait_consultation';

-- IMPORTANT : Réparer les partitions pour charger tous les fichiers
MSCK REPAIR TABLE fait_consultation;

-- ========================================
-- VÉRIFICATION
-- ========================================

-- Afficher toutes les tables
SHOW TABLES;

-- Compter les lignes
SELECT 'dim_temps' as table_name, COUNT(*) as nb_lignes FROM dim_temps
UNION ALL
SELECT 'dim_patient', COUNT(*) FROM dim_patient
UNION ALL
SELECT 'dim_diagnostic', COUNT(*) FROM dim_diagnostic
UNION ALL
SELECT 'dim_professionnel', COUNT(*) FROM dim_professionnel
UNION ALL
SELECT 'dim_etablissement', COUNT(*) FROM dim_etablissement
UNION ALL
SELECT 'fait_consultation', COUNT(*) FROM fait_consultation;
