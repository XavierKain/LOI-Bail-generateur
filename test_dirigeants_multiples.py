"""Test de l'extraction du dirigeant pour plusieurs SIRETs."""

from modules.inpi_client import INPIClient
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

client = INPIClient()

# Test avec les trois SIRETs
test_cases = [
    ("532321916", "KARAVEL"),
    ("841917743", "Entreprise 2"),
    ("481283901", "FLEUX")
]

print("\nTest extraction dirigeants - Multiples SIRETs\n")
print("="*80)

for siret, nom in test_cases:
    print(f"\n{nom} (SIRET: {siret}):")
    print("-" * 40)

    result = client.get_company_info(siret)

    nom_societe = result.get("NOM DE LA SOCIETE", "?")
    dirigeant = result.get("PRESIDENT DE LA SOCIETE", "")

    print(f"  Société: {nom_societe}")
    print(f"  Dirigeant: {dirigeant if dirigeant else '❌ NON TROUVÉ'}")

    if dirigeant:
        print(f"  ✅ OK")
    else:
        print(f"  ❌ MANQUANT - Besoin d'investigation")

print("\n" + "="*80)
