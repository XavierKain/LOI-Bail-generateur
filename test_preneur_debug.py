"""Debug script to trace Preneur formatting"""

from modules.excel_parser import ExcelParser
from modules.bail_generator import BailGenerator
from modules.bail_word_generator import BailWordGenerator

# Parse data
parser = ExcelParser("Fiche de décision test.xlsx", "Redaction BAIL.xlsx")
donnees = parser.extract()

# Generate articles
generator = BailGenerator("Redaction BAIL.xlsx", "Fiche de décision test.xlsx")
articles = generator.generer_bail(donnees)

print("="*80)
print("DEBUG PRENEUR FORMATTING")
print("="*80)
print()

# Check Preneur article
preneur_text = articles.get("Comparution Preneur", "")
print("1. Texte généré pour Comparution Preneur:")
print(f"   Longueur: {len(preneur_text)}")
print(f"   Contient <b>: {'<b>' in preneur_text}")
print(f"   Premiers 300 car:")
print(f"   {preneur_text[:300]}")
print()

# Check données complètes
print("2. Données disponibles pour Preneur:")
preneur_keys = [k for k in donnees.keys() if 'preneur' in k.lower() or 'societe' in k.lower()]
for key in preneur_keys[:10]:
    val = str(donnees[key])[:50] if donnees[key] else "None"
    print(f"   {key}: {val}")
print()

# Test parsing
print("3. Test du parsing des balises:")
segments = BailWordGenerator._parse_formatting_tags(preneur_text[:300])
for i, (text, fmt) in enumerate(segments[:5]):
    print(f"   Segment {i}: format={fmt}, text={text[:50]}...")
print()
