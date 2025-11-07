"""Test de toutes les corrections"""

from modules.bail_generator import BailGenerator

# Test données
donnees = {
    "Date de prise d'effet": "01/01/2025",
    "Durée Bail": "9",
    "Montant du loyer": "50000",
}

gen = BailGenerator("Redaction BAIL.xlsx")

# Test génération articles
articles = gen.generer_bail(donnees)

print(f"Articles générés: {len(articles)}")
print("Liste des articles:")
for key in articles.keys():
    print(f"  - {key}")

# Vérifier Comparution
if "Comparution Bailleur" in articles:
    print("\n✅ Comparution Bailleur trouvée")
else:
    print("\n❌ Comparution Bailleur MANQUANTE")

if "Comparution Preneur" in articles:
    print("✅ Comparution Preneur trouvée")
else:
    print("❌ Comparution Preneur MANQUANTE")

# Vérifier les variables dérivées
print("\n\nVariables dérivées:")
derivees = gen.calculer_variables_derivees(donnees)
for key, value in derivees.items():
    if key not in donnees:
        print(f"  {key}: {value}")

# Test date +9 ans avec différentes casses
print("\n\nTest Date de Prise d'effet + 9 ans:")
key1 = "Date de prise d'effet + 9 ans"
key2 = "Date de Prise d'effet + 9 ans"
print(f"  {key1}: {derivees.get(key1)}")
print(f"  {key2}: {derivees.get(key2)}")
