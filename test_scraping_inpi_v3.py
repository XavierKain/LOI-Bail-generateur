"""Test extraction du dirigeant depuis INPI avec la bonne structure."""

import requests
from bs4 import BeautifulSoup

def scrape_inpi_dirigeant(siren: str):
    """Scrape le dirigeant depuis data.inpi.fr"""
    url = f"https://data.inpi.fr/entreprises/{siren}"
    print(f"URL: {url}\n")

    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        if response.status_code != 200:
            print(f"❌ Status {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Chercher la section "Gestion et Direction" (h3)
        gestion_h3 = soup.find('h3', string='Gestion et Direction')

        if not gestion_h3:
            print("❌ Section 'Gestion et Direction' non trouvée")
            return None

        print("✅ Section 'Gestion et Direction' trouvée")

        # Trouver tous les blocs dirigeant après ce h3
        section = gestion_h3.find_parent()
        blocs = section.find_all('div', class_='bloc-dirigeant')

        print(f"\nNombre de blocs dirigeant: {len(blocs)}\n")

        dirigeants_info = {}

        for bloc in blocs:
            # Chaque bloc contient un label (p avec inpi-light) et une valeur (p suivant)
            paragraphs = bloc.find_all('p')
            if len(paragraphs) >= 2:
                label = paragraphs[0].get_text().strip()
                valeur = paragraphs[1].get_text().strip()
                dirigeants_info[label] = valeur
                print(f"{label}: {valeur}")

        # Extraire le dirigeant (nom de la dénomination ou nom/prénom)
        if 'Dénomination' in dirigeants_info:
            dirigeant = dirigeants_info['Dénomination']
        elif 'Nom' in dirigeants_info and 'Prénom' in dirigeants_info:
            dirigeant = f"{dirigeants_info['Prénom']} {dirigeants_info['Nom']}"
        elif 'Nom' in dirigeants_info:
            dirigeant = dirigeants_info['Nom']
        else:
            print("\n❌ Impossible d'extraire le nom du dirigeant")
            return None

        print(f"\n✅ Dirigeant trouvé: {dirigeant}")
        return dirigeant

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None


# Test avec les 3 SIRETs
test_cases = [
    ("532321916", "KARAVEL"),
    ("841917743", "Entreprise 2"),
    ("481283901", "FLEUX")
]

print("Test scraping INPI pour multiples SIRETs\n")
print("=" * 80)

for siren, nom in test_cases:
    print(f"\n{nom} (SIREN: {siren}):")
    print("-" * 40)
    result = scrape_inpi_dirigeant(siren)
    print("=" * 80)
