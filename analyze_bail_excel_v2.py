"""Analyse du fichier Redaction BAIL.xlsx pour comprendre la structure."""

import pandas as pd

# Lire les deux onglets
print("=" * 80)
print("ANALYSE DU FICHIER REDACTION BAIL.xlsx")
print("=" * 80)

# Onglet 1: Liste données BAIL
print("\n\n### ONGLET 1: Liste données BAIL ###\n")
df_donnees = pd.read_excel("Redaction BAIL.xlsx", sheet_name="Liste données BAIL")
print(f"Colonnes: {list(df_donnees.columns)}")
print(f"Nombre de lignes: {len(df_donnees)}\n")

# Afficher de manière plus lisible
for idx, row in df_donnees.iterrows():
    if pd.notna(row['Données Primaire']):
        source = row['Unnamed: 1'] if pd.notna(row['Unnamed: 1']) else ""
        print(f"{idx+1}. {row['Données Primaire']:35} | {source}")

# Sauvegarder en JSON pour inspection
df_donnees.to_json("bail_donnees.json", orient="records", indent=2, force_ascii=False)
print("\n✅ Sauvegardé dans bail_donnees.json")

# Onglet 2: Rédaction BAIL
print("\n\n### ONGLET 2: Rédaction BAIL ###\n")
df_redaction = pd.read_excel("Redaction BAIL.xlsx", sheet_name="Rédaction BAIL")
print(f"Colonnes: {list(df_redaction.columns)}")
print(f"Nombre de lignes: {len(df_redaction)}\n")

# Afficher les premières lignes pour comprendre la structure
print("Aperçu des premières lignes:")
print(df_redaction.head(20).to_string())

# Sauvegarder en JSON pour inspection détaillée
df_redaction.to_json("bail_redaction.json", orient="records", indent=2, force_ascii=False)
print("\n✅ Sauvegardé dans bail_redaction.json")

print("\n\n" + "=" * 80)
print("ANALYSE TERMINÉE - Voir bail_donnees.json et bail_redaction.json pour détails")
print("=" * 80)
