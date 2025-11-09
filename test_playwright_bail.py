"""
Test end-to-end de génération BAIL avec Playwright
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path
import time

async def test_bail_generation():
    """Test complet de génération BAIL via l'interface Streamlit"""

    async with async_playwright() as p:
        # Lancer Streamlit en arrière-plan
        import subprocess
        streamlit_process = subprocess.Popen(
            ["streamlit", "run", "app.py", "--server.port=8502", "--server.headless=true"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Attendre que Streamlit démarre
        print("⏳ Démarrage de Streamlit...")
        time.sleep(5)

        try:
            # Lancer le navigateur
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            # Aller sur l'app
            print("🌐 Chargement de l'application...")
            await page.goto("http://localhost:8502")

            # Attendre que la page se charge
            await page.wait_for_selector("text=Générateur de Documents Immobiliers", timeout=10000)
            print("✅ Application chargée")

            # Upload du fichier test
            print("📤 Upload du fichier test...")
            file_input = await page.locator('input[type="file"]').element_handle()
            await file_input.set_input_files("Fiche de décision test.xlsx")

            # Attendre l'extraction
            await page.wait_for_selector("text=variables extraites", timeout=15000)
            print("✅ Fichier uploadé et variables extraites")

            # Screenshot 1: Données extraites
            await page.screenshot(path="test_screenshots/01_donnees_extraites.png")

            # Vérifier section INPI
            inpi_section = await page.locator("text=Données INPI").count()
            if inpi_section > 0:
                print("✅ Section INPI trouvée")
            else:
                print("⚠️ Section INPI non trouvée")

            # Cliquer sur le bouton "Voir toutes les variables extraites"
            print("📋 Affichage des variables extraites...")
            await page.locator("text=Voir toutes les variables extraites").click()
            await page.screenshot(path="test_screenshots/02_variables_completes.png")

            # Générer le BAIL
            print("🚀 Génération du BAIL...")
            await page.locator('button:has-text("Générer BAIL")').click()

            # Attendre la génération
            await page.wait_for_selector("text=Document BAIL généré avec succès", timeout=30000)
            print("✅ BAIL généré avec succès!")

            # Screenshot 2: BAIL généré
            await page.screenshot(path="test_screenshots/03_bail_genere.png")

            # Cliquer sur "Statut des placeholders"
            print("📝 Affichage du statut des placeholders...")
            await page.locator("text=Statut des placeholders du template").click()
            await page.screenshot(path="test_screenshots/04_statut_placeholders.png")

            # Vérifier les placeholders manquants
            missing_text = await page.locator("text=placeholders non remplacés").count()
            if missing_text > 0:
                print("⚠️ Certains placeholders ne sont pas remplacés")
                # Extraire le texte
                warning = await page.locator("text=placeholders non remplacés").text_content()
                print(f"   {warning}")
            else:
                success = await page.locator("text=Tous les").count()
                if success > 0:
                    msg = await page.locator("text=Tous les").text_content()
                    print(f"✅ {msg}")

            # Télécharger le BAIL
            print("📥 Téléchargement du BAIL...")
            async with page.expect_download() as download_info:
                await page.locator('button:has-text("Télécharger le document BAIL")').click()
            download = await download_info.value

            # Sauvegarder
            bail_path = Path("output") / f"TEST_{download.suggested_filename}"
            await download.save_as(bail_path)
            print(f"✅ BAIL téléchargé: {bail_path}")

            # Attendre un peu pour voir le résultat
            await page.wait_for_timeout(2000)

            # Screenshot final
            await page.screenshot(path="test_screenshots/05_final.png", full_page=True)

            print("\n" + "="*60)
            print("✅ Test terminé avec succès!")
            print("="*60)
            print(f"\n📁 Screenshots sauvegardés dans: test_screenshots/")
            print(f"📄 Document BAIL sauvegardé: {bail_path}")

            await browser.close()

        finally:
            # Arrêter Streamlit
            streamlit_process.terminate()
            streamlit_process.wait()
            print("\n🛑 Streamlit arrêté")


if __name__ == "__main__":
    # Créer le dossier pour les screenshots
    Path("test_screenshots").mkdir(exist_ok=True)

    # Lancer le test
    asyncio.run(test_bail_generation())
