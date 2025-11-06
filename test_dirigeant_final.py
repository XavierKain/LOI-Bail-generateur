"""Test final de l'extraction du dirigeant."""

from modules.inpi_client import INPIClient
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

client = INPIClient()

# Test avec les deux SIRENs
sirens = [
    ("532321916", "KARAVEL"),
    ("481283901", "FLEUX")
]

print("\nTest extraction dirigeants\n")
print("="*80)

for siren, nom in sirens:
    print(f"\n{nom} (SIREN: {siren}):")
    result = client.get_company_info(siren)

    nom_societe = result.get("NOM DE LA SOCIETE", "?")
    dirigeant = result.get("PRESIDENT DE LA SOCIETE", "")

    print(f"  Société: {nom_societe}")
    print(f"  Dirigeant: {dirigeant if dirigeant else '❌ NON TROUVÉ'}")

    if dirigeant:
        print(f"  ✅ OK")
    else:
        print(f"  ❌ MANQUANT")

print("\n" + "="*80)
