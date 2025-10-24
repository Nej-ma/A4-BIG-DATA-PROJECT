# RÉCAPITULATIF FINAL - MODÈLE DIMENSIONNEL CHU
## Toutes les dimensions vérifiées avec sources réelles

**Date de validation**: 13/10/2025
**Statut**: ✅ TOUTES LES DIMENSIONS VALIDÉES

---

## 📊 VUE D'ENSEMBLE

| Dimension | Type | Source(s) | Nb Attributs | Nb Lignes Estimées | Statut |
|-----------|------|-----------|--------------|-------------------|--------|
| **DIM_TEMPS** | Commune (générée) | Générée automatiquement | 13 | ~4,383 | ✅ OK |
| **DIM_PATIENT** | Commune | PostgreSQL `Patient` | 12 | 100,000 | ✅ OK |
| **DIM_ETABLISSEMENT** | Commune | CSV `etablissement_sante.csv` (78 MB) | 21 | Milliers | ✅ OK |
| **DIM_DIAGNOSTIC** | Commune | PostgreSQL `Diagnostic` + CIM-10 OMS | 7 | 15,490 | ✅ OK |
| **DIM_PROFESSIONNEL** | Spécifique | PostgreSQL + CSV (73 MB) | 9 | 1,048,575+ | ✅ OK |
| **DIM_SPECIALITE** | Spécifique | PostgreSQL `Specialites` | 5 | Dizaines | ✅ OK |
| **DIM_MUTUELLE** | Spécifique | PostgreSQL `Mutuelle` + `Adher` | 6 | Centaines | ✅ OK |
| **DIM_TYPE_ENQUETE** | Spécifique | XLSX 2020 (ESATIS48H + ESATISCA) | 9 | 2 | ✅ OK |

**Total**: 8 dimensions • 82 attributs totaux

---

## 🔍 DÉTAIL PAR DIMENSION

### 1. DIM_TEMPS (Dimension temporelle)

**Type**: Dimension générée (pas de source externe)
**Période**: 2014-2025 (12 ans)
**Lignes estimées**: ~4,383

#### Attributs (13)
```sql
sk_temps INT PK,                    -- Clé surrogate auto-increment
date_complete DATE,                 -- Format YYYY-MM-DD
annee INT,                          -- 2014 à 2025
trimestre INT,                      -- 1 à 4
mois INT,                           -- 1 à 12
mois_libelle VARCHAR(20),           -- Janvier à Décembre
semaine INT,                        -- 1 à 53 (ISO)
jour INT,                           -- 1 à 31
jour_semaine VARCHAR(10),           -- Lundi à Dimanche
jour_semaine_num INT,               -- 1=Lundi, 7=Dimanche
est_weekend BOOLEAN,                -- 0/1
est_ferie BOOLEAN,                  -- 0/1 (jours fériés France)
trimestre_libelle VARCHAR(5)        -- Q1 à Q4
```

#### Hiérarchies
- Année → Trimestre → Mois → Semaine → Jour

#### Validation
✅ Structure standard d'entrepôt de données

---

### 2. DIM_PATIENT (Démographie pseudonymisée)

**Type**: Dimension commune
**Source**: PostgreSQL table `Patient`
**Lignes estimées**: 100,000

#### Colonnes source PostgreSQL (16)
`Id_patient`, `Nom`, `Prenom`, `Sexe`, `Adresse`, `Ville`, `Code_postal`, `Pays`, `EMail`, `Tel`, `Date`, `Age`, `Num_Secu`, `Groupe_sanguin`, `Poid`, `Taille`

#### ⚠️ Transformation T1 (Pseudonymisation RGPD)
**Champs supprimés**: `Nom`, `Prenom`, `Adresse`, `EMail`, `Tel`, `Num_Secu`, `Date`
**Raison**: Données personnelles identifiantes

#### Attributs finaux (12)
```sql
sk_patient INT PK,                  -- Clé surrogate
patient_pseudo_id VARCHAR(64),      -- SHA-256 de Id_patient + sel
sexe CHAR(1),                       -- M/F | SOURCE: Sexe
age INT,                            -- Âge | SOURCE: Age
tranche_age VARCHAR(10),            -- 0-18, 19-65, 65+ | CALCULÉ
groupe_sanguin VARCHAR(5),          -- A, B, AB, O, A+, A-, etc | SOURCE: Groupe_sanguin
ville VARCHAR(100),                 -- Ville | SOURCE: Ville
code_postal VARCHAR(5),             -- Code postal | SOURCE: Code_postal
pays VARCHAR(50),                   -- Pays | SOURCE: Pays
poid DECIMAL(5,2),                  -- Poids kg | SOURCE: Poid
taille DECIMAL(5,2),                -- Taille cm | SOURCE: Taille
bmi DECIMAL(4,2)                    -- IMC | CALCULÉ: poid/(taille/100)²
```

