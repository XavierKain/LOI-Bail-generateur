"""Test du placeholder Date de Prise d'effet + 9 ans"""

from modules.bail_generator import BailGenerator

# Test simple
donnees = {"Date de prise d'effet": "01/01/2025"}

# Simuler la normalisation
gen = BailGenerator("Redaction BAIL.xlsx")
derivees = gen.calculer_variables_derivees(donnees)

print("Variables dérivées:")
for key, value in derivees.items():
    print(f"  {key}: {value}")

# Tester l'accès avec différentes casses
print()
print("Test accès:")
key1 = "Date de prise d'effet + 9 ans"
key2 = "Date de Prise d'effet + 9 ans"
print(f"  derivees.get('{key1}'): {derivees.get(key1)}")
print(f"  derivees.get('{key2}'): {derivees.get(key2)}")
