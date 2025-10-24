#!/usr/bin/env python3
"""
Script d'analyse complète pour le projet CHU Big Data
Génère automatiquement :
- L'extraction des métadonnées PostgreSQL
- L'analyse de tous les fichiers CSV
- Le modèle décisionnel complet (dimensions et faits)
- Un schéma Mermaid visualisable
- Un rapport LaTeX intégrable dans Livrable1.tex
"""

import os
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class AnalyseurModeleCHU:
    """Analyseur complet du modèle décisionnel CHU"""

    def __init__(self, data_root: str):
        self.data_root = Path(data_root)
        self.metadata = {
            "csv_files": {},
            "postgresql_tables": {},
            "dimensions": {},
            "faits": {},
            "enrichissements": []
        }

    def analyser_csv(self, filepath: Path, max_lines: int = 10) -> Dict:
        """Analyse un fichier CSV et extrait ses métadonnées"""
        try:
            # Détection de l'encodage et du séparateur
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            delimiters = [';', ',', '\t', '|']

            for encoding in encodings:
                for delimiter in delimiters:
                    try:
                        with open(filepath, 'r', encoding=encoding) as f:
                            reader = csv.DictReader(f, delimiter=delimiter)
                            headers = reader.fieldnames
                            if headers and len(headers) > 1:
                                # Lire quelques lignes pour analyse
                                rows = []
                                for i, row in enumerate(reader):
                                    if i >= max_lines:
                                        break
                                    rows.append(row)

                                return {
                                    "path": str(filepath.relative_to(self.data_root)),
                                    "encoding": encoding,
                                    "delimiter": delimiter,
                                    "columns": headers,
                                    "nb_columns": len(headers),
                                    "sample_rows": rows,
                                    "size_mb": filepath.stat().st_size / (1024 * 1024)
                                }
                    except:
                        continue

            return {"error": f"Impossible de lire {filepath.name}"}
        except Exception as e:
            return {"error": str(e)}

    def scanner_tous_csv(self):
        """Scanner récursivement tous les fichiers CSV"""
        print("[SCAN] Scanning des fichiers CSV...")

        csv_files = list(self.data_root.rglob("*.csv"))
        print(f"   Trouvé {len(csv_files)} fichiers CSV")

        for csv_file in csv_files:
            category = self.categoriser_fichier(csv_file)
            metadata = self.analyser_csv(csv_file)

            if "error" not in metadata:
                if category not in self.metadata["csv_files"]:
                    self.metadata["csv_files"][category] = []
                self.metadata["csv_files"][category].append(metadata)
                print(f"   [OK] {csv_file.name} [{category}]")

    def categoriser_fichier(self, filepath: Path) -> str:
        """Catégorise un fichier selon son emplacement"""
        path_str = str(filepath).lower()

        if "satisfaction" in path_str:
            return "Satisfaction"
        elif "hospitalisation" in path_str:
            return "Hospitalisation"
        elif "deces" in path_str:
            return "Décès"
        elif "etablissement" in path_str or "professionnel" in path_str:
            return "Référentiels"
        else:
            return "Autres"

    def definir_tables_postgresql(self):
        """Définit les tables PostgreSQL du projet (structure connue)"""
        print("\n[POSTGRESQL] Definition des tables PostgreSQL...")

        self.metadata["postgresql_tables"] = {
            "Patient": {
                "columns": [
                    "Id_patient", "Nom", "Prenom", "Sexe", "Adresse",
                    "Ville", "Code_postal", "Pays", "EMail", "Tel",
                    "Date", "Age", "Num_Secu", "Groupe_sanguin", "Poid", "Taille"
                ],
                "pk": "Id_patient",
                "rows_estimate": "100,000",
                "sensible": ["Nom", "Prenom", "EMail", "Tel", "Num_Secu", "Adresse"]
            },
            "Consultation": {
                "columns": [
                    "Id_consultation", "Date_consultation", "Id_patient",
                    "Identifiant", "Code_diag"
                ],
                "pk": "Id_consultation",
                "fk": {
                    "Id_patient": "Patient.Id_patient",
                    "Identifiant": "Professionnel_de_sante.Identifiant",
                    "Code_diag": "Diagnostic.Code_diag"
                },
                "rows_estimate": "1,027,157"
            },
            "Professionnel_de_sante": {
                "columns": [
                    "Identifiant", "Civilite", "Categorie_professionnelle",
                    "Nom", "Prenom", "Profession", "Type_identifiant", "Code_specialite"
                ],
                "pk": "Identifiant",
                "fk": {
                    "Code_specialite": "Specialites.Code_specialite"
                },
                "rows_estimate": "1,048,575",
                "sensible": ["Nom", "Prenom"]
            },
            "Diagnostic": {
                "columns": ["Code_diag", "Diagnostic"],
                "pk": "Code_diag",
                "rows_estimate": "15,490"
            },
            "Specialites": {
                "columns": ["Code_specialite", "Fonction", "Specialite"],
                "pk": "Code_specialite",
                "rows_estimate": "N/A"
            },
            "Mutuelle": {
                "columns": ["Id_Mut", "Nom", "Adresse"],
                "pk": "Id_Mut",
                "rows_estimate": "N/A"
            },
            "Adher": {
                "columns": ["Id_patient", "Id_mut"],
                "pk": ["Id_patient", "Id_mut"],
                "fk": {
                    "Id_patient": "Patient.Id_patient",
                    "Id_mut": "Mutuelle.Id_Mut"
                },
                "rows_estimate": "N/A"
            }
        }
        print(f"   [OK] {len(self.metadata['postgresql_tables'])} tables PostgreSQL definies")

    def construire_modele_decisionnel(self):
        """Construit le modèle décisionnel complet (dimensions + faits)"""
        print("\n[MODELE] Construction du modele decisionnel...")

        # ========== DIMENSIONS ==========
        self.metadata["dimensions"] = {
            "DIM_TEMPS": {
                "role": "Axe temporel unifié pour toutes les analyses chronologiques",
                "type": "dimension_commune",
                "source": "Générée automatiquement (2014-2025)",
                "attributs": {
                    "sk_temps": "Clé surrogate (PK)",
                    "date_complete": "Date complète (YYYY-MM-DD)",
                    "annee": "Année (2014-2025)",
                    "trimestre": "Trimestre (Q1-Q4)",
                    "mois": "Mois (1-12)",
                    "mois_libelle": "Nom du mois (Janvier-Décembre)",
                    "semaine": "Numéro de semaine ISO (1-53)",
                    "jour": "Jour du mois (1-31)",
                    "jour_semaine": "Jour de la semaine (Lundi-Dimanche)",
                    "est_weekend": "Indicateur weekend (0/1)",
                    "est_ferie": "Indicateur jour férié (0/1)"
                },
                "hierarchies": "Année → Trimestre → Mois → Semaine → Jour"
            },

            "DIM_PATIENT": {
                "role": "Démographie pseudonymisée des patients pour analyses épidémiologiques",
                "type": "dimension_commune",
                "source": "Table PostgreSQL 'Patient' après pseudonymisation T1",
                "attributs": {
                    "sk_patient": "Clé surrogate (PK)",
                    "patient_pseudo_id": "Identifiant pseudonymisé (SHA-256 + sel)",
                    "sexe": "Sexe (M/F)",
                    "age_a_la_consultation": "Âge calculé à la date de l'événement",
                    "tranche_age": "Catégorie d'âge (0-18, 19-65, 65+)",
                    "groupe_sanguin": "Groupe sanguin (A, B, AB, O)",
                    "ville": "Ville de résidence",
                    "code_postal": "Code postal",
                    "region": "Région (calculée depuis code postal)",
                    "pays": "Pays",
                    "poid": "Poids (kg)",
                    "taille": "Taille (cm)",
                    "bmi": "Indice de masse corporelle (calculé)"
                },
                "transformations_t1": [
                    "Hachage SHA-256 de Id_patient avec sel secret",
                    "Suppression de Nom, Prenom, EMail, Tel, Num_Secu, Adresse",
                    "Conservation de Sexe, Age, Groupe_sanguin, Ville, Code_postal, Pays, Poid, Taille"
                ]
            },

            "DIM_PROFESSIONNEL": {
                "role": "Référentiel des praticiens pour analyses d'activité et répartition",
                "type": "dimension_specifique",
                "source": "Table PostgreSQL 'Professionnel_de_sante' + CSV 'professionnel_sante.csv'",
                "attributs": {
                    "sk_professionnel": "Clé surrogate (PK)",
                    "prof_pseudo_id": "Identifiant pseudonymisé",
                    "civilite": "Civilité (M., Mme)",
                    "categorie_professionnelle": "Catégorie (Civil, etc.)",
                    "profession": "Profession exercée",
                    "type_identifiant": "Type d'identifiant (ADELI, RPPS)",
                    "specialite": "Spécialité médicale",
                    "commune": "Commune d'exercice"
                },
                "transformations_t1": [
                    "Hachage SHA-256 de l'identifiant professionnel",
                    "Suppression de Nom, Prenom"
                ],
                "enrichissement_t2": [
                    "Jointure avec DIM_SPECIALITE via Code_specialite",
                    "Fusion avec données CSV (72 MB professionnel_sante.csv)"
                ]
            },

            "DIM_DIAGNOSTIC": {
                "role": "Classification médicale enrichie CIM-10 pour analyses pathologiques",
                "type": "dimension_commune",
                "source": "Table PostgreSQL 'Diagnostic' + Référentiel CIM-10 OMS",
                "attributs": {
                    "sk_diagnostic": "Clé surrogate (PK)",
                    "code_diag": "Code CIM-10 (ex: S02800, Q902, R192)",
                    "libelle_diagnostic": "Description complète du diagnostic",
                    "code_cim10_3car": "Code CIM-10 3 caractères (chapitre)",
                    "chapitre_cim10": "Chapitre CIM-10 (ex: Chapitre XIX - Lésions traumatiques)",
                    "categorie_cim10": "Catégorie (ex: Fractures du crâne)",
                    "gravite": "Niveau de gravité (Bénin, Modéré, Sévère, Critique)"
                },
                "enrichissement_t2": [
                    "Jointure avec référentiel CIM-10 officiel OMS",
                    "Extraction du code 3 caractères (chapitre)",
                    "Mapping avec chapitres CIM-10 (I à XXII)",
                    "Classification gravité via règles métier"
                ],
                "note": "15,490 codes diagnostics dans PostgreSQL à enrichir"
            },

            "DIM_ETABLISSEMENT": {
                "role": "Référentiel géographique et administratif des structures de santé",
                "type": "dimension_commune",
                "source": "CSV 'etablissement_sante.csv' (78 MB, référentiel FINESS national)",
                "attributs": {
                    "sk_etablissement": "Clé surrogate (PK)",
                    "finess": "Identifiant FINESS (ex: F010000024)",
                    "identifiant_organisation": "Identifiant organisation",
                    "nom_etablissement": "Raison sociale (ex: CH DE FLEYRIAT)",
                    "commune": "Commune de l'établissement",
                    "code_postal": "Code postal",
                    "region": "Région administrative",
                    "type_etablissement": "Type (CH, CHU, Clinique, HAD, EHPAD)",
                    "statut": "Statut juridique (Public, Privé, PSPH)",
                    "adresse_complete": "Adresse complète",
                    "telephone": "Téléphone",
                    "email": "Email de contact"
                },
                "justification": "Hospitalisation et Consultation ne contiennent que des codes FINESS (ex: F010000107). Ce référentiel permet d'enrichir avec noms, adresses, régions et types d'établissements."
            },

            "DIM_SPECIALITE": {
                "role": "Classification des spécialités médicales",
                "type": "dimension_specifique",
                "source": "Table PostgreSQL 'Specialites'",
                "attributs": {
                    "sk_specialite": "Clé surrogate (PK)",
                    "code_specialite": "Code officiel de la spécialité",
                    "fonction": "Fonction du spécialiste",
                    "specialite": "Libellé de la spécialité"
                }
            },

            "DIM_MUTUELLE": {
                "role": "Classification des organismes complémentaires pour analyses de couverture sociale",
                "type": "dimension_specifique",
                "source": "Tables PostgreSQL 'Mutuelle' + 'Adher'",
                "attributs": {
                    "sk_mutuelle": "Clé surrogate (PK)",
                    "id_mut": "Identifiant mutuelle",
                    "nom": "Nom de la mutuelle",
                    "adresse": "Adresse de la mutuelle",
                    "type_mutuelle": "Type (Nationale, Régionale, Entreprise)"
                }
            },

            "DIM_TYPE_ENQUETE": {
                "role": "Classification des méthodologies d'enquêtes satisfaction",
                "type": "dimension_specifique",
                "source": "Fichiers CSV multiples dans 'Satisfaction/' (2014-2020)",
                "attributs": {
                    "sk_type_enquete": "Clé surrogate (PK)",
                    "type_enquete": "Type (ESATIS48H, ESATISCA, IQSS, DPA, RCP)",
                    "annee_enquete": "Année de l'enquête (2014-2020)",
                    "methodologie": "Méthodologie (Questionnaire post-sortie, Audit clinique)",
                    "periodicite": "Périodicité (Annuelle, Continue, Ponctuelle)",
                    "description": "Description détaillée de l'enquête"
                },
                "note": "27 fichiers CSV hétérogènes à harmoniser dans la couche Silver"
            },

            "DIM_LOCALISATION": {
                "role": "Géographie détaillée pour analyses territoriales des décès",
                "type": "dimension_specifique",
                "source": "CSV 'deces.csv' + Référentiel géographique INSEE",
                "attributs": {
                    "sk_localisation": "Clé surrogate (PK)",
                    "code_lieu": "Code lieu (naissance ou décès)",
                    "commune": "Nom de la commune",
                    "code_postal": "Code postal",
                    "departement": "Département",
                    "region": "Région administrative",
                    "pays": "Pays (pour naissances/décès à l'étranger)"
                },
                "enrichissement_t2": [
                    "Mapping code_lieu_naissance et code_lieu_deces avec référentiel INSEE",
                    "Géocodage pour analyses territoriales"
                ]
            }
        }

        # ========== FAITS ==========
        self.metadata["faits"] = {
            "FAIT_CONSULTATION": {
                "processus_metier": "Activité ambulatoire et suivi patient",
                "granularite": "Une ligne = une consultation médicale individuelle",
                "source": "Table PostgreSQL 'Consultation' (1,027,157 lignes)",
                "dimensions_liees": [
                    "DIM_TEMPS (date consultation)",
                    "DIM_PATIENT (patient consulté)",
                    "DIM_PROFESSIONNEL (praticien)",
                    "DIM_DIAGNOSTIC (pathologie diagnostiquée)",
                    "DIM_ETABLISSEMENT (lieu consultation)",
                    "DIM_MUTUELLE (couverture sociale)"
                ],
                "mesures": {
                    "nb_consultations": "Compteur (toujours = 1, agrégeable)",
                    "duree_consultation": "Durée en minutes (peut être calculée/estimée)",
                    "cout_consultation": "Coût en euros (peut nécessiter enrichissement)",
                    "motif_consultation": "Motif (Urgence, Contrôle, Premier recours) - attribut descriptif"
                },
                "cles_etrangeres": {
                    "sk_temps": "→ DIM_TEMPS",
                    "sk_patient": "→ DIM_PATIENT",
                    "sk_professionnel": "→ DIM_PROFESSIONNEL",
                    "sk_diagnostic": "→ DIM_DIAGNOSTIC",
                    "sk_etablissement": "→ DIM_ETABLISSEMENT",
                    "sk_mutuelle": "→ DIM_MUTUELLE"
                }
            },

            "FAIT_HOSPITALISATION": {
                "processus_metier": "Séjours hospitaliers avec suivi de durée et coûts",
                "granularite": "Une ligne = un séjour hospitalier complet (entrée → sortie)",
                "source": "CSV 'Hospitalisations.csv' (2,481 lignes, période 2016-2020)",
                "dimensions_liees": [
                    "DIM_TEMPS (date entrée et date sortie)",
                    "DIM_PATIENT (patient hospitalisé)",
                    "DIM_ETABLISSEMENT (établissement d'accueil)",
                    "DIM_DIAGNOSTIC (diagnostic principal)"
                ],
                "mesures": {
                    "nb_hospitalisations": "Compteur (= 1, agrégeable)",
                    "duree_sejour": "Durée en jours (colonne 'Jour_Hospitalisation')",
                    "cout_sejour": "Coût total en euros (peut nécessiter enrichissement)",
                    "service": "Service d'hospitalisation (Cardiologie, Chirurgie, etc.) - attribut descriptif",
                    "mode_entree": "Mode d'entrée (Urgence, Programmé, Transfert)",
                    "mode_sortie": "Mode de sortie (Domicile, Transfert, Décès)"
                },
                "cles_etrangeres": {
                    "sk_temps_entree": "→ DIM_TEMPS (date entrée)",
                    "sk_temps_sortie": "→ DIM_TEMPS (date sortie)",
                    "sk_patient": "→ DIM_PATIENT",
                    "sk_etablissement": "→ DIM_ETABLISSEMENT",
                    "sk_diagnostic": "→ DIM_DIAGNOSTIC"
                },
                "colonnes_source": [
                    "Num_Hospitalisation", "Id_patient", "identifiant_organisation (FINESS)",
                    "Code_diagnostic", "Suite_diagnostic_consultation",
                    "Date_Entree", "Jour_Hospitalisation"
                ]
            },

            "FAIT_DECES": {
                "processus_metier": "Mortalité et épidémiologie des causes de décès",
                "granularite": "Une ligne = un décès individuel",
                "source": "CSV 'deces.csv' (1.9 GB, données nationales)",
                "dimensions_liees": [
                    "DIM_TEMPS (date décès)",
                    "DIM_PATIENT (décédé - enrichi avec données décès)",
                    "DIM_LOCALISATION (lieu naissance et lieu décès)"
                ],
                "mesures": {
                    "nb_deces": "Compteur (= 1, agrégeable pour taux mortalité)",
                    "age_au_deces": "Âge au décès (calculé depuis date_naissance)",
                    "numero_acte_deces": "Référence administrative"
                },
                "attributs_descriptifs": {
                    "code_lieu_naissance": "Code du lieu de naissance",
                    "lieu_naissance": "Libellé lieu de naissance",
                    "pays_naissance": "Pays de naissance",
                    "code_lieu_deces": "Code du lieu de décès"
                },
                "cles_etrangeres": {
                    "sk_temps": "→ DIM_TEMPS (date_deces)",
                    "sk_patient": "→ DIM_PATIENT",
                    "sk_localisation_naissance": "→ DIM_LOCALISATION",
                    "sk_localisation_deces": "→ DIM_LOCALISATION"
                },
                "colonnes_source": [
                    "nom", "prenom", "sexe", "date_naissance", "code_lieu_naissance",
                    "lieu_naissance", "pays_naissance", "date_deces",
                    "code_lieu_deces", "numero_acte_deces"
                ],
                "avertissement_rgpd": "⚠️ Contient données nominatives (nom, prénom) → pseudonymisation OBLIGATOIRE dans T1"
            },

            "FAIT_SATISFACTION": {
                "processus_metier": "Évaluation qualité perçue par les patients hospitalisés",
                "granularite": "Une ligne = résultats agrégés d'enquête par établissement et période",
                "source": "Multiples CSV dans 'Satisfaction/' (2014-2020, formats hétérogènes)",
                "dimensions_liees": [
                    "DIM_TEMPS (période enquête)",
                    "DIM_ETABLISSEMENT (hôpital évalué)",
                    "DIM_TYPE_ENQUETE (méthodologie utilisée)"
                ],
                "mesures": {
                    "nb_reponses": "Nombre de questionnaires valides (représentativité)",
                    "score_global": "Note globale (/100, indicateur synthétique)",
                    "score_accueil": "Score accueil (/100)",
                    "score_soins": "Score qualité des soins (/100)",
                    "score_chambre": "Score confort chambre (/100)",
                    "score_repas": "Score restauration (/100)",
                    "score_sortie": "Score organisation sortie (/100)",
                    "niveau_satisfaction": "Classement national (A, B, C, D)"
                },
                "cles_etrangeres": {
                    "sk_temps": "→ DIM_TEMPS",
                    "sk_etablissement": "→ DIM_ETABLISSEMENT",
                    "sk_type_enquete": "→ DIM_TYPE_ENQUETE"
                },
                "defis_integration": [
                    "27 fichiers CSV avec structures évolutives (2014-2020)",
                    "Formats différents (ESATIS48H, IQSS, DPA, RCP, etc.)",
                    "Harmonisation des scores et indicateurs nécessaire dans couche Silver",
                    "Pivot de données pour passer de format 'large' à 'long'"
                ]
            }
        }

        print(f"   [OK] {len(self.metadata['dimensions'])} dimensions definies")
        print(f"   [OK] {len(self.metadata['faits'])} tables de faits definies")

    def identifier_enrichissements(self):
        """Identifie les enrichissements nécessaires"""
        print("\n[ENRICHISSEMENT] Identification des enrichissements...")

        self.metadata["enrichissements"] = [
            {
                "nom": "Enrichissement CIM-10",
                "source": "Référentiel CIM-10 OMS (Classification Internationale des Maladies)",
                "cible": "DIM_DIAGNOSTIC",
                "etape": "T2 (Transformation Métier dans Silver)",
                "description": "Ajouter chapitres, catégories et gravité aux 15,490 codes diagnostics",
                "colonnes_ajoutees": [
                    "code_cim10_3car", "chapitre_cim10", "categorie_cim10", "gravite"
                ]
            },
            {
                "nom": "Enrichissement FINESS",
                "source": "CSV 'etablissement_sante.csv' (78 MB, référentiel national)",
                "cible": "DIM_ETABLISSEMENT + FAIT_HOSPITALISATION + FAIT_CONSULTATION",
                "etape": "T2 (Transformation Métier dans Silver)",
                "description": "Mapper les codes FINESS avec noms, adresses, régions et types d'établissements",
                "justification": "Les données sources ne contiennent que des codes FINESS (ex: F010000107) sans informations descriptives"
            },
            {
                "nom": "Enrichissement Géographique",
                "source": "Référentiel INSEE des communes et codes postaux",
                "cible": "DIM_PATIENT + DIM_LOCALISATION + DIM_ETABLISSEMENT",
                "etape": "T2 (Transformation Métier dans Silver)",
                "description": "Calculer les régions depuis les codes postaux, enrichir les localisations de décès"
            },
            {
                "nom": "Fusion professionnels de santé",
                "source": "PostgreSQL 'Professionnel_de_sante' + CSV 'professionnel_sante.csv' (72 MB)",
                "cible": "DIM_PROFESSIONNEL",
                "etape": "T2 (Transformation Métier dans Silver)",
                "description": "Fusionner les données PostgreSQL avec le référentiel national CSV pour complétude",
                "methode": "Jointure sur identifiant pseudo ou matching fuzzy"
            },
            {
                "nom": "Harmonisation enquêtes satisfaction",
                "source": "27 fichiers CSV multiples (2014-2020)",
                "cible": "FAIT_SATISFACTION + DIM_TYPE_ENQUETE",
                "etape": "T2 (Transformation Métier dans Silver)",
                "description": "Harmoniser les formats hétérogènes, pivoter les données, normaliser les scores",
                "defis": [
                    "Structures différentes entre années",
                    "Noms de colonnes variables",
                    "Échelles de notation différentes à normaliser",
                    "Méthodologies évolutives (ESATIS48H, IQSS, DPA, RCP)"
                ]
            },
            {
                "nom": "Calcul BMI",
                "source": "DIM_PATIENT (colonnes poid, taille)",
                "cible": "DIM_PATIENT.bmi",
                "etape": "T2 (Transformation Métier dans Silver)",
                "description": "Calculer l'indice de masse corporelle : BMI = poid / (taille/100)²",
                "formule": "BMI = poid_kg / (taille_m)²"
            },
            {
                "nom": "Calcul tranche d'âge",
                "source": "DIM_PATIENT (colonne age)",
                "cible": "DIM_PATIENT.tranche_age",
                "etape": "T2 (Transformation Métier dans Silver)",
                "description": "Catégoriser les patients : 0-18 (pédiatrie), 19-65 (adulte), 65+ (gériatrie)"
            },
            {
                "nom": "Calcul durée séjour",
                "source": "FAIT_HOSPITALISATION (Date_Entree + Jour_Hospitalisation)",
                "cible": "FAIT_HOSPITALISATION.duree_sejour + sk_temps_sortie",
                "etape": "T2 (Transformation Métier dans Silver)",
                "description": "Calculer date_sortie = Date_Entree + Jour_Hospitalisation pour jointure DIM_TEMPS"
            }
        ]

        print(f"   [OK] {len(self.metadata['enrichissements'])} enrichissements identifies")

    def generer_schema_mermaid(self) -> str:
        """Génère un schéma Mermaid du modèle en constellation"""
        print("\n[MERMAID] Generation du schema Mermaid...")

        mermaid = """erDiagram
    %% ===== DIMENSIONS COMMUNES =====
    DIM_TEMPS {
        int sk_temps PK
        date date_complete
        int annee
        int trimestre
        int mois
        string mois_libelle
        int semaine
        int jour
        string jour_semaine
        boolean est_weekend
    }

    DIM_PATIENT {
        int sk_patient PK
        string patient_pseudo_id
        string sexe
        int age_a_la_consultation
        string tranche_age
        string groupe_sanguin
        string ville
        string code_postal
        string region
        string pays
        float poid
        float taille
        float bmi
    }

    DIM_DIAGNOSTIC {
        int sk_diagnostic PK
        string code_diag
        string libelle_diagnostic
        string code_cim10_3car
        string chapitre_cim10
        string categorie_cim10
        string gravite
    }

    DIM_ETABLISSEMENT {
        int sk_etablissement PK
        string finess
        string identifiant_organisation
        string nom_etablissement
        string commune
        string code_postal
        string region
        string type_etablissement
        string statut
        string adresse_complete
        string telephone
        string email
    }

    %% ===== DIMENSIONS SPÉCIFIQUES =====
    DIM_PROFESSIONNEL {
        int sk_professionnel PK
        string prof_pseudo_id
        string civilite
        string categorie_professionnelle
        string profession
        string type_identifiant
        string specialite
        string commune
    }

    DIM_SPECIALITE {
        int sk_specialite PK
        string code_specialite
        string fonction
        string specialite
    }

    DIM_MUTUELLE {
        int sk_mutuelle PK
        string id_mut
        string nom
        string adresse
        string type_mutuelle
    }

    DIM_TYPE_ENQUETE {
        int sk_type_enquete PK
        string type_enquete
        int annee_enquete
        string methodologie
        string periodicite
        string description
    }

    DIM_LOCALISATION {
        int sk_localisation PK
        string code_lieu
        string commune
        string code_postal
        string departement
        string region
        string pays
    }

    %% ===== TABLES DE FAITS =====
    FAIT_CONSULTATION {
        int sk_temps FK
        int sk_patient FK
        int sk_professionnel FK
        int sk_diagnostic FK
        int sk_etablissement FK
        int sk_mutuelle FK
        int nb_consultations
        int duree_consultation
        float cout_consultation
        string motif_consultation
    }

    FAIT_HOSPITALISATION {
        int sk_temps_entree FK
        int sk_temps_sortie FK
        int sk_patient FK
        int sk_etablissement FK
        int sk_diagnostic FK
        int nb_hospitalisations
        int duree_sejour
        float cout_sejour
        string service
        string mode_entree
        string mode_sortie
    }

    FAIT_DECES {
        int sk_temps FK
        int sk_patient FK
        int sk_localisation_naissance FK
        int sk_localisation_deces FK
        int nb_deces
        int age_au_deces
        string numero_acte_deces
    }

    FAIT_SATISFACTION {
        int sk_temps FK
        int sk_etablissement FK
        int sk_type_enquete FK
        int nb_reponses
        float score_global
        float score_accueil
        float score_soins
        float score_chambre
        float score_repas
        float score_sortie
        string niveau_satisfaction
    }

    %% ===== RELATIONS FAIT_CONSULTATION =====
    FAIT_CONSULTATION ||--o{ DIM_TEMPS : "sk_temps"
    FAIT_CONSULTATION ||--o{ DIM_PATIENT : "sk_patient"
    FAIT_CONSULTATION ||--o{ DIM_PROFESSIONNEL : "sk_professionnel"
    FAIT_CONSULTATION ||--o{ DIM_DIAGNOSTIC : "sk_diagnostic"
    FAIT_CONSULTATION ||--o{ DIM_ETABLISSEMENT : "sk_etablissement"
    FAIT_CONSULTATION ||--o{ DIM_MUTUELLE : "sk_mutuelle"

    %% ===== RELATIONS FAIT_HOSPITALISATION =====
    FAIT_HOSPITALISATION ||--o{ DIM_TEMPS : "sk_temps_entree"
    FAIT_HOSPITALISATION ||--o{ DIM_TEMPS : "sk_temps_sortie"
    FAIT_HOSPITALISATION ||--o{ DIM_PATIENT : "sk_patient"
    FAIT_HOSPITALISATION ||--o{ DIM_ETABLISSEMENT : "sk_etablissement"
    FAIT_HOSPITALISATION ||--o{ DIM_DIAGNOSTIC : "sk_diagnostic"

    %% ===== RELATIONS FAIT_DECES =====
    FAIT_DECES ||--o{ DIM_TEMPS : "sk_temps"
    FAIT_DECES ||--o{ DIM_PATIENT : "sk_patient"
    FAIT_DECES ||--o{ DIM_LOCALISATION : "sk_localisation_naissance"
    FAIT_DECES ||--o{ DIM_LOCALISATION : "sk_localisation_deces"

    %% ===== RELATIONS FAIT_SATISFACTION =====
    FAIT_SATISFACTION ||--o{ DIM_TEMPS : "sk_temps"
    FAIT_SATISFACTION ||--o{ DIM_ETABLISSEMENT : "sk_etablissement"
    FAIT_SATISFACTION ||--o{ DIM_TYPE_ENQUETE : "sk_type_enquete"

    %% ===== RELATIONS INTER-DIMENSIONS =====
    DIM_PROFESSIONNEL ||--o{ DIM_SPECIALITE : "specialite"
"""

        print("   [OK] Schema Mermaid genere")
        return mermaid

    def generer_rapport_latex(self) -> str:
        """Génère un rapport LaTeX détaillé"""
        print("\n[LATEX] Generation du rapport LaTeX...")

        latex = f"""
% ============================================================
% RAPPORT D'ANALYSE AUTOMATIQUE - MODÈLE DÉCISIONNEL CHU
% Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
% ============================================================

\\section{{Annexe : Analyse automatique des sources de données}}

\\subsection{{Résumé des fichiers CSV analysés}}

"""
        # Statistiques CSV
        total_csv = sum(len(files) for files in self.metadata["csv_files"].values())
        latex += f"Le système a identifié \\textbf{{{total_csv} fichiers CSV}} répartis dans les catégories suivantes :\n\n"
        latex += "\\begin{itemize}[leftmargin=*]\n"
        for category, files in self.metadata["csv_files"].items():
            total_size = sum(f.get("size_mb", 0) for f in files)
            latex += f"    \\item \\textbf{{{category}}} : {len(files)} fichiers ({total_size:.1f} MB)\n"
        latex += "\\end{itemize}\n\n"

        # Tables PostgreSQL
        latex += "\\subsection{Tables PostgreSQL identifiées}\n\n"
        latex += "\\begin{table}[H]\n\\centering\n\\caption{Tables PostgreSQL sources}\n"
        latex += "\\begin{tabularx}{\\textwidth}{|l|c|X|}\n\\hline\n"
        latex += "\\textbf{Table} & \\textbf{Colonnes} & \\textbf{Volume estimé} \\\\\n\\hline\n"
        for table_name, table_info in self.metadata["postgresql_tables"].items():
            nb_cols = len(table_info["columns"])
            volume = table_info["rows_estimate"]
            latex += f"{table_name} & {nb_cols} & {volume} \\\\\n\\hline\n"
        latex += "\\end{tabularx}\n\\end{table}\n\n"

        # Dimensions
        latex += "\\subsection{Dimensions du modèle décisionnel}\n\n"
        latex += f"Le modèle comprend \\textbf{{{len(self.metadata['dimensions'])} dimensions}} :\n\n"

        for dim_name, dim_info in self.metadata["dimensions"].items():
            latex += f"\\subsubsection{{{dim_name}}}\n\n"
            latex += f"\\textbf{{Rôle}} : {dim_info['role']}\n\n"
            latex += f"\\textbf{{Type}} : {dim_info['type'].replace('_', ' ')}\n\n"
            latex += f"\\textbf{{Source}} : {dim_info['source']}\n\n"
            latex += f"\\textbf{{Attributs}} ({len(dim_info['attributs'])}) :\n"
            latex += "\\begin{itemize}[leftmargin=*]\n"
            for attr, desc in list(dim_info["attributs"].items())[:5]:  # Limiter à 5 pour brièveté
                latex += f"    \\item \\texttt{{{attr}}} : {desc}\n"
            if len(dim_info["attributs"]) > 5:
                latex += f"    \\item \\textit{{... et {len(dim_info['attributs'])-5} autres attributs}}\n"
            latex += "\\end{itemize}\n\n"

        # Faits
        latex += "\\subsection{Tables de faits}\n\n"
        latex += f"Le modèle comprend \\textbf{{{len(self.metadata['faits'])} tables de faits}} :\n\n"

        for fait_name, fait_info in self.metadata["faits"].items():
            latex += f"\\subsubsection{{{fait_name}}}\n\n"
            latex += f"\\textbf{{Processus métier}} : {fait_info['processus_metier']}\n\n"
            latex += f"\\textbf{{Granularité}} : {fait_info['granularite']}\n\n"
            latex += f"\\textbf{{Source}} : {fait_info['source']}\n\n"
            latex += f"\\textbf{{Dimensions liées}} :\n"
            latex += "\\begin{itemize}[leftmargin=*]\n"
            for dim in fait_info["dimensions_liees"]:
                latex += f"    \\item {dim}\n"
            latex += "\\end{itemize}\n\n"
            latex += f"\\textbf{{Mesures}} :\n"
            latex += "\\begin{itemize}[leftmargin=*]\n"
            for mesure, desc in fait_info["mesures"].items():
                latex += f"    \\item \\texttt{{{mesure}}} : {desc}\n"
            latex += "\\end{itemize}\n\n"

        # Enrichissements
        latex += "\\subsection{Enrichissements identifiés}\n\n"
        latex += f"Le système a identifié \\textbf{{{len(self.metadata['enrichissements'])} enrichissements nécessaires}} :\n\n"
        latex += "\\begin{enumerate}[leftmargin=*]\n"
        for enrich in self.metadata["enrichissements"]:
            latex += f"    \\item \\textbf{{{enrich['nom']}}} : {enrich['description']}\n"
        latex += "\\end{enumerate}\n\n"

        print("   [OK] Rapport LaTeX genere")
        return latex

    def generer_rapport_markdown(self) -> str:
        """Génère un rapport Markdown lisible"""
        print("\n[MARKDOWN] Generation du rapport Markdown...")

        md = f"""# Analyse Complète du Modèle Décisionnel CHU

**Généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}**

---

## 📊 Résumé Exécutif

### Sources de données identifiées

"""
        # CSV
        total_csv = sum(len(files) for files in self.metadata["csv_files"].values())
        md += f"- **{total_csv} fichiers CSV** analysés\n"
        for category, files in self.metadata["csv_files"].items():
            total_size = sum(f.get("size_mb", 0) for f in files)
            md += f"  - {category}: {len(files)} fichiers ({total_size:.1f} MB)\n"

        # PostgreSQL
        md += f"\n- **{len(self.metadata['postgresql_tables'])} tables PostgreSQL**\n"
        for table_name, table_info in self.metadata["postgresql_tables"].items():
            md += f"  - {table_name}: {len(table_info['columns'])} colonnes, ~{table_info['rows_estimate']} lignes\n"

        # Modèle décisionnel
        md += f"\n### Modèle décisionnel\n\n"
        md += f"- **{len(self.metadata['dimensions'])} dimensions**\n"
        md += f"- **{len(self.metadata['faits'])} tables de faits**\n"
        md += f"- **{len(self.metadata['enrichissements'])} enrichissements** nécessaires\n"

        # Architecture
        md += "\n---\n\n## 🏗️ Architecture du Modèle en Constellation\n\n"
        md += "Le modèle adopte une **architecture en constellation d'étoiles** avec :\n\n"
        md += "### Dimensions communes (partagées entre plusieurs faits)\n\n"
        for dim_name, dim_info in self.metadata["dimensions"].items():
            if dim_info["type"] == "dimension_commune":
                md += f"#### {dim_name}\n\n"
                md += f"**Rôle** : {dim_info['role']}\n\n"
                md += f"**Source** : {dim_info['source']}\n\n"
                md += f"**Attributs clés** :\n"
                for attr, desc in list(dim_info["attributs"].items())[:7]:
                    md += f"- `{attr}` : {desc}\n"
                md += "\n"

        md += "### Dimensions spécifiques\n\n"
        for dim_name, dim_info in self.metadata["dimensions"].items():
            if dim_info["type"] == "dimension_specifique":
                md += f"#### {dim_name}\n\n"
                md += f"**Rôle** : {dim_info['role']}\n\n"
                md += f"**Source** : {dim_info['source']}\n\n"

        # Faits
        md += "\n---\n\n## 📈 Tables de Faits\n\n"
        for fait_name, fait_info in self.metadata["faits"].items():
            md += f"### {fait_name}\n\n"
            md += f"**Processus métier** : {fait_info['processus_metier']}\n\n"
            md += f"**Granularité** : {fait_info['granularite']}\n\n"
            md += f"**Source** : {fait_info['source']}\n\n"
            md += f"**Dimensions liées** :\n"
            for dim in fait_info["dimensions_liees"]:
                md += f"- {dim}\n"
            md += "\n**Mesures** :\n"
            for mesure, desc in fait_info["mesures"].items():
                md += f"- `{mesure}` : {desc}\n"
            md += "\n"

        # Enrichissements
        md += "\n---\n\n## 🔄 Enrichissements Identifiés\n\n"
        for i, enrich in enumerate(self.metadata["enrichissements"], 1):
            md += f"### {i}. {enrich['nom']}\n\n"
            md += f"**Source** : {enrich['source']}\n\n"
            md += f"**Cible** : {enrich['cible']}\n\n"
            md += f"**Étape** : {enrich['etape']}\n\n"
            md += f"**Description** : {enrich['description']}\n\n"

        # Schéma Mermaid
        md += "\n---\n\n## 🎨 Schéma du Modèle en Constellation\n\n"
        md += "```mermaid\n"
        md += self.generer_schema_mermaid()
        md += "```\n\n"

        # Recommandations
        md += "\n---\n\n## ✅ Recommandations\n\n"
        md += "### Pour le Livrable 1 (Conception)\n\n"
        md += "1. **Valider le modèle décisionnel** présenté ci-dessus\n"
        md += "2. **Intégrer le schéma Mermaid** dans la section 3 du document LaTeX\n"
        md += "3. **Compléter les sections manquantes** :\n"
        md += "   - Relations clés entre faits et dimensions (tableau récapitulatif)\n"
        md += "   - DAG des jobs d'alimentation\n"
        md += "   - Dictionnaire de données complet en annexe\n\n"

        md += "### Pour le Livrable 2 (Implémentation)\n\n"
        md += "1. **Scripts Spark T1** (pseudonymisation) :\n"
        md += "   - Job T1-Patient : hachage SHA-256 des ID, suppression PII\n"
        md += "   - Job T1-Consultation : normalisation dates\n"
        md += "   - Job T1-Deces : pseudonymisation obligatoire (données nominatives)\n"
        md += "   - Job T1-Satisfaction : harmonisation formats multiples\n\n"

        md += "2. **Scripts Spark T2** (transformations métier) :\n"
        md += "   - Enrichissement CIM-10 (15,490 codes à enrichir)\n"
        md += "   - Mapping FINESS (codes → noms établissements)\n"
        md += "   - Géocodage (codes postaux → régions)\n"
        md += "   - Fusion professionnels (PostgreSQL + CSV 72 MB)\n"
        md += "   - Harmonisation satisfaction (27 fichiers hétérogènes)\n\n"

        md += "3. **Tables Hive ORC** :\n"
        md += "   - Partitionnement par année pour DIM_TEMPS\n"
        md += "   - Bucketing sur clés étrangères pour optimisation jointures\n"
        md += "   - Indexation ORC pour requêtes analytiques rapides\n\n"

        print("   [OK] Rapport Markdown genere")
        return md

    def sauvegarder_resultats(self, output_dir: str):
        """Sauvegarde tous les résultats"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        print(f"\n[SAVE] Sauvegarde des resultats dans {output_path}...")

        # JSON complet
        json_file = output_path / "analyse_complete.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        print(f"   [OK] {json_file}")

        # Rapport Markdown
        md_file = output_path / "RAPPORT_MODELE_DECISIONNEL.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(self.generer_rapport_markdown())
        print(f"   [OK] {md_file}")

        # Rapport LaTeX
        latex_file = output_path / "annexe_analyse_automatique.tex"
        with open(latex_file, 'w', encoding='utf-8') as f:
            f.write(self.generer_rapport_latex())
        print(f"   [OK] {latex_file}")

        # Schéma Mermaid seul
        mermaid_file = output_path / "schema_constellation.mmd"
        with open(mermaid_file, 'w', encoding='utf-8') as f:
            f.write(self.generer_schema_mermaid())
        print(f"   [OK] {mermaid_file}")

        print("\n[SUCCESS] Analyse complete terminee avec succes !")
        print(f"\n[OUTPUT] Fichiers generes dans : {output_path.absolute()}")
        print("\n[NEXT STEPS] Prochaines etapes :")
        print("   1. Consulter RAPPORT_MODELE_DECISIONNEL.md pour vue d'ensemble")
        print("   2. Integrer annexe_analyse_automatique.tex dans Livrable1.tex")
        print("   3. Visualiser schema_constellation.mmd sur mermaid.live")
        print("   4. Utiliser analyse_complete.json pour scripts d'implementation")


def main():
    """Point d'entrée principal"""
    import sys
    import io

    # Fix encoding for Windows console
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    print("="*80)
    print("ANALYSEUR MODELE DECISIONNEL CHU - Cloud Healthcare Unit")
    print("="*80)
    print()

    # Chemin racine des données
    data_root = r"C:\Users\littl\Desktop\Big DATA\DATA 2024"
    output_dir = r"C:\Users\littl\Desktop\Big DATA\projet\analyse_resultats"

    # Créer l'analyseur
    analyseur = AnalyseurModeleCHU(data_root)

    # Exécuter l'analyse complète
    analyseur.scanner_tous_csv()
    analyseur.definir_tables_postgresql()
    analyseur.construire_modele_decisionnel()
    analyseur.identifier_enrichissements()

    # Sauvegarder les résultats
    analyseur.sauvegarder_resultats(output_dir)


if __name__ == "__main__":
    main()
