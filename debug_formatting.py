"""
Script de débogage pour vérifier le traitement des balises de formatage.
"""

from modules.excel_parser import ExcelParser
from modules.bail_generator import BailGenerator
from modules.bail_word_generator import BailWordGenerator

print("=" * 80)
print("DÉBOGAGE DU FORMATAGE")
print("=" * 80)
print()

# Étape 1: Extraire les données
parser = ExcelParser("Fiche de décision test.xlsx", "Redaction BAIL.xlsx")
donnees_extraites = parser.extraire_donnees()

print("1. Données extraites:")
print(f"   Société Bailleur: {donnees_extraites.get('Société Bailleur')}")
print()

# Étape 2: Générer les articles
generator = BailGenerator("Redaction BAIL.xlsx", "Fiche de décision test.xlsx")
articles = generator.generer_bail(donnees_extraites)

print("2. Article Comparution Bailleur généré:")
comp_bailleur = articles.get("Comparution Bailleur", "")
print(f"   Longueur: {len(comp_bailleur)} caractères")
print(f"   Contient <b>: {'<b>' in comp_bailleur}")
print(f"   Premiers 200 caractères:")
print(f"   {comp_bailleur[:200]}")
print()

# Étape 3: Vérifier si le texte contient bien les balises
if '<b>' in comp_bailleur:
    print("✅ Les balises <b> sont présentes dans le texte généré")
    print()

    # Tester le parser
    segments = BailWordGenerator._parse_formatting_tags(comp_bailleur[:300])
    print(f"3. Parsing des balises (premiers 300 car):")
    for i, (text, formatting) in enumerate(segments):
        print(f"   Segment {i}:")
        print(f"     Texte: {text[:50]}...")
        print(f"     Format: {formatting}")
else:
    print("❌ Les balises <b> NE SONT PAS présentes dans le texte généré!")
    print()
    print("Vérification du texte brut depuis Excel...")

    import openpyxl
    wb = openpyxl.load_workbook('Redaction BAIL.xlsx')
    ws = wb['Rédaction BAIL']

    # Ligne 5 = SCI HSR 2
    texte_excel = ws.cell(row=5, column=7).value
    print(f"Texte ligne 5 colonne G:")
    print(f"  {texte_excel[:200]}")
    print(f"  Contient <b>: {'<b>' in texte_excel}")

print()
print("=" * 80)
