# FAIT_SATISFACTION - MODÈLE RÉEL BASÉ SUR LES DONNÉES SOURCES

## ⚠️ PROBLÈME IDENTIFIÉ

Les fichiers CSV de satisfaction (2014-2020) ont des **structures TOTALEMENT DIFFÉRENTES** selon les années et types d'enquêtes :

### Format A : ESATIS48H (2019) - Enquête satisfaction patient
**Fichier** : `resultats-esatis48h-mco-open-data-2019.csv`

**Structure** : Scores patients par dimension
- ✅ `score_accueil_rea_ajust` : Score accueil ajusté
- ✅ `score_PECinf_rea_ajust` : Score prise en charge infirmière
- ✅ `score_PECmed_rea_ajust` : Score prise en charge médicale
- ✅ `score_chambre_rea_ajust` : Score chambre
- ✅ `score_repas_rea_ajust` : Score repas
- ✅ `score_sortie_rea_ajust` : Score sortie
- ✅ `score_all_rea_ajust` : Score global
- ✅ `nb_rep_score_all_rea_ajust` : Nombre de réponses
- ✅ `classement` : A, B, C, NV, DI
- ✅ `evolution` : Amélioration, Stable, Dégradation

**Granularité** : 1 ligne = 1 établissement × 1 année

---

### Format B : IQSS (2019) - Indicateurs qualité sécurité soins
**Fichier** : `resultats-iqss-open-data-2019.csv`