#### Transformations T2
- Calcul BMI = poid / (taille/100)²
- Calcul tranche_age depuis Age
- Validation codes postaux (format 5 chiffres)

#### Validation
✅ Colonnes PostgreSQL confirmées • 100,000 lignes

---

### 3. DIM_ETABLISSEMENT (Référentiel FINESS)

**Type**: Dimension commune
**Source**: CSV `etablissement_sante.csv` (78.4 MB)
**Encodage**: UTF-8 • Délimiteur: `;`
**Colonnes source**: 24

#### Attributs (21)
```sql
sk_etablissement INT PK,
finess VARCHAR(9),                      -- SOURCE: finess_site
identifiant_organisation VARCHAR(20),   -- SOURCE: identifiant_organisation
nom_etablissement VARCHAR(200),         -- SOURCE: raison_sociale_site
enseigne_commerciale VARCHAR(200),      -- SOURCE: enseigne_commerciale_site
commune VARCHAR(100),                   -- SOURCE: commune
code_postal VARCHAR(5),                 -- SOURCE: code_postal
code_commune VARCHAR(10),               -- SOURCE: code_commune
adresse VARCHAR(200),                   -- SOURCE: adresse
voie VARCHAR(100),                      -- SOURCE: voie
type_voie VARCHAR(50),                  -- SOURCE: type_voie (Rue, Avenue, etc.)
numero_voie VARCHAR(10),                -- SOURCE: numero_voie
cedex VARCHAR(50),                      -- SOURCE: cedex
pays VARCHAR(50),                       -- SOURCE: pays
telephone VARCHAR(20),                  -- SOURCE: telephone
telephone_2 VARCHAR(20),                -- SOURCE: telephone_2
telecopie VARCHAR(20),                  -- SOURCE: telecopie
email VARCHAR(100),                     -- SOURCE: email
siren VARCHAR(9),                       -- SOURCE: siren_site
siret VARCHAR(14),                      -- SOURCE: siret_site
finess_etablissement_juridique VARCHAR(9), -- SOURCE: finess_etablissement_juridique
region VARCHAR(100)                     -- CALCULÉ depuis code_postal
```

#### Échantillon première ligne
```
finess_site: F010000024
raison_sociale_site: CH DE FLEYRIAT
commune: Viriat
code_postal: 01440
telephone: 0474454647
email: dirg@ch-bourg01.fr
```

#### Transformations T2
- Extraction région depuis code postal
- Détermination type établissement (CH, CHU, Clinique, HAD, EHPAD) depuis raison_sociale
- Détermination statut (Public, Privé, PSPH) depuis raison_sociale

#### Validation
✅ CSV confirmé • 24 colonnes • Plusieurs milliers lignes

---

### 4. DIM_PROFESSIONNEL (Professionnels de santé)

**Type**: Dimension spécifique
**Sources**:
1. PostgreSQL `Professionnel_de_sante` (1,048,575 lignes)
2. CSV `professionnel_sante.csv` (72.8 MB)

#### Colonnes source PostgreSQL (8)
`Identifiant`, `Civilite`, `Categorie_professionnelle`, `Nom`, `Prenom`, `Profession`, `Type_identifiant`, `Code_specialite`

#### Colonnes source CSV (9)
`identifiant`, `civilite`, `categorie_professionnelle`, `nom`, `prenom`, `commune`, `profession`, `specialite`, `type_identifiant`

#### ⚠️ Transformation T1 (Pseudonymisation)
**Champs supprimés**: `Nom`, `Prenom`

#### Attributs finaux (9)
```sql
sk_professionnel INT PK,
prof_pseudo_id VARCHAR(64),           -- SHA-256 de Identifiant
civilite VARCHAR(10),                 -- M., Mme | SOURCE PG: Civilite
categorie_professionnelle VARCHAR(50), -- Civil, etc | SOURCE PG: Categorie_professionnelle
profession VARCHAR(100),              -- Profession | SOURCE PG/CSV: Profession
type_identifiant VARCHAR(10),         -- ADELI, RPPS | SOURCE PG/CSV: Type_identifiant
specialite VARCHAR(200),              -- Spécialité | SOURCE CSV: specialite
commune VARCHAR(100),                 -- Commune | SOURCE CSV: commune
code_specialite VARCHAR(10)           -- Code | SOURCE PG: Code_specialite → FK DIM_SPECIALITE
```

