-- Script pour charger les CSV dans PostgreSQL
-- Auteurs: Nejma MOUALHI | Brieuc OLIVIERI | Nicolas TAING

-- ============================================================
-- 1. TABLE DECES (filtré 2019)
-- ============================================================

DROP TABLE IF EXISTS "Deces_2019";

CREATE TABLE "Deces_2019" (
    nom VARCHAR(100),
    prenom VARCHAR(100),
    sexe VARCHAR(1),
    date_naissance DATE,
    code_lieu_naissance VARCHAR(10),
    lieu_naissance VARCHAR(100),
    pays_naissance VARCHAR(100),
    date_deces DATE,
    code_lieu_deces VARCHAR(10),
    numero_acte_deces VARCHAR(20)
);

-- Charger seulement les décès de 2019
-- On utilise un filtre WHERE pendant l'import
COPY "Deces_2019" FROM '/docker-entrypoint-initdb.d/DATA 2024/DECES EN FRANCE/deces.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

-- Filtrer seulement 2019 (supprimer les autres)
DELETE FROM "Deces_2019" WHERE EXTRACT(YEAR FROM date_deces) != 2019;

-- ============================================================
-- 2. TABLE ETABLISSEMENTS DE SANTE
-- ============================================================

DROP TABLE IF EXISTS "Etablissement_sante";

CREATE TABLE "Etablissement_sante" (
    adresse TEXT,
    cedex VARCHAR(20),
    code_commune VARCHAR(10),
    code_postal VARCHAR(10),
    commune VARCHAR(100),
    complement_destinataire TEXT,
    complement_point_geographique TEXT,
    email VARCHAR(200),
    enseigne_commerciale_site TEXT,
    finess_etablissement_juridique VARCHAR(20),
    finess_site VARCHAR(20),
    identifiant_organisation VARCHAR(50),
    indice_repetition_voie VARCHAR(10),
    mention_distribution TEXT,
    numero_voie VARCHAR(10),
    pays VARCHAR(100),
    raison_sociale_site TEXT,
    siren_site VARCHAR(20),
    siret_site VARCHAR(20),
    telecopie VARCHAR(20),
    telephone VARCHAR(20),
    telephone_2 VARCHAR(20),
    type_voie VARCHAR(50),
    voie TEXT
);

COPY "Etablissement_sante" FROM '/docker-entrypoint-initdb.d/DATA 2024/Etablissement de SANTE/etablissement_sante.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ';', ENCODING 'UTF8');

-- ============================================================
-- 3. TABLE SATISFACTION 2019
-- ============================================================

DROP TABLE IF EXISTS "Satisfaction_2019";

CREATE TABLE "Satisfaction_2019" (
    finess VARCHAR(20),
    rs_finess TEXT,
    finess_geo VARCHAR(20),
    rs_finess_geo TEXT,
    region VARCHAR(100),
    participation VARCHAR(50),
    depot VARCHAR(10),
    nb_rep_score_all_rea_ajust INTEGER,
    score_all_rea_ajust DECIMAL(5,2),
    classement VARCHAR(10),
    evolution VARCHAR(50),
    nb_rep_score_accueil_rea_ajust INTEGER,
    score_accueil_rea_ajust DECIMAL(5,2),
    nb_rep_score_pecinf_rea_ajust INTEGER,
    score_pecinf_rea_ajust DECIMAL(5,2),
    nb_rep_score_pecmed_rea_ajust INTEGER,
    score_pecmed_rea_ajust DECIMAL(5,2),
    nb_rep_score_chambre_rea_ajust INTEGER,
    score_chambre_rea_ajust DECIMAL(5,2),
    nb_rep_score_repas_rea_ajust INTEGER,
    score_repas_rea_ajust DECIMAL(5,2),
    nb_rep_score_sortie_rea_ajust INTEGER,
    score_sortie_rea_ajust DECIMAL(5,2),
    taux_reco_brut DECIMAL(5,2),
    nb_reco_brut INTEGER
);

COPY "Satisfaction_2019" FROM '/docker-entrypoint-initdb.d/DATA 2024/Satisfaction/2019/resultats-esatis48h-mco-open-data-2019.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ';', ENCODING 'UTF8');

-- ============================================================
-- VERIFICATION
-- ============================================================

SELECT 'Deces_2019' as table_name, COUNT(*) as nb_lignes FROM "Deces_2019"
UNION ALL
SELECT 'Etablissement_sante', COUNT(*) FROM "Etablissement_sante"
UNION ALL
SELECT 'Satisfaction_2019', COUNT(*) FROM "Satisfaction_2019";
