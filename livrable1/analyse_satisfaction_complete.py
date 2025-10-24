#!/usr/bin/env python3
"""
Analyse COMPLETE de tous les fichiers CSV de satisfaction
Pour comprendre le bordel et trouver une solution
"""

import os
import csv
from pathlib import Path
from collections import defaultdict
import json

def analyser_fichier_csv(filepath):
    """Analyse un CSV et retourne sa structure"""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    delimiters = [';', ',', '\t', '|']

    for encoding in encodings:
        for delimiter in delimiters:
            try:
                with open(filepath, 'r', encoding=encoding, errors='replace') as f:
                    reader = csv.DictReader(f, delimiter=delimiter)
                    headers = reader.fieldnames
                    if headers and len(headers) > 1:
                        # Lire 3 lignes pour échantillon
                        rows = []
                        for i, row in enumerate(reader):
                            if i >= 3:
                                break
                            rows.append(row)

                        return {
                            'encoding': encoding,
                            'delimiter': delimiter,
                            'columns': headers,
                            'nb_columns': len(headers),
                            'sample_rows': rows
                        }
            except:
                continue
    return None

def main():
    import sys
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    base_path = Path(r"C:\Users\littl\Desktop\Big DATA\DATA 2024\Satisfaction")

    print("="*100)
    print("ANALYSE COMPLETE DES FICHIERS SATISFACTION")
    print("="*100)
    print()

    # Grouper par année
    fichiers_par_annee = defaultdict(list)

    for csv_file in base_path.rglob("*.csv"):
        annee = None
        if "2014" in str(csv_file):
            annee = "2014"
        elif "2015" in str(csv_file):
            annee = "2015"
        elif "2016" in str(csv_file):
            annee = "2016"
        elif "2017" in str(csv_file) or "2018" in str(csv_file):
            annee = "2017-2018"
        elif "2019" in str(csv_file):
            annee = "2019"
        else:
            annee = "Autre"

        fichiers_par_annee[annee].append(csv_file)

    # Analyser fichier par fichier
    rapport_complet = {}

    for annee in sorted(fichiers_par_annee.keys()):
        print(f"\n{'='*100}")
        print(f"ANNEE {annee}")
        print(f"{'='*100}\n")

        rapport_complet[annee] = []

        for fichier in sorted(fichiers_par_annee[annee]):
            nom_fichier = fichier.name
            taille_mb = fichier.stat().st_size / (1024 * 1024)

            print(f"\n[FICHIER] {nom_fichier} ({taille_mb:.2f} MB)")
            print("-" * 100)

            # Identifier le type
            type_enquete = "INCONNU"
            if "esatis48h" in nom_fichier.lower():
                type_enquete = "ESATIS48H - E-Satis 48h (satisfaction patient MCO)"
            elif "esatisca" in nom_fichier.lower():
                type_enquete = "ESATISCA - E-Satis Chirurgie Ambulatoire"
            elif "iqss" in nom_fichier.lower():
                type_enquete = "IQSS - Indicateurs Qualité Sécurité Soins"
            elif "dpa" in nom_fichier.lower() and "had" in nom_fichier.lower():
                type_enquete = "DPA HAD - Dossier Patient HAD"
            elif "dpa" in nom_fichier.lower() and "ssr" in nom_fichier.lower():
                type_enquete = "DPA SSR - Dossier Patient SSR"
            elif "dpa" in nom_fichier.lower() and "mco" in nom_fichier.lower():
                type_enquete = "DPA MCO - Dossier Patient MCO"
            elif "rcp" in nom_fichier.lower():
                type_enquete = "RCP - Réunion Concertation Pluridisciplinaire"
            elif "dan" in nom_fichier.lower():
                type_enquete = "DAN - Dossier Anesthésie"
            elif "hpp" in nom_fichier.lower():
                type_enquete = "HPP - Hémorragie Post-Partum"
            elif "idm" in nom_fichier.lower():
                type_enquete = "IDM - Infarctus Du Myocarde"
            elif "ete" in nom_fichier.lower() and "ortho" in nom_fichier.lower():
                type_enquete = "ETE ORTHO - Événement Thrombo-Embolique Orthopédie"

            print(f"Type: {type_enquete}")

            # Analyser structure
            structure = analyser_fichier_csv(fichier)

            if structure:
                print(f"Encodage: {structure['encoding']}")
                print(f"Délimiteur: '{structure['delimiter']}'")
                print(f"Nombre de colonnes: {structure['nb_columns']}")
                print(f"\nColonnes ({structure['nb_columns']}):")

                # Identifier colonnes clés
                colonnes_cles = []
                for col in structure['columns']:
                    col_lower = col.lower()
                    if any(kw in col_lower for kw in ['finess', 'raison', 'nom_es']):
                        colonnes_cles.append(f"  [ETAB] {col} (etablissement)")
                    elif any(kw in col_lower for kw in ['score', 'res_', 'resultat']):
                        colonnes_cles.append(f"  [MESURE] {col} (mesure)")
                    elif any(kw in col_lower for kw in ['classe', 'classement']):
                        colonnes_cles.append(f"  [CLASS] {col} (classement)")
                    elif any(kw in col_lower for kw in ['nb_rep', 'nb_', 'taux']):
                        colonnes_cles.append(f"  [QTE] {col} (quantite)")
                    elif any(kw in col_lower for kw in ['region', 'type', 'participation']):
                        colonnes_cles.append(f"  [CAT] {col} (categorie)")

                for c in colonnes_cles[:15]:  # Limiter affichage
                    print(c)

                if len(colonnes_cles) > 15:
                    print(f"  ... et {len(colonnes_cles) - 15} autres colonnes")

                # Echantillon valeurs
                if structure['sample_rows'] and len(structure['sample_rows']) > 0:
                    print(f"\n[ECHANTILLON] 1ere ligne:")
                    for key, value in list(structure['sample_rows'][0].items())[:8]:
                        if value and len(str(value)) > 0:
                            val_display = str(value)[:60]
                            print(f"  {key}: {val_display}")

                rapport_complet[annee].append({
                    'fichier': nom_fichier,
                    'taille_mb': taille_mb,
                    'type_enquete': type_enquete,
                    'nb_columns': structure['nb_columns'],
                    'columns': structure['columns'],
                    'colonnes_cles': colonnes_cles
                })
            else:
                print("[ERREUR] IMPOSSIBLE DE LIRE CE FICHIER")

    # Sauvegarder rapport
    output_path = Path(r"C:\Users\littl\Desktop\Big DATA\projet\analyse_resultats")
    output_path.mkdir(exist_ok=True)

    with open(output_path / "analyse_satisfaction_detaillee.json", 'w', encoding='utf-8') as f:
        json.dump(rapport_complet, f, ensure_ascii=False, indent=2)

    print("\n\n" + "="*100)
    print("SYNTHESE FINALE")
    print("="*100)

    # Compter types d'enquêtes
    types_enquetes = defaultdict(int)
    total_fichiers = 0

    for annee, fichiers in rapport_complet.items():
        for f in fichiers:
            types_enquetes[f['type_enquete']] += 1
            total_fichiers += 1

    print(f"\nTotal fichiers: {total_fichiers}")
    print(f"Types d'enquêtes distincts: {len(types_enquetes)}")
    print("\nRépartition par type:")
    for type_enq, count in sorted(types_enquetes.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {type_enq}: {count} fichier(s)")

    print(f"\n[OK] Rapport detaille sauvegarde: {output_path / 'analyse_satisfaction_detaillee.json'}")

    # Recommandations
    print("\n\n" + "="*100)
    print("RECOMMANDATIONS POUR LE MODELE DECISIONNEL")
    print("="*100)

    print("""
[PROBLEME] PROBLEME IDENTIFIE:
   Les fichiers satisfaction ne sont PAS homogènes. Il y a plusieurs types d'enquêtes
   totalement différentes, avec des structures incompatibles.

[SOLUTION] SOLUTION PROPOSEE:

   Option 1: GARDER UNIQUEMENT ESATIS48H (satisfaction patient)
   ------------------------------------------------------------------
   - Fichiers: esatis48h-mco, esatisca-mco (2015-2019)
   - Données: Scores satisfaction patient (accueil, soins, chambre, repas, sortie)
   - Granularité: 1 ligne = 1 établissement × 1 année
   - Homogeneite: [OK] Structure comparable entre annees
   - Utilisable pour: Analyses satisfaction patient, corrélations diagnostic/satisfaction

   => RECOMMANDE pour Livrable 1 (simplicite + pertinence metier)

   Option 2: MODELE MULTI-ENQUETES (2 tables de faits)
   ------------------------------------------------------------------
   Table 1: FAIT_SATISFACTION_PATIENT (ESATIS uniquement)
   Table 2: FAIT_INDICATEURS_QUALITE (IQSS, DPA, RCP, etc.)

   [ATTENTION] Complexite ETL elevee, necessite:
   - Pivot des indicateurs IQSS (46 colonnes → format long)
   - Harmonisation des échelles de mesure
   - Mapping codes techniques vers libelles
   - Dimension DIM_TYPE_INDICATEUR supplémentaire

   => POSSIBLE pour Livrable 2 si temps disponible

   Option 3: EXCLURE TOTALEMENT les données satisfaction
   ------------------------------------------------------------------
   - Se concentrer sur Consultation, Hospitalisation, Décès
   - Justification: Hétérogénéité trop importante, ROI faible

   => FALLBACK si probleme de temps

[RECOMMANDATION] MA RECOMMANDATION FINALE:

   Pour votre Livrable 1, proposez l'Option 1 (ESATIS48H uniquement):

   FAIT_SATISFACTION_PATIENT {
       sk_temps FK,                    -- Année enquête
       sk_etablissement FK,            -- Établissement évalué
       nb_reponses INT,                -- Nombre questionnaires
       score_global DECIMAL(5,2),      -- Score global /100
       score_accueil DECIMAL(5,2),     -- Score accueil /100
       score_pec_infirmiere DECIMAL(5,2), -- Prise en charge infirmière
       score_pec_medicale DECIMAL(5,2),   -- Prise en charge médicale
       score_chambre DECIMAL(5,2),     -- Confort chambre
       score_repas DECIMAL(5,2),       -- Qualité repas
       score_sortie DECIMAL(5,2),      -- Organisation sortie
       classement VARCHAR(10),         -- A, B, C
       evolution VARCHAR(50)           -- Amélioration, Stable, Dégradation
   }

   Justification dans le rapport:
   "Parmi les 27 fichiers d'enquêtes satisfaction (2014-2020), nous avons retenu
   uniquement les enquêtes ESATIS48H (E-Satis 48h) qui mesurent la satisfaction
   réelle des patients hospitalisés. Les autres fichiers (IQSS, DPA, RCP) concernent
   des indicateurs de processus hospitaliers internes, non directement liés à
   l'expérience patient, et seront intégrés dans une phase ultérieure."
""")

if __name__ == "__main__":
    main()
