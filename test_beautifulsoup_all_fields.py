"""Test pour voir quels champs BeautifulSoup peut récupérer depuis le HTML initial"""

import requests
from bs4 import BeautifulSoup

siren = "532321916"
url = f"https://data.inpi.fr/entreprises/{siren}"

print("=" * 80)
print("TEST: QUELS CHAMPS BEAUTIFULSOUP PEUT-IL RÉCUPÉRER ?")
print("=" * 80)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(response.content, 'html.parser')

print(f"\n📄 HTML reçu: {len(response.content)} bytes")

# 1. Chercher le H1 (nom)
print("\n1️⃣ NOM DE LA SOCIETE")
print("-" * 80)
h1 = soup.find('h1')
if h1:
    print(f"✅ Trouvé dans H1: {h1.get_text().strip()}")
else:
    print("❌ Pas de H1")

# 2. Chercher tous les textes contenant des mots-clés
print("\n2️⃣ RECHERCHE PAR MOTS-CLÉS DANS TOUT LE HTML")
print("-" * 80)

keywords = {
    "Forme juridique": "TYPE DE SOCIETE",
    "Capital": "CAPITAL SOCIAL",
    "Adresse du siège": "ADRESSE DE DOMICILIATION",
}

for keyword, field_name in keywords.items():
    # Chercher dans tout le texte de la page
    page_text = soup.get_text()
    if keyword in page_text:
        print(f"✅ '{keyword}' trouvé dans le texte de la page")

        # Essayer de trouver l'élément exact
        elements = soup.find_all(string=lambda text: text and keyword in text)
        if elements:
            print(f"   Nombre d'occurrences: {len(elements)}")
            for idx, elem in enumerate(elements[:3]):
                # Essayer de récupérer le parent et ses siblings
                parent = elem.parent
                if parent:
                    # Afficher le contenu du parent
                    parent_text = parent.get_text(strip=True)
                    if len(parent_text) < 200:
                        print(f"   [{idx}] Parent text: {parent_text}")

                    # Chercher les siblings
                    next_sibling = parent.find_next_sibling()
                    if next_sibling:
                        sibling_text = next_sibling.get_text(strip=True)
                        if sibling_text and len(sibling_text) < 200:
                            print(f"       → Next sibling: {sibling_text}")
    else:
        print(f"❌ '{keyword}' NON trouvé")

# 3. Regarder la structure du HTML autour de "Identité"
print("\n3️⃣ SECTION IDENTITÉ (structure détaillée)")
print("-" * 80)

# Chercher la section Identité
identite_headers = soup.find_all(['h2', 'h3', 'h4'], string=lambda s: s and 'Identité' in s)
if identite_headers:
    print(f"✅ Section 'Identité' trouvée ({len(identite_headers)} occurrences)")

    for idx, header in enumerate(identite_headers):
        print(f"\n  Section {idx}: {header.name} - {header.get_text().strip()}")

        # Regarder ce qui suit ce header
        next_elem = header.find_next_sibling()
        depth = 0
        while next_elem and depth < 5:
            if next_elem.name:
                text = next_elem.get_text(strip=True)
                if text and len(text) < 300:
                    print(f"    [{depth}] {next_elem.name}: {text[:100]}")
            next_elem = next_elem.find_next_sibling()
            depth += 1
else:
    print("❌ Section 'Identité' non trouvée")

# 4. Chercher tous les divs avec du contenu structuré
print("\n4️⃣ DIVS AVEC CLASSES INTÉRESSANTES")
print("-" * 80)

interesting_classes = ['row', 'col', 'form-group', 'field', 'data']
for class_name in interesting_classes:
    divs = soup.find_all('div', class_=lambda c: c and class_name in c.lower() if c else False)
    if divs:
        print(f"✅ Classe '{class_name}': {len(divs)} trouvés")
        # Afficher quelques exemples
        for div in divs[:3]:
            text = div.get_text(strip=True)
            if text and len(text) < 150 and any(kw in text for kw in ['Forme', 'Capital', 'Adresse']):
                print(f"   → {text}")

# 5. Chercher des données dans des balises script (JSON embarqué)
print("\n5️⃣ DONNÉES JSON DANS <script>")
print("-" * 80)

scripts = soup.find_all('script')
print(f"Nombre de balises <script>: {len(scripts)}")

for idx, script in enumerate(scripts):
    script_content = script.string
    if script_content and ('SIREN' in script_content or 'entreprise' in script_content or 'capital' in script_content.lower()):
        print(f"\n  Script {idx} contient des données potentielles:")
        print(f"  {script_content[:200]}...")

print("\n" + "=" * 80)
