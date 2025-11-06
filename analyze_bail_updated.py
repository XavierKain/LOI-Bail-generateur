"""Analyse du fichier Excel BAIL mis à jour avec le nouvel onglet."""

import pandas as pd

print("=" * 80)
print("ANALYSE DU FICHIER REDACTION BAIL.xlsx MIS À JOUR")
print("=" * 80)

# Lister tous les onglets
xl_file = pd.ExcelFile("Redaction BAIL.xlsx")
print(f"\nOnglets disponibles ({len(xl_file.sheet_names)}):")
for i, sheet in enumerate(xl_file.sheet_names, 1):
    print(f"  {i}. {sheet}")

# Analyser chaque onglet
for sheet_name in xl_file.sheet_names:
    print(f"\n{'=' * 80}")
    print(f"ONGLET: {sheet_name}")
    print('=' * 80)

    df = pd.read_excel("Redaction BAIL.xlsx", sheet_name=sheet_name)
    print(f"Dimensions: {df.shape[0]} lignes x {df.shape[1]} colonnes")
    print(f"Colonnes: {list(df.columns)[:10]}")  # Premières 10 colonnes

    # Afficher aperçu
    if df.shape[0] > 0:
        print(f"\nAperçu (5 premières lignes):")
        print(df.head().to_string()[:500])

print("\n" + "=" * 80)
