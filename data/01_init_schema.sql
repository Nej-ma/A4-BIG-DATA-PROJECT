-- ============================================================
-- SCRIPT D'INITIALISATION - BASE DE DONNÉES CHU
-- ============================================================
-- Cloud Healthcare Unit - Projet Big Data
-- CESI FISA A4 - Livrable 2
-- ============================================================

-- Suppression des tables existantes (si besoin)
DROP TABLE IF EXISTS "Hospitalisation" CASCADE;
DROP TABLE IF EXISTS "Consultation" CASCADE;
DROP TABLE IF EXISTS "Prescription" CASCADE;
DROP TABLE IF EXISTS "Acte" CASCADE;
DROP TABLE IF EXISTS "Patient" CASCADE;
DROP TABLE IF EXISTS "Medecin" CASCADE;
DROP TABLE IF EXISTS "Medicament" CASCADE;
DROP TABLE IF EXISTS "Service" CASCADE;

-- ============================================================
-- TABLE: Service (Dimension)
-- ============================================================
CREATE TABLE "Service" (
    id_service SERIAL PRIMARY KEY,
    nom_service VARCHAR(100) NOT NULL,
    type_service VARCHAR(50) NOT NULL, -- Urgences, Cardiologie, Pédiatrie, etc.
    capacite_lits INTEGER,
    etage INTEGER,
    batiment VARCHAR(50)
);

-- ============================================================
-- TABLE: Medecin (Dimension)
-- ============================================================
CREATE TABLE "Medecin" (
    id_medecin SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    specialite VARCHAR(100) NOT NULL,
    telephone VARCHAR(20),
    email VARCHAR(100),
    id_service INTEGER REFERENCES "Service"(id_service),
    date_embauche DATE
);

-- ============================================================
-- TABLE: Patient (Dimension - AVEC DONNÉES PII POUR RGPD)
-- ============================================================
CREATE TABLE "Patient" (
    id_patient SERIAL PRIMARY KEY,
    -- Données PII à pseudonymiser (T1)
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    date_naissance DATE NOT NULL,
    sexe CHAR(1) CHECK (sexe IN ('M', 'F', 'A')),
    numero_securite_sociale VARCHAR(15) UNIQUE,
    adresse TEXT,
    code_postal VARCHAR(10),
    ville VARCHAR(100),
    telephone VARCHAR(20),
    email VARCHAR(100),
    -- Données médicales
    groupe_sanguin VARCHAR(5),
    date_inscription DATE DEFAULT CURRENT_DATE,
    -- Métadonnées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: Medicament (Dimension)
-- ============================================================
CREATE TABLE "Medicament" (
    id_medicament SERIAL PRIMARY KEY,
    nom_commercial VARCHAR(200) NOT NULL,
    denomination_commune VARCHAR(200),
    dosage VARCHAR(50),
    forme VARCHAR(50), -- Comprimé, Sirop, Injectable, etc.
    laboratoire VARCHAR(100),
    prix_unitaire DECIMAL(10,2),
    remboursable BOOLEAN DEFAULT TRUE
);

-- ============================================================
-- TABLE: Consultation (Fait)
-- ============================================================
CREATE TABLE "Consultation" (
    id_consultation SERIAL PRIMARY KEY,
    id_patient INTEGER NOT NULL REFERENCES "Patient"(id_patient),
    id_medecin INTEGER NOT NULL REFERENCES "Medecin"(id_medecin),
    date_consultation TIMESTAMP NOT NULL,
    motif TEXT,
    diagnostic TEXT,
    observations TEXT,
    duree_minutes INTEGER,
    tarif DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: Hospitalisation (Fait)
-- ============================================================
CREATE TABLE "Hospitalisation" (
    id_hospitalisation SERIAL PRIMARY KEY,
    id_patient INTEGER NOT NULL REFERENCES "Patient"(id_patient),
    id_medecin INTEGER NOT NULL REFERENCES "Medecin"(id_medecin),
    id_service INTEGER NOT NULL REFERENCES "Service"(id_service),
    date_entree TIMESTAMP NOT NULL,
    date_sortie TIMESTAMP,
    motif_entree TEXT,
    diagnostic_principal TEXT,
    diagnostic_secondaire TEXT,
    numero_chambre VARCHAR(20),
    type_admission VARCHAR(50), -- Urgence, Programmée, Transfert
    cout_total DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: Prescription (Fait)
-- ============================================================
CREATE TABLE "Prescription" (
    id_prescription SERIAL PRIMARY KEY,
    id_consultation INTEGER REFERENCES "Consultation"(id_consultation),
    id_hospitalisation INTEGER REFERENCES "Hospitalisation"(id_hospitalisation),
    id_medicament INTEGER NOT NULL REFERENCES "Medicament"(id_medicament),
    id_patient INTEGER NOT NULL REFERENCES "Patient"(id_patient),
    id_medecin INTEGER NOT NULL REFERENCES "Medecin"(id_medecin),
    date_prescription TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    quantite INTEGER NOT NULL,
    posologie TEXT,
    duree_traitement_jours INTEGER,
    renouvellable BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (id_consultation IS NOT NULL OR id_hospitalisation IS NOT NULL)
);

-- ============================================================
-- TABLE: Acte (Fait)
-- ============================================================
CREATE TABLE "Acte" (
    id_acte SERIAL PRIMARY KEY,
    id_consultation INTEGER REFERENCES "Consultation"(id_consultation),
    id_hospitalisation INTEGER REFERENCES "Hospitalisation"(id_hospitalisation),
    id_medecin INTEGER NOT NULL REFERENCES "Medecin"(id_medecin),
    code_acte VARCHAR(20) NOT NULL, -- Code CCAM
    libelle_acte VARCHAR(200) NOT NULL,
    date_acte TIMESTAMP NOT NULL,
    tarif DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (id_consultation IS NOT NULL OR id_hospitalisation IS NOT NULL)
);

-- ============================================================
-- INDEX POUR PERFORMANCES
-- ============================================================
CREATE INDEX idx_patient_date_naissance ON "Patient"(date_naissance);
CREATE INDEX idx_patient_code_postal ON "Patient"(code_postal);
CREATE INDEX idx_consultation_date ON "Consultation"(date_consultation);
CREATE INDEX idx_consultation_patient ON "Consultation"(id_patient);
CREATE INDEX idx_consultation_medecin ON "Consultation"(id_medecin);
CREATE INDEX idx_hospitalisation_dates ON "Hospitalisation"(date_entree, date_sortie);
CREATE INDEX idx_hospitalisation_patient ON "Hospitalisation"(id_patient);
CREATE INDEX idx_prescription_date ON "Prescription"(date_prescription);
CREATE INDEX idx_acte_date ON "Acte"(date_acte);

-- ============================================================
-- COMMENTAIRES
-- ============================================================
COMMENT ON TABLE "Patient" IS 'Table patients avec données PII à pseudonymiser lors de la transformation T1';
COMMENT ON TABLE "Consultation" IS 'Table de faits - Consultations médicales';
COMMENT ON TABLE "Hospitalisation" IS 'Table de faits - Hospitalisations';
COMMENT ON TABLE "Prescription" IS 'Table de faits - Prescriptions médicamenteuses';
COMMENT ON TABLE "Acte" IS 'Table de faits - Actes médicaux';

-- ============================================================
-- FIN DU SCRIPT
-- ============================================================
