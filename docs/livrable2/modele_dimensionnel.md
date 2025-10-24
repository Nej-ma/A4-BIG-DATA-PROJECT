# Modèle Dimensionnel - Gold Layer (Star Schema)

**Projet:** CHU Data Lakehouse
**Auteurs:** Nejma MOUALHI | Brieuc OLIVIERI | Nicolas TAING
**Date:** 2025

---

## 📊 Architecture du Modèle

Le modèle dimensionnel suit une architecture **Star Schema** optimisée pour répondre aux besoins analytiques du groupe CHU.

---

## 🎯 Besoins Analytiques à Satisfaire

1. Taux de consultation des patients dans un établissement X sur une période Y
2. Taux de consultation par rapport à un diagnostic X sur une période Y
3. Taux global d'hospitalisation sur une période Y
4. Taux d'hospitalisation par diagnostic sur une période donnée
5. Taux d'hospitalisation par sexe, par âge
6. Taux de consultation par professionnel
7. Nombre de décès par localisation (région) et année 2019
8. Taux global de satisfaction par région sur l'année 2020

---

## 📐 Schéma en Étoile (Star Schema)

```
                    ┌─────────────────┐
                    │  dim_temps      │
                    ├─────────────────┤
                    │ id_temps (PK)   │
                    │ date            │
                    │ annee           │
                    │ mois            │
                    │ trimestre       │
                    │ jour_semaine    │
                    └─────────────────┘
                            │
                            │
    ┌──────────────┐       │       ┌─────────────────┐
    │ dim_patient  │       │       │ dim_diagnostic  │
    ├──────────────┤       │       ├─────────────────┤
    │ id_patient   │       │       │ code_diag (PK)  │
    │ sexe         │◄──────┼──────►│ libelle         │
    │ age          │       │       │ categorie       │
    │ ville        │       │       └─────────────────┘
    │ code_postal  │       │
    │ groupe_sang  │       │       ┌──────────────────┐
    └──────────────┘       │       │ dim_professionnel│
                           │       ├──────────────────┤
                           │       │ id_prof (PK)     │
    ┌──────────────┐       │       │ nom              │
    │ dim_mutuelle │       │       │ prenom           │
    ├──────────────┤       │       │ specialite       │
    │ id_mut (PK)  │       │       └──────────────────┘
    │ nom          │       │
    │ type         │       │       ┌──────────────────┐
    └──────────────┘       │       │ dim_etablissement│
                           │       ├──────────────────┤
                           │       │ finess (PK)      │
                           │       │ nom              │
                           ▼       │ region           │
                   ┌─────────────────────────┐
                   │  FAIT_CONSULTATION      │
                   ├─────────────────────────┤
                   │ id_consultation (PK)    │
                   │ id_patient (FK)         │
                   │ id_temps (FK)           │
                   │ id_prof (FK)            │
                   │ code_diag (FK)          │
                   │ id_mut (FK)             │
                   │ duree_minutes           │
                   │ heure_debut             │
                   │ heure_fin               │
                   └─────────────────────────┘


                   ┌─────────────────────────┐
                   │  FAIT_HOSPITALISATION   │
                   ├─────────────────────────┤
                   │ id_hospi (PK)           │
                   │ id_patient (FK)         │
                   │ id_temps (FK)           │
                   │ code_diag (FK)          │
                   │ finess (FK)             │
                   │ duree_sejour            │
                   │ mode_entree             │
                   │ mode_sortie             │
                   └─────────────────────────┘


                   ┌─────────────────────────┐
                   │  FAIT_DECES             │
                   ├─────────────────────────┤
                   │ id_deces (PK)           │
                   │ id_temps (FK)           │
                   │ sexe                    │
                   │ age_deces               │
                   │ code_lieu_deces         │
                   │ lieu_deces              │
                   │ pays_naissance          │
                   └─────────────────────────┘


                   ┌─────────────────────────┐
                   │  FAIT_SATISFACTION      │
                   ├─────────────────────────┤
                   │ id_satisfaction (PK)    │
                   │ finess (FK)             │
                   │ id_temps (FK)           │
                   │ score_global            │
                   │ score_accueil           │
                   │ score_pec_infirmiere    │
                   │ score_pec_medicale      │
                   │ score_chambre           │
                   │ score_repas             │
                   │ score_sortie            │
                   │ taux_recommandation     │
                   │ nb_repondants           │
                   └─────────────────────────┘
```

---

## 📋 Description des Tables

### Tables de Dimensions

#### 1. **dim_temps**
- **Clé primaire:** id_temps (INT)
- **Description:** Dimension temporelle pour toutes les analyses
- **Granularité:** Jour
- **Attributs:**
  - date (DATE)
  - annee (INT)
  - mois (INT)
  - trimestre (INT)
  - jour_semaine (STRING)
  - est_weekend (BOOLEAN)

