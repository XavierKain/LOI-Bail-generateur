"""Analyse du fichier Redaction BAIL.xlsx pour comprendre la structure."""

import pandas as pd
import json

# Lire les deux onglets
print("=" * 80)
print("ANALYSE DU FICHIER REDACTION BAIL.xlsx")
print("=" * 80)

# Onglet 1: Liste données BAIL
print("\n\n### ONGLET 1: Liste données BAIL ###\n")
df_donnees = pd.read_excel("Redaction BAIL.xlsx", sheet_name="Liste données BAIL")
print(f"Colonnes: {list(df_donnees.columns)}")
print(f"Nombre de lignes: {len(df_donnees)}")
print("\nContenu:")
print(df_donnees.to_string())

# Sauvegarder en JSON pour inspection
df_donnees.to_json("bail_donnees.json", orient="records", indent=2, force_ascii=False)
print("\n✅ Sauvegardé dans bail_donnees.json")

# Onglet 2: Rédaction Bail
print("\n\n### ONGLET 2: Rédaction Bail ###\n")
df_redaction = pd.read_excel("Redaction BAIL.xlsx", sheet_name="Rédaction Bail")
print(f"Colonnes: {list(df_redaction.columns)}")
print(f"Nombre de lignes: {len(df_redaction)}")
print("\nContenu:")
print(df_redaction.to_string())

# Sauvegarder en JSON pour inspection
df_redaction.to_json("bail_redaction.json", orient="records", indent=2, force_ascii=False)
print("\n✅ Sauvegardé dans bail_redaction.json")

print("\n\n" + "=" * 80)
print("ANALYSE TERMINÉE")
print("=" * 80)
