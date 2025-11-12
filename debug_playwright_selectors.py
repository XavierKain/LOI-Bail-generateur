"""Debug des sélecteurs Playwright sur data.inpi.fr"""

from playwright.sync_api import sync_playwright
import time

siren = "532321916"
url = f"https://data.inpi.fr/entreprises/{siren}"

print("=" * 80)
print(f"DEBUG PLAYWRIGHT SELECTORS: {url}")
print("=" * 80)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Mode visible pour debug
    page = browser.new_page()

    print("\n📡 Navigation vers la page...")
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(5000)  # Attendre 5 secondes

    print("\n✅ Page chargée\n")

    # 1. Tous les textes visibles contenant des mots clés
    print("1️⃣ RECHERCHE DE TEXTES AVEC MOTS-CLÉS")
    print("-" * 80)

    keywords = ["Forme juridique", "Capital", "Adresse", "Siège"]
    for keyword in keywords:
        try:
            elements = page.locator(f'text=/{keyword}/').all()
            print(f"\n🔍 Recherche '{keyword}': {len(elements)} résultat(s)")
            for idx, elem in enumerate(elements[:3]):  # Max 3 premiers
                try:
                    text = elem.text_content()[:100]
                    print(f"    [{idx}] {text}")
                except:
                    pass
        except Exception as e:
            print(f"    ❌ Erreur: {e}")

    # 2. Afficher la structure des DL/DT/DD (listes de définitions)
    print("\n\n2️⃣ STRUCTURE DES LISTES DE DÉFINITIONS (DL/DT/DD)")
    print("-" * 80)

    dls = page.locator('dl').all()
    print(f"Nombre de <dl>: {len(dls)}\n")

    for idx, dl in enumerate(dls[:5]):  # Max 5 premières listes
        print(f"\n--- DL #{idx} ---")
        try:
            dts = dl.locator('dt').all()
            dds = dl.locator('dd').all()

            for dt, dd in zip(dts, dds):
                label = dt.text_content().strip()
                value = dd.text_content().strip()
                print(f"  {label}: {value[:50]}")
        except Exception as e:
            print(f"  Erreur: {e}")

    # 3. Afficher tous les H2/H3
    print("\n\n3️⃣ TITRES DE SECTIONS (H2/H3)")
    print("-" * 80)

    h2s = page.locator('h2').all()
    h3s = page.locator('h3').all()

    print(f"H2: {len(h2s)}")
    for h2 in h2s:
        print(f"  - {h2.text_content().strip()}")

    print(f"\nH3: {len(h3s)}")
    for h3 in h3s:
        text = h3.text_content().strip()
        h3_id = h3.get_attribute('id')
        print(f"  - {text} (id={h3_id})")

    print("\n\n4️⃣ SCREENSHOT POUR INSPECTION")
    print("-" * 80)
    screenshot_path = "debug_inpi_screenshot.png"
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"✅ Screenshot sauvegardé: {screenshot_path}")

    print("\n\n⏸️  Pause de 10 secondes pour inspection manuelle...")
    time.sleep(10)

    browser.close()

print("\n" + "=" * 80)