#### 2. **dim_patient**
- **Clé primaire:** id_patient (INT)
- **Description:** Informations démographiques des patients
- **Attributs:**
  - nom, prenom
  - sexe (M/F)
  - age (INT)
  - ville, code_postal, pays
  - groupe_sanguin
  - date_naissance

#### 3. **dim_diagnostic**
- **Clé primaire:** code_diag (STRING)
- **Description:** Classification des diagnostics médicaux
- **Attributs:**
  - libelle (description)
  - categorie (classification)

#### 4. **dim_professionnel**
- **Clé primaire:** id_prof (STRING)
- **Description:** Professionnels de santé
- **Attributs:**
  - nom, prenom
  - specialite
  - type_professionnel

#### 5. **dim_mutuelle**
- **Clé primaire:** id_mut (INT)
- **Description:** Mutuelles de santé
- **Attributs:**
  - nom
  - type

#### 6. **dim_etablissement**
- **Clé primaire:** finess (STRING)
- **Description:** Établissements de santé
- **Attributs:**
  - nom
  - region
  - ville
  - code_postal
  - type_etablissement

---

### Tables de Faits

#### 1. **FAIT_CONSULTATION**
- **Granularité:** Une ligne par consultation
- **Mesures:**
  - duree_minutes (calculé depuis heure_debut et heure_fin)
- **Clés étrangères:**
  - id_patient → dim_patient
  - id_temps → dim_temps
  - id_prof → dim_professionnel
  - code_diag → dim_diagnostic
  - id_mut → dim_mutuelle

#### 2. **FAIT_HOSPITALISATION**
- **Granularité:** Une ligne par hospitalisation
- **Mesures:**
  - duree_sejour (en jours)
- **Clés étrangères:**
  - id_patient → dim_patient
  - id_temps → dim_temps
  - code_diag → dim_diagnostic
  - finess → dim_etablissement

#### 3. **FAIT_DECES**
- **Granularité:** Une ligne par décès
- **Mesures:**
  - age_deces (calculé)
- **Clés étrangères:**
  - id_temps → dim_temps

#### 4. **FAIT_SATISFACTION**
- **Granularité:** Une ligne par établissement et période
- **Mesures:**
  - score_global, score_accueil, etc.
  - taux_recommandation
  - nb_repondants
- **Clés étrangères:**
  - finess → dim_etablissement
  - id_temps → dim_temps

---

## 🎯 Optimisations Prévues

### Partitionnement
- **dim_temps:** Par annee
- **FAIT_CONSULTATION:** Par annee, mois
- **FAIT_HOSPITALISATION:** Par annee, mois
- **FAIT_DECES:** Par annee
- **FAIT_SATISFACTION:** Par annee

### Bucketing
- **FAIT_CONSULTATION:** 32 buckets par id_patient
- **FAIT_HOSPITALISATION:** 16 buckets par id_patient
- **FAIT_DECES:** 16 buckets par code_lieu_deces
- **FAIT_SATISFACTION:** 8 buckets par finess

### Indexes et Optimisations Delta Lake
- Z-ORDER sur les colonnes fréquemment filtrées
- OPTIMIZE pour compaction des petits fichiers
- VACUUM pour nettoyage des anciennes versions

---

## 📈 Requêtes Analytiques Supportées

### 1. Taux de consultation par établissement
```sql
SELECT
    e.nom AS etablissement,
    t.annee, t.mois,
    COUNT(c.id_consultation) AS nb_consultations
FROM FAIT_CONSULTATION c
JOIN dim_professionnel p ON c.id_prof = p.id_prof
JOIN dim_etablissement e ON p.finess = e.finess  -- Via jointure
JOIN dim_temps t ON c.id_temps = t.id_temps
WHERE e.finess = 'XXX' AND t.annee = 2019
GROUP BY e.nom, t.annee, t.mois
```

### 2. Hospitalisation par diagnostic
```sql
SELECT
    d.categorie,
    COUNT(h.id_hospi) AS nb_hospitalisations,
    AVG(h.duree_sejour) AS duree_moyenne
FROM FAIT_HOSPITALISATION h
JOIN dim_diagnostic d ON h.code_diag = d.code_diag
JOIN dim_temps t ON h.id_temps = t.id_temps
WHERE t.annee = 2019
GROUP BY d.categorie
```

### 3. Décès par région
```sql
SELECT
    lieu_deces,
    COUNT(*) AS nb_deces
FROM FAIT_DECES
JOIN dim_temps t ON FAIT_DECES.id_temps = t.id_temps
WHERE t.annee = 2019
GROUP BY lieu_deces
ORDER BY nb_deces DESC
```

---

## 🔄 Pipeline ETL

```
BRONZE (Raw)
    ↓
SILVER (Cleaned)
    ↓
GOLD (Star Schema)
    ↓
Analytics/BI
```
