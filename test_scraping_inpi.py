"""Test du scraping INPI pour trouver le dirigeant."""

import requests
from bs4 import BeautifulSoup

siren = "532321916"  # KARAVEL

url = f"https://data.inpi.fr/entreprises/{siren}"
print(f"URL INPI: {url}\n")

try:
    response = requests.get(url, timeout=30)
    print(f"Status: {response.status_code}\n")

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Sauvegarder le HTML pour analyse
        with open('inpi_page.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("✅ HTML sauvegardé dans inpi_page.html\n")

        # Chercher les sections avec "Dirigeant", "Président", "Gérant"
        print("Recherche de texte contenant 'dirigeant', 'président', 'gérant'...\n")

        # Méthode 1: Chercher dans tout le texte
        text = soup.get_text()
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in ['président', 'gérant', 'dirigeant', 'représentant']):
                print(f"Ligne {i}: {line.strip()}")
                # Afficher les lignes autour
                if i > 0:
                    print(f"  Avant: {lines[i-1].strip()}")
                if i < len(lines) - 1:
                    print(f"  Après: {lines[i+1].strip()}")
                print()

        # Méthode 2: Chercher des sections spécifiques
        print("\n" + "="*80)
        print("Sections trouvées:")
        sections = soup.find_all(['h2', 'h3', 'h4'])
        for section in sections:
            print(f"- {section.get_text().strip()}")

except Exception as e:
    print(f"❌ Erreur: {e}")
