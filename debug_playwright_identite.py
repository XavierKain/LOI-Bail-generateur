"""Debug de la section Identité avec Playwright"""

from playwright.sync_api import sync_playwright

siren = "532321916"
url = f"https://data.inpi.fr/entreprises/{siren}"

print("=" * 80)
print("DEBUG SECTION IDENTITÉ")
print("=" * 80)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(5000)

    # Trouver la section Identité
    print("\n📦 Recherche de la section 'Identité'...")

    # Méthode 1: Par le H3
    h3_identite = page.locator('h3:has-text("Identité")').first
    if h3_identite:
        print("✅ H3 'Identité' trouvé")

        # Trouver le conteneur parent (souvent un div)
        # Naviguer vers le parent ou le sibling
        section_parent = h3_identite.locator('xpath=following-sibling::*[1]')

        print("\n📋 Contenu de la section Identité:")
        print("-" * 80)

        # Afficher tout le texte de la section
        try:
            texte_complet = section_parent.text_content()
            print(texte_complet)
        except:
            print("❌ Impossible de récupérer le texte")

        print("\n\n🔍 Recherche des champs spécifiques...")
        print("-" * 80)

        # Essayer de trouver les éléments un par un
        champs = [
            ("Forme juridique", 'text=/Forme juridique/'),
            ("Capital", 'text=/Capital/'),
            ("Adresse", 'text=/Adresse du siège/'),
        ]

        for nom, selector in champs:
            print(f"\n🔎 Cherche '{nom}':")
            try:
                elem = page.locator(selector).first
                if elem:
                    # Essayer de trouver la valeur (peut être dans le même élément ou un suivant)
                    parent = elem.locator('xpath=..')
                    text_full = parent.text_content()
                    print(f"   Texte parent: {text_full}")

                    # Essayer aussi le sibling suivant
                    next_sibling = elem.locator('xpath=following-sibling::*[1]')
                    if next_sibling:
                        try:
                            text_sibling = next_sibling.text_content()
                            print(f"   Sibling suivant: {text_sibling}")
                        except:
                            pass
                else:
                    print(f"   ❌ Non trouvé")
            except Exception as e:
                print(f"   ❌ Erreur: {e}")

    else:
        print("❌ H3 'Identité' non trouvé")

    # Essayer une approche alternative: chercher tous les textes contenant ":"
    print("\n\n🔍 ALTERNATIVE: Tous les textes avec ':'")
    print("-" * 80)

    # Chercher dans toute la page les textes avec pattern "Label: Valeur"
    all_text = page.content()

    # Utiliser un sélecteur CSS pour trouver tous les éléments visibles
    visible_elements = page.locator('body *:visible').all()

    keywords_to_find = ["Forme juridique", "Capital", "Adresse du siège"]
    for keyword in keywords_to_find:
        print(f"\n🔎 '{keyword}':")
        for elem in visible_elements[:500]:  # Limiter à 500 premiers éléments
            try:
                text = elem.text_content().strip()
                if keyword in text and len(text) < 200:  # Pas trop long
                    print(f"   ✓ {text}")
                    break  # Prendre le premier trouvé
            except:
                pass

    browser.close()

print("\n" + "=" * 80)
