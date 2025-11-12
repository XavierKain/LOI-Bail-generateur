"""Debug de la structure HTML de data.inpi.fr"""

import requests
from bs4 import BeautifulSoup

siren = "532321916"
url = f"https://data.inpi.fr/entreprises/{siren}"

print("=" * 80)
print(f"ANALYSE DE LA PAGE: {url}")
print("=" * 80)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers, timeout=30)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    # 1. Chercher le h1
    print("\n1️⃣ H1 TITLE:")
    print("-" * 80)
    h1 = soup.find('h1')
    if h1:
        print(f"✅ H1 trouvé: {h1.get_text().strip()}")
    else:
        print("❌ Pas de H1")

    # 2. Chercher la section identité
    print("\n2️⃣ SECTION IDENTITÉ:")
    print("-" * 80)
    identite = soup.find('div', id='identite')
    if identite:
        print("✅ Section identité trouvée")

        # Afficher toutes les lignes
        rows = identite.find_all('div', class_='row')
        print(f"   Nombre de rows: {len(rows)}")

        for idx, row in enumerate(rows[:10]):  # Limite à 10 premières lignes
            text = row.get_text(separator=' | ', strip=True)
            print(f"   Row {idx}: {text[:100]}")
    else:
        print("❌ Section identité non trouvée")

        # Essayer d'autres sélecteurs
        print("\n   Tentative de trouver des sections alternatives:")

        # Chercher tous les divs avec des IDs
        all_divs_with_id = soup.find_all('div', id=True)
        print(f"   Nombre de divs avec ID: {len(all_divs_with_id)}")
        for div in all_divs_with_id[:20]:
            print(f"     - ID: {div.get('id')}")

    # 3. Chercher la section gestion
    print("\n3️⃣ SECTION GESTION ET DIRECTION:")
    print("-" * 80)
    gestion = soup.find('h3', id='representants')
    if gestion:
        print("✅ Section gestion trouvée")
    else:
        print("❌ Section gestion non trouvée")

        # Chercher tous les h3
        all_h3 = soup.find_all('h3')
        print(f"   Tous les H3 trouvés ({len(all_h3)}):")
        for h3 in all_h3[:10]:
            print(f"     - {h3.get_text().strip()} (id={h3.get('id')})")

    # 4. Afficher la structure générale
    print("\n4️⃣ STRUCTURE GÉNÉRALE:")
    print("-" * 80)

    # Chercher tous les éléments avec classe contenant "entreprise" ou "societe"
    print("\n   Éléments avec classes intéressantes:")
    for tag in soup.find_all(class_=lambda x: x and ('entreprise' in x.lower() or 'societe' in x.lower() or 'identite' in x.lower())):
        print(f"     - {tag.name}.{tag.get('class')}: {tag.get_text(strip=True)[:50]}")

else:
    print(f"❌ Erreur HTTP {response.status_code}")

print("\n" + "=" * 80)
