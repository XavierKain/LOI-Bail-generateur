"""Test du scraping INPI complet"""

from modules.inpi_client import INPIClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("\n" + "=" * 80)
print("TEST DU SCRAPING INPI COMPLET (FALLBACK)")
print("=" * 80)

# SIREN de test (celui du fichier de test)
siren = "532321916"

print(f"\n📋 SIREN à tester: {siren}")

# Créer le client INPI
inpi = INPIClient()

print("\n1️⃣ TEST DE get_company_info (avec fallback scraping)")
print("-" * 80)

# Appeler get_company_info qui va automatiquement utiliser le fallback scraping
# si l'API rate limit est atteinte
enriched_data = inpi.get_company_info(siren)

print(f"\n📊 Statut enrichissement: {enriched_data.get('enrichment_status')}")
print(f"💬 Message: {enriched_data.get('error_message', 'Aucun message')}")

print("\n📦 Données récupérées:")
print("-" * 80)

champs_importants = [
    "NOM DE LA SOCIETE",
    "TYPE DE SOCIETE",
    "ADRESSE DE DOMICILIATION",
    "CAPITAL SOCIAL",
    "LOCALITE RCS",
    "PRESIDENT DE LA SOCIETE"
]

for champ in champs_importants:
    valeur = enriched_data.get(champ, "❌ NON TROUVÉ")
    emoji = "✅" if valeur and valeur != "❌ NON TROUVÉ" else "❌"
    print(f"{emoji} {champ}: {valeur}")

# Compter combien de champs ont été remplis
champs_remplis = sum(1 for champ in champs_importants if enriched_data.get(champ))

print("\n" + "=" * 80)
print(f"RÉSULTAT: {champs_remplis}/{len(champs_importants)} champs remplis")
print("=" * 80)

if champs_remplis >= 4:
    print("✅ TEST RÉUSSI - La plupart des champs sont remplis")
else:
    print("⚠️  TEST PARTIEL - Certains champs manquent")

print()
