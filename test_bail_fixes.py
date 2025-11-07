"""
Test rapide des corrections BAIL
"""

from modules.bail_generator import BailGenerator
from modules.number_to_french import number_to_french_words

# Test 1: Conversion nombre en lettres avec espace
print("=" * 60)
print("Test 1: Conversion nombre en lettres")
print("=" * 60)

montants = [5000, 12500, 40000, 50000, 160000]
for montant in montants:
    words = number_to_french_words(montant)
    # Simuler le résultat avec espace après
    result = words + " euros"
    print(f"{montant} → {result}")

print()

# Test 2: Calcul de Date de prise d'effet + 9 ans
print("=" * 60)
print("Test 2: Calcul Date de prise d'effet + 9 ans")
print("=" * 60)

generator = BailGenerator("Redaction BAIL.xlsx")

# Cas de test avec différentes variations de nom
test_data = [
    {"Date de prise d'effet": "01/01/2025"},
    {"Date prise d'effet": "15/03/2024"},
    {"Date début bail": "01/06/2023"},
]

for data in test_data:
    print(f"Input: {data}")
    derivees = generator.calculer_variables_derivees(data)
    date_calculee = derivees.get("Date de prise d'effet + 9 ans")
    print(f"  → Date de prise d'effet + 9 ans: {date_calculee}")
    print()

# Test 3: Normalisation des noms de variables
print("=" * 60)
print("Test 3: Normalisation des noms de variables")
print("=" * 60)

test_vars = {
    "Date prise d'effet": "01/01/2025",
    "Date de prise d'effet du bail": "15/03/2024",
    "Durée du Bail": "9",
    "Montant du Palier 1": "5000",
}

print("Variables en entrée:")
for key, value in test_vars.items():
    print(f"  {key}: {value}")

derivees = generator.calculer_variables_derivees(test_vars)

print("\nVariables après normalisation et calcul:")
for key, value in sorted(derivees.items()):
    print(f"  {key}: {value}")

print("\n✓ Tests terminés!")
