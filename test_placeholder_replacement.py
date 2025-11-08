"""Test du remplacement de placeholders"""

from modules.bail_generator import BailGenerator
import re

# Créer des données de test
donnees = {
    "Date de prise d'effet": "01/01/2025",
    "Nom Preneur": "Test SAS",
}

gen = BailGenerator("Redaction BAIL.xlsx")
donnees_complete = gen.calculer_variables_derivees(donnees)

print("Variables dans donnees_complete:")
for key in sorted(donnees_complete.keys()):
    print(f"  '{key}': {donnees_complete[key]}")

# Simuler le remplacement d'un placeholder
test_placeholders = [
    "[Date de prise d'effet]",
    "[Date de Prise d'effet + 9 ans]",
    "[Date de prise d'effet + 9 ans]",
    "[Nom Preneur]",
]

print("\n\nTest de remplacement:")
for placeholder in test_placeholders:
    # Extraire le nom de la variable
    match = re.match(r'\[([^\]]+)\]', placeholder)
    if match:
        var_name = match.group(1)
        value = donnees_complete.get(var_name)
        print(f"  {placeholder} → {value if value else '❌ NOT FOUND'}")
