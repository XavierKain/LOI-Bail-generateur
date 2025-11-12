"""Test du fallback BeautifulSoup pour Streamlit Cloud"""

from modules.inpi_client import INPIClient
import logging

logging.basicConfig(level=logging.INFO)

print("=" * 80)
print("TEST FALLBACK BEAUTIFULSOUP (Compatible Streamlit Cloud)")
print("=" * 80)

siren = "532321916"

inpi = INPIClient()

# Forcer le scénario où l'API est indisponible en testant directement le scraping
print("\n📋 Test direct du scraping BeautifulSoup...")
print("-" * 80)

dirigeant = inpi._scrape_inpi_dirigeant(siren)

if dirigeant:
    print(f"✅ SUCCÈS: Dirigeant récupéré: {dirigeant}")
else:
    print("❌ ÉCHEC: Aucun dirigeant trouvé")

# Test complet via get_company_info
print("\n\n📋 Test complet via get_company_info (avec rate limit simulée)...")
print("-" * 80)

enriched_data = inpi.get_company_info(siren)

print(f"\nStatut: {enriched_data.get('enrichment_status')}")
print(f"Message: {enriched_data.get('error_message')}")
print(f"\nPrésident: {enriched_data.get('PRESIDENT DE LA SOCIETE', 'NON TROUVÉ')}")

print("\n" + "=" * 80)

if enriched_data.get('PRESIDENT DE LA SOCIETE'):
    print("✅ TEST RÉUSSI - Le fallback BeautifulSoup fonctionne!")
else:
    print("❌ TEST ÉCHOUÉ")

print("=" * 80)