#### Échantillon CSV
```
identifiant: 10001717
civilite: Madame
categorie_professionnelle: Civil
profession: Psychotherapeute
type_identifiant: ADELI
```

#### Transformations T2
- Fusion PostgreSQL + CSV (jointure sur identifiant pseudo)
- Enrichissement avec spécialités depuis DIM_SPECIALITE

#### Validation
✅ Sources PostgreSQL (1M+ lignes) et CSV (73 MB) confirmées

---

### 5. DIM_DIAGNOSTIC (Classification CIM-10)

**Type**: Dimension commune
**Sources**:
1. PostgreSQL `Diagnostic` (15,490 codes)
2. Référentiel CIM-10 OMS (enrichissement externe)

#### Colonnes source PostgreSQL (2)
`Code_diag`, `Diagnostic`

#### Attributs (7)
```sql
sk_diagnostic INT PK,
code_diag VARCHAR(10),                -- Code CIM-10 | SOURCE PG: Code_diag | Ex: S02800, Q902, R192
libelle_diagnostic VARCHAR(500),      -- Description | SOURCE PG: Diagnostic
code_cim10_3car VARCHAR(3),           -- 3 caractères | EXTRAIT de Code_diag
chapitre_cim10 VARCHAR(200),          -- Chapitre CIM-10 | ENRICHISSEMENT OMS
categorie_cim10 VARCHAR(200),         -- Catégorie | ENRICHISSEMENT OMS
gravite VARCHAR(20)                   -- Bénin, Modéré, Sévère, Critique | CALCULÉ
```

#### Exemples codes
- `S02800`: Fracture de l'alvéole dentaire, fermées
- `Q902`: Trisomie 21, translocation
- `R192`: Péristaltisme apparent
- `M1125`: Autre chondrocalcinose, région pelvienne et cuisse

#### Enrichissement externe
**Source**: Référentiel CIM-10 OMS (Classification Internationale des Maladies)
**Méthode**: Jointure externe sur les 3 premiers caractères du code diagnostic
**Colonnes ajoutées**: `code_cim10_3car`, `chapitre_cim10`, `categorie_cim10`, `gravite`

#### Transformations T2
- Extraction code 3 caractères depuis Code_diag
- Jointure avec référentiel CIM-10 pour chapitres/catégories
- Classification gravité via règles métier

#### Validation
✅ Table PostgreSQL confirmée • 15,490 codes

---

### 6. DIM_SPECIALITE (Spécialités médicales)

**Type**: Dimension spécifique
**Source**: PostgreSQL `Specialites`

#### Colonnes source PostgreSQL (3)
`Code_specialite`, `Fonction`, `Specialite`

#### Attributs (5)
```sql
sk_specialite INT PK,
code_specialite VARCHAR(10),          -- Code officiel | SOURCE PG: Code_specialite
fonction VARCHAR(100),                -- Fonction | SOURCE PG: Fonction
specialite VARCHAR(200),              -- Libellé | SOURCE PG: Specialite
domaine_medical VARCHAR(50)           -- Chirurgie, Médecine, etc | CALCULÉ depuis Specialite
```

#### Transformations T2
- Classification domaine_medical depuis libellé spécialité
- Normalisation libellés

#### Validation
✅ Table PostgreSQL confirmée • Référentiel

---

### 7. DIM_MUTUELLE (Organismes complémentaires)

**Type**: Dimension spécifique
**Sources**:
- PostgreSQL `Mutuelle`
- PostgreSQL `Adher` (table liaison Patient-Mutuelle)

#### Colonnes source PostgreSQL (3)
`Id_Mut`, `Nom`, `Adresse`

#### Attributs (6)
```sql
sk_mutuelle INT PK,
id_mut VARCHAR(20),                   -- Identifiant | SOURCE PG: Id_Mut
nom VARCHAR(200),                     -- Nom | SOURCE PG: Nom
adresse VARCHAR(200),                 -- Adresse | SOURCE PG: Adresse
type_mutuelle VARCHAR(50),            -- Nationale, Régionale, Entreprise | CALCULÉ depuis Nom
region_mutuelle VARCHAR(100)          -- Région siège | CALCULÉ depuis Adresse
```

#### Transformations T2
- Classification type_mutuelle depuis Nom
- Extraction région depuis Adresse

#### Validation
✅ Table PostgreSQL confirmée • Référentiel

---

### 8. DIM_TYPE_ENQUETE (Types enquêtes satisfaction)

