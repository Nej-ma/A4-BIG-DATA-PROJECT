#!/usr/bin/env python3
"""
Analyse des fichiers satisfaction 2020 (format XLSX)
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from pathlib import Path
import pandas as pd

def analyser_xlsx(filepath):
    """Analyse un fichier XLSX"""
    try:
        # Lire le fichier Excel
        xls = pd.ExcelFile(filepath)

        print(f"\n{'='*100}")
        print(f"FICHIER: {filepath.name}")
        print(f"Taille: {filepath.stat().st_size / (1024*1024):.2f} MB")
        print(f"{'='*100}")

        print(f"\nNombre de feuilles: {len(xls.sheet_names)}")
        print(f"Feuilles: {xls.sheet_names}")

        # Analyser chaque feuille
        for sheet_name in xls.sheet_names:
            print(f"\n--- FEUILLE: {sheet_name} ---")

            df = pd.read_excel(xls, sheet_name=sheet_name)

            print(f"Dimensions: {df.shape[0]} lignes × {df.shape[1]} colonnes")
            print(f"\nColonnes ({len(df.columns)}):")

            # Identifier colonnes clés
            for col in df.columns[:20]:  # Limiter à 20 colonnes
                col_str = str(col)
                col_lower = col_str.lower()

                if any(kw in col_lower for kw in ['finess', 'raison', 'nom']):
                    print(f"  [ETAB] {col_str}")
                elif any(kw in col_lower for kw in ['score', 'res_', 'resultat']):
                    print(f"  [SCORE] {col_str}")
                elif any(kw in col_lower for kw in ['classe', 'classement']):
                    print(f"  [CLASS] {col_str}")
                elif any(kw in col_lower for kw in ['nb_rep', 'nb_', 'taux']):
                    print(f"  [QTE] {col_str}")
                elif any(kw in col_lower for kw in ['region', 'type', 'participation']):
                    print(f"  [CAT] {col_str}")
                else:
                    print(f"  {col_str}")

            if len(df.columns) > 20:
                print(f"  ... et {len(df.columns) - 20} autres colonnes")

            # Échantillon première ligne
            if len(df) > 0:
                print(f"\n[ECHANTILLON] Première ligne:")
                for col in list(df.columns)[:10]:
                    val = df[col].iloc[0]
                    if pd.notna(val):
                        print(f"  {col}: {val}")

        return True
    except Exception as e:
        print(f"[ERREUR] Impossible de lire {filepath.name}: {e}")
        return False

def main():
    base_path = Path(r"C:\Users\littl\Desktop\Big DATA\DATA 2024\Satisfaction\2020")

    print("="*100)
    print("ANALYSE DES FICHIERS SATISFACTION 2020")
    print("="*100)

    # Analyser uniquement les fichiers de résultats (pas les lexiques)
    fichiers_resultats = [
        "resultats-esatis48h-mco-open-data-2020.xlsx",
        "resultats-esatisca-mco-open-data-2020.xlsx",
        "resultats-iqss-open-data-2020.xlsx"
    ]

    for fichier in fichiers_resultats:
        filepath = base_path / fichier
        if filepath.exists():
            analyser_xlsx(filepath)
        else:
            print(f"\n[ATTENTION] Fichier non trouvé: {fichier}")

    print("\n\n" + "="*100)
    print("RECOMMANDATION FINALE")
    print("="*100)
    print("""
Pour votre Livrable 1, utilisez UNIQUEMENT les fichiers satisfaction 2020 :

1. resultats-esatis48h-mco-open-data-2020.xlsx
   - E-Satis 48h : satisfaction patient hospitalisé MCO
   - Scores: accueil, prise en charge, chambre, repas, sortie

2. resultats-esatisca-mco-open-data-2020.xlsx
   - E-Satis CA : satisfaction chirurgie ambulatoire
   - Même structure que ESATIS48H

=> Ignorer resultats-iqss-open-data-2020.xlsx (indicateurs techniques)

FAIT_SATISFACTION_PATIENT {
    sk_temps,                  -- 2020
    sk_etablissement,          -- finess
    nb_reponses,               -- Nombre questionnaires
    score_global,              -- Score global /100
    score_accueil,             -- Accueil
    score_pec_infirmiere,      -- Prise en charge infirmière
    score_pec_medicale,        -- Prise en charge médicale
    score_chambre,             -- Chambre
    score_repas,               -- Repas
    score_sortie,              -- Sortie
    classement,                -- A, B, C
    evolution                  -- Amélioration/Stable/Dégradation
}

Sources: 2 fichiers XLSX (ESATIS48H + ESATISCA) pour l'année 2020 uniquement.
""")

if __name__ == "__main__":
    main()
