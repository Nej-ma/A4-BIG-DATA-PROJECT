-- Script simplifié pour charger les CSV essentiels dans PostgreSQL
-- On utilise des types TEXT pour éviter les erreurs de format

-- ============================================================
-- 1. ETABLISSEMENTS (le plus simple)
-- ============================================================

DROP TABLE IF EXISTS "Etablissement_sante";

CREATE TABLE "Etablissement_sante" (
    adresse TEXT,
    cedex TEXT,
    code_commune TEXT,
    code_postal TEXT,
    commune TEXT,
    complement_destinataire TEXT,
    complement_point_geographique TEXT,
    email TEXT,
    enseigne_commerciale_site TEXT,
    finess_etablissement_juridique TEXT,
    finess_site TEXT,
    identifiant_organisation TEXT,
    indice_repetition_voie TEXT,
    mention_distribution TEXT,
    numero_voie TEXT,
    pays TEXT,
    raison_sociale_site TEXT,
    siren_site TEXT,
    siret_site TEXT,
    telecopie TEXT,
    telephone TEXT,
    telephone_2 TEXT,
    type_voie TEXT,
    voie TEXT
);

COPY "Etablissement_sante" FROM '/docker-entrypoint-initdb.d/DATA 2024/Etablissement de SANTE/etablissement_sante.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ';', ENCODING 'LATIN1');

-- ============================================================
-- 2. SATISFACTION 2019 (tout en TEXT pour éviter les erreurs)
-- ============================================================

DROP TABLE IF EXISTS "Satisfaction_2019";

CREATE TABLE "Satisfaction_2019" (
    finess TEXT,
    rs_finess TEXT,
    finess_geo TEXT,
    rs_finess_geo TEXT,
    region TEXT,
    participation TEXT,
    depot TEXT,
    nb_rep_score_all_rea_ajust TEXT,
    score_all_rea_ajust TEXT,
    classement TEXT,
    evolution TEXT,
    nb_rep_score_accueil_rea_ajust TEXT,
    score_accueil_rea_ajust TEXT,
    nb_rep_score_pecinf_rea_ajust TEXT,
    score_pecinf_rea_ajust TEXT,
    nb_rep_score_pecmed_rea_ajust TEXT,
    score_pecmed_rea_ajust TEXT,
    nb_rep_score_chambre_rea_ajust TEXT,
    score_chambre_rea_ajust TEXT,
    nb_rep_score_repas_rea_ajust TEXT,
    score_repas_rea_ajust TEXT,
    nb_rep_score_sortie_rea_ajust TEXT,
    score_sortie_rea_ajust TEXT,
    taux_reco_brut TEXT,
    nb_reco_brut TEXT
);

COPY "Satisfaction_2019" FROM '/docker-entrypoint-initdb.d/DATA 2024/Satisfaction/2019/resultats-esatis48h-mco-open-data-2019.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ';', ENCODING 'LATIN1');

-- ============================================================
-- VERIFICATION
-- ============================================================

SELECT 'Etablissement_sante' as table_name, COUNT(*) as nb_lignes FROM "Etablissement_sante"
UNION ALL
SELECT 'Satisfaction_2019', COUNT(*) FROM "Satisfaction_2019";

\echo '✅ Tables CSV chargées dans PostgreSQL !'