**Structure** : Indicateurs techniques par processus
- `classe_ias_icsha_v3_mhs` : Classe consommation SHA (A, B, C)
- `res_ias_icsha_v3_mhs` : Résultat indicateur (0-100)
- `classe_DPA_qls_v2_MCO` : Classe qualité lettre liaison
- `res_dpa_qls_v2_mco` : Résultat DPA
- `classe_DPA_pcd_MCO` : Classe prise en charge douleur
- ... (46 colonnes d'indicateurs !)

**⚠️ PAS de scores patients !** Ce sont des indicateurs de **processus hospitaliers**

**Granularité** : 1 ligne = 1 établissement × multiples indicateurs techniques

---

### Format C : DPA SSR (2017-2018) - Dossier patient audit
**Fichier** : `dpa-ssr-recueil2018-donnee2017-donnees.csv`

**Structure** : Indicateurs audit dossier
- `Resultat_doc` : Résultat audit documentation
- `doc_c_etbt` : Score établissement documentation (0-100)
- `doc_c_pos_seuil_etbt` : Position vs seuil (A, B, C)
- `Resultat_dtn` : Résultat dossier traçabilité nutrition
- `dtn2_c2_etbt` : Score traçabilité nutrition

**⚠️ Indicateurs techniques d'audit, PAS de satisfaction patients !**

**Granularité** : 1 ligne = 1 établissement × indicateurs audit

---

### Format D : RCP MCO (2014) - Réunion concertation pluridisciplinaire
**Fichier** : `RCP_MCO_recueil2014_donnee2013_table_es.csv`

**Structure** : Codes techniques RCP
- `rcp2_c2_den_etbt` : Dénominateur RCP
- `rcp2_c2_etbt` : Score RCP (0-100)
- `rcp2_c2_icbas_etbt` : Intervalle confiance bas
- `rcp2_c2_ichaut_etbt` : Intervalle confiance haut

**⚠️ Indicateur technique RCP, PAS de satisfaction patients !**

---

## ✅ SOLUTION : MODÈLE EN 2 TABLES DE FAITS DISTINCTES

### FAIT_SATISFACTION_PATIENT (Format A uniquement - ESATIS48H)
**Processus métier** : Évaluation qualité perçue par les patients hospitalisés

**Source** : `resultats-esatis48h-mco-open-data-2019.csv` + équivalents 2015-2018

**Granularité** : 1 ligne = 1 établissement × 1 période d'enquête

**Dimensions liées** :
- `sk_temps` → DIM_TEMPS (année enquête)
- `sk_etablissement` → DIM_ETABLISSEMENT (finess)
- `sk_type_enquete` → DIM_TYPE_ENQUETE (ESATIS48H)

**Mesures réelles** :
```sql
nb_reponses                INT,          -- nb_rep_score_all_rea_ajust
score_global               DECIMAL(5,2), -- score_all_rea_ajust
score_accueil              DECIMAL(5,2), -- score_accueil_rea_ajust
score_pec_infirmiere       DECIMAL(5,2), -- score_PECinf_rea_ajust
score_pec_medicale         DECIMAL(5,2), -- score_PECmed_rea_ajust
score_chambre              DECIMAL(5,2), -- score_chambre_rea_ajust
score_repas                DECIMAL(5,2), -- score_repas_rea_ajust
score_sortie               DECIMAL(5,2), -- score_sortie_rea_ajust
classement                 VARCHAR(10),  -- A, B, C, NV (Nouveau), DI (Donnée insuffisante)
evolution                  VARCHAR(50),  -- Amélioration, Stable, Dégradation, Non comparable
taux_recommandation_brut   DECIMAL(5,2), -- taux_reco_brut
nb_recommandations         INT           -- nb_reco_brut
```

**Transformation T2 nécessaire** :
- Harmoniser les noms de colonnes entre années (2015: `hpp_`, 2016: `dan_`, 2017: `ESATIS48H_`, 2019: `score_`)
- Normaliser les scores (certains sont 0-100, d'autres 0-10)
- Mapper les classements (A/B/C vs codes numériques selon années)

---

### FAIT_INDICATEURS_QUALITE (Formats B, C, D - Indicateurs techniques)
**Processus métier** : Suivi qualité et sécurité des soins (processus internes)

**Sources** :
- `resultats-iqss-open-data-2019.csv` (IQSS)
- `dpa-ssr-recueil2018-donnee2017-donnees.csv` (DPA SSR)
- `RCP_MCO_recueil2014_donnee2013_table_es.csv` (RCP MCO)

**Granularité** : 1 ligne = 1 établissement × 1 type indicateur × 1 période

**Dimensions liées** :
- `sk_temps` → DIM_TEMPS
- `sk_etablissement` → DIM_ETABLISSEMENT
- `sk_type_indicateur` → DIM_TYPE_INDICATEUR (nouvelle dimension)

**Structure pivotée** :
```sql
code_indicateur            VARCHAR(50),  -- ias_icsha_v3_mhs, dpa_qls_v2_mco, etc.
libelle_indicateur         VARCHAR(200), -- "Consommation SHA", "Qualité lettre liaison"
valeur_indicateur          DECIMAL(10,2),-- Valeur numérique
classe_indicateur          VARCHAR(10),  -- A, B, C
evolution_indicateur       VARCHAR(50),  -- Amélioration, Stable, etc.
type_mesure                VARCHAR(50),  -- Résultat, Classe, Évolution
```

**Transformation T2 nécessaire** :
- **PIVOT** : passer de format "wide" (46 colonnes) à format "long" (1 ligne par indicateur)
- Mapping des codes techniques vers libellés (via fichiers lexique)
- Normalisation des échelles de mesure

---

## 📊 DIMENSION SUPPLÉMENTAIRE NÉCESSAIRE

### DIM_TYPE_INDICATEUR
**Rôle** : Référentiel des indicateurs qualité/sécurité

**Attributs** :
```sql
sk_type_indicateur         INT PK,
code_indicateur            VARCHAR(50),  -- ias_icsha_v3_mhs, dpa_qls_v2_mco
libelle_court              VARCHAR(100), -- "SHA MCO/HAD/SSR"
libelle_complet            VARCHAR(500), -- "Consommation de solutions hydro-alcooliques..."
categorie                  VARCHAR(50),  -- IAS, DPA, CA, IQSS, ESATIS, RCP
domaine                    VARCHAR(50),  -- Hygiène, Documentation, Douleur, Nutrition
type_secteur               VARCHAR(50),  -- MCO, SSR, HAD, PSY
echelle_min                DECIMAL(5,2), -- 0
echelle_max                DECIMAL(5,2), -- 100
unite_mesure               VARCHAR(20),  -- %, Score, Ratio
```

**Source** : Fichiers lexique (`lexique-iqss-open-data-2019.csv`, etc.)

---

## 🔄 JOBS D'ALIMENTATION RÉVISÉS

### Job T2-Satisfaction-Patient
**Entrée** : CSV ESATIS48H (2015-2019)
**Sortie** : FAIT_SATISFACTION_PATIENT

**Étapes** :
1. Filtrer uniquement fichiers ESATIS48H (format patient)
2. Harmoniser noms colonnes selon année :
   ```python
   mapping = {
       '2015': {'hpp_mco_': 'score_'},
       '2016': {'dan_mco_': 'score_'},
       '2017': {'ESATIS48H_': 'score_'},
       '2019': {'score_': 'score_'}
   }
   ```
3. Normaliser scores (ramener tous sur 0-100)
4. Mapper classements vers A/B/C standard
5. Jointure avec DIM_ETABLISSEMENT (finess)
6. Jointure avec DIM_TEMPS (année enquête)

### Job T2-Indicateurs-Qualite
**Entrée** : CSV IQSS, DPA, RCP (2014-2019)
**Sortie** : FAIT_INDICATEURS_QUALITE

**Étapes** :
1. Charger fichiers lexique pour mapping codes
2. **PIVOT** : transformer colonnes multiples → lignes multiples
   ```python
   # Avant (wide) : finess | res_ias_icsha | res_dpa_qls | res_dpa_pcd
   # Après (long) : finess | code_indicateur | valeur
   ```
3. Enrichir avec libellés depuis lexique
4. Normaliser échelles de mesure
5. Créer DIM_TYPE_INDICATEUR
6. Jointures établissement + temps

---

## 📝 RECOMMANDATION FINALE

### Option 1 : Garder UNIQUEMENT ESATIS48H (satisfaction patient)
**Avantages** :
- Données homogènes, comparables dans le temps
- Sens métier clair pour analyses décisionnelles
- Moins de complexité ETL

**Inconvénients** :
- Perte de 70% des fichiers satisfaction (IQSS, DPA, RCP)

### Option 2 : Modéliser les 2 faits séparément (RECOMMANDÉ)
**Avantages** :
- Conservation complète des données sources
- Séparation claire satisfaction patient vs indicateurs qualité
- Analyses riches (corrélations satisfaction ↔ indicateurs)

**Inconvénients** :
- Complexité ETL accrue (pivot, harmonisation)
- 2 tables de faits à maintenir

### Option 3 : Tout mettre dans une table générique
**Avantages** :
- Flexibilité maximale

**Inconvénients** :
- Modèle peu lisible pour analystes
- Performances dégradées (NULL partout)

---

## ✅ PREUVE FINALE

**MON ERREUR INITIALE** :
- J'ai inventé des colonnes "score_soins" qui n'existent PAS
- J'ai mélangé satisfaction patient (ESATIS) et indicateurs qualité (IQSS/DPA)
- Je n'ai pas pris en compte l'hétérogénéité des formats

**CE QUI EXISTE VRAIMENT** :
- ESATIS48H : scores patient (accueil, PEC infirmière, PEC médicale, chambre, repas, sortie)
- IQSS : 46 indicateurs techniques qualité/sécurité (SHA, lettre liaison, douleur, etc.)
- DPA : indicateurs audit dossier patient
- RCP : indicateurs réunions pluridisciplinaires

**SOLUTION PROPOSÉE** :
- Séparer en 2 faits distincts avec structures claires
- Transformer IQSS/DPA/RCP avec PIVOT pour normaliser
- Créer DIM_TYPE_INDICATEUR pour référencer les codes techniques

---

**Voulez-vous que je regénère les fichiers (schéma Mermaid, rapport LaTeX, JSON) avec cette modélisation RÉELLE ?**
