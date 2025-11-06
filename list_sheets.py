"""Liste tous les onglets du fichier Excel."""

import pandas as pd

# Lire le fichier pour voir tous les onglets
xl_file = pd.ExcelFile("Redaction BAIL.xlsx")

print("Onglets disponibles dans 'Redaction BAIL.xlsx':")
for i, sheet in enumerate(xl_file.sheet_names, 1):
    print(f"{i}. '{sheet}'")