**Type**: Dimension spécifique
**Source**: XLSX 2020 (ESATIS48H + ESATISCA)
**Année données**: 2020 uniquement

#### Attributs (9)
```sql
sk_type_enquete INT PK,
type_enquete VARCHAR(20),             -- 'ESATIS48H' ou 'ESATISCA'
annee_enquete INT,                    -- 2020
libelle_court VARCHAR(100),           -- 'E-Satis 48h MCO' ou 'E-Satis CA'
libelle_complet VARCHAR(500),         -- Description complète
methodologie VARCHAR(200),            -- Questionnaire post-sortie 48h/sortie immédiate
periodicite VARCHAR(20),              -- 'Annuelle'
secteur VARCHAR(20),                  -- 'MCO' ou 'MCO CA'
description TEXT                      -- Description détaillée enquête
```

#### Valeurs possibles (2 lignes)

**Type 1: ESATIS48H**
- Libellé: E-Satis 48h MCO
- Description: Enquête satisfaction patient hospitalisé en MCO, questionnaire 48h après sortie
- Secteur: MCO
- Établissements: 1,150

**Type 2: ESATISCA**
- Libellé: E-Satis Chirurgie Ambulatoire
- Description: Enquête satisfaction patient chirurgie ambulatoire, questionnaire à la sortie
- Secteur: MCO CA
- Établissements: 931

#### Transformations T2
- Création de 2 lignes fixes
- Enrichissement avec descriptions méthodologiques

#### Validation
✅ Fichiers XLSX 2020 confirmés

---

## 📈 TABLES DE FAITS (Validation sources)

### FAIT_CONSULTATION
**Source**: PostgreSQL `Consultation` (1,027,157 lignes)
**Dimensions**: DIM_TEMPS, DIM_PATIENT, DIM_PROFESSIONNEL, DIM_DIAGNOSTIC, DIM_ETABLISSEMENT, DIM_MUTUELLE

### FAIT_HOSPITALISATION
**Source**: CSV `Hospitalisations.csv` (2,481 lignes, 2016-2020)
**Colonnes source**: `Num_Hospitalisation`, `Id_patient`, `identifiant_organisation (FINESS)`, `Code_diagnostic`, `Suite_diagnostic_consultation`, `Date_Entree`, `Jour_Hospitalisation`
**Dimensions**: DIM_TEMPS (entrée+sortie), DIM_PATIENT, DIM_ETABLISSEMENT, DIM_DIAGNOSTIC

### FAIT_DECES
**Source**: CSV `deces.csv` (1.9 GB)
**Colonnes source**: `nom`, `prenom`, `sexe`, `date_naissance`, `code_lieu_naissance`, `lieu_naissance`, `pays_naissance`, `date_deces`, `code_lieu_deces`, `numero_acte_deces`
**⚠️ RGPD**: Contient données nominatives → pseudonymisation OBLIGATOIRE T1
**Dimensions**: DIM_TEMPS, DIM_PATIENT

### FAIT_SATISFACTION_PATIENT
**Source**: XLSX 2020 (ESATIS48H + ESATISCA) = 2,081 lignes
**Colonnes source XLSX**: `finess`, `rs_finess`, `region`, `nb_rep_score_all_rea_ajust`, `score_all_rea_ajust`, `score_accueil_rea_ajust`, `score_PECinf_rea_ajust`, `score_PECmed_rea_ajust`, `score_chambre_rea_ajust`, `score_repas_rea_ajust`, `score_sortie_rea_ajust`, `classement`, `evolution`
**Dimensions**: DIM_TEMPS (2020), DIM_ETABLISSEMENT, DIM_TYPE_ENQUETE

---

## ✅ VALIDATION FINALE

### Statistiques globales
- **8 dimensions** validées avec sources réelles
- **82 attributs** totaux
- **4 tables de faits** avec sources confirmées
- **Sources**: 7 PostgreSQL tables + 4 CSV + 2 XLSX

### Conformité RGPD
✅ Pseudonymisation T1 : DIM_PATIENT, DIM_PROFESSIONNEL, FAIT_DECES
✅ Suppression données identifiantes : Nom, Prénom, Email, Tel, Num_Secu, Adresse
✅ Conservation données analytiques uniquement

### Prochaines étapes (Livrable 2)
1. Scripts Spark T1 (pseudonymisation)
2. Scripts Spark T2 (enrichissements CIM-10, FINESS, géo)
3. Tables Hive ORC avec partitionnement
4. Tests performance et optimisation

---

**Document généré le**: 13/10/2025
**Statut final**: ✅ TOUTES LES DIMENSIONS VALIDÉES AVEC SOURCES RÉELLES
