"""Test détaillé du scraping INPI pour extraire le dirigeant."""

import requests
from bs4 import BeautifulSoup

siren = "532321916"  # KARAVEL

url = f"https://data.inpi.fr/entreprises/{siren}"
print(f"Test scraping INPI pour {siren}\n")

try:
    response = requests.get(url, timeout=30, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Chercher la section "Gestion et Direction"
        print("Recherche de la section 'Gestion et Direction'...\n")

        # Méthode 1: Trouver le h2 "Gestion et Direction" puis chercher le contenu après
        gestion_h2 = soup.find('h2', string='Gestion et Direction')
        if gestion_h2:
            print("✅ Section 'Gestion et Direction' trouvée!")

            # Trouver le contenu après ce h2
            section = gestion_h2.find_next_sibling()
            print(f"\nContenu de la section:\n{section.get_text()}\n")

            # Chercher les dl/dt/dd (definition list)
            dl = gestion_h2.find_next('dl')
            if dl:
                print("=" * 80)
                print("Liste de définitions trouvée:")
                dts = dl.find_all('dt')
                dds = dl.find_all('dd')

                for dt, dd in zip(dts, dds):
                    role = dt.get_text().strip()
                    valeur = dd.get_text().strip()
                    print(f"\n{role}:")
                    print(f"  {valeur}")

        # Méthode 2: Chercher directement "Président" dans les dt
        print("\n" + "=" * 80)
        print("Recherche directe de 'Président', 'Gérant', etc...")

        all_dt = soup.find_all('dt')
        for dt in all_dt:
            text = dt.get_text().strip().lower()
            if any(keyword in text for keyword in ['président', 'gérant', 'directeur général']):
                dd = dt.find_next_sibling('dd')
                if dd:
                    print(f"\n{dt.get_text().strip()}:")
                    print(f"  {dd.get_text().strip()}")

    else:
        print(f"❌ Status: {response.status_code}")

except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
