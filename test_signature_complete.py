"""Test complet: enrichissement INPI + génération avec signatures"""

from modules import ExcelParser, BailGenerator, BailWordGenerator
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("\n" + "=" * 80)
print("TEST COMPLET: ENRICHISSEMENT INPI + SIGNATURES")
print("=" * 80)

# 1. Charger les données
test_file = "Fiche de décision test.xlsx"
config_loi = "Rédaction LOI.xlsx"
config_bail = "Redaction BAIL.xlsx"
template_bail = "Template BAIL avec placeholder.docx"

print(f"\n1️⃣ EXTRACTION DES DONNÉES")
print("-" * 80)

parser = ExcelParser(test_file, config_loi)
variables = parser.extract_variables()
societes_info = parser.extract_societe_info()

print(f"✅ {len(variables)} variables extraites")

# Vérifier SIRET du Preneur
siret_preneur = variables.get("N° DE SIRET")
print(f"\n📋 SIRET Preneur: {siret_preneur}")

# 2. Enrichissement INPI
print(f"\n2️⃣ ENRICHISSEMENT INPI")
print("-" * 80)

if siret_preneur:
    siren = str(siret_preneur)[:9]
    print(f"SIREN extrait: {siren}")

    from modules.inpi_client import INPIClient
    inpi = INPIClient()

    try:
        enriched_data = inpi.get_company_info(siren)

        if enriched_data.get("enrichment_status") in ["success", "partial"]:
            president = enriched_data.get("PRESIDENT DE LA SOCIETE")
            print(f"✅ Président trouvé: {president}")

            # Ajouter aux variables
            variables["PRESIDENT DE LA SOCIETE"] = president
        else:
            print(f"⚠️  Enrichissement échoué: {enriched_data.get('error_message')}")
            variables["PRESIDENT DE LA SOCIETE"] = "[DONNÉE MANQUANTE]"

    except Exception as e:
        print(f"❌ Erreur INPI: {str(e)}")
        variables["PRESIDENT DE LA SOCIETE"] = "[ERREUR INPI]"
else:
    print("❌ Pas de SIRET - impossible d'enrichir")
    variables["PRESIDENT DE LA SOCIETE"] = "[PAS DE SIRET]"

# 3. Générer le BAIL
print(f"\n3️⃣ GÉNÉRATION DU BAIL")
print("-" * 80)

bail_generator = BailGenerator(config_bail, source_file=test_file)
articles_generes = bail_generator.generer_bail(variables)
donnees_complete = bail_generator.calculer_variables_derivees(variables)

print(f"✅ {len(articles_generes)} articles générés")

# Vérifier que PRESIDENT est dans les données complètes
president_final = donnees_complete.get("PRESIDENT DE LA SOCIETE")
print(f"\n📋 Président dans données complètes: {president_final}")

# 4. Générer le document Word
print(f"\n4️⃣ GÉNÉRATION DU DOCUMENT WORD")
print("-" * 80)

word_generator = BailWordGenerator(template_bail)

output_path = Path("output") / "TEST_BAIL_SIGNATURES.docx"
output_path.parent.mkdir(exist_ok=True)

word_generator.generer_document(
    articles_generes,
    donnees_complete,
    str(output_path)
)

print(f"✅ Document généré: {output_path}")

# 5. Vérifier les signatures dans le document généré
print(f"\n5️⃣ VÉRIFICATION DU TABLEAU DE SIGNATURES")
print("-" * 80)

from docx import Document
doc_generated = Document(str(output_path))

# Trouver le tableau de signatures
signature_table = doc_generated.tables[0]

print(f"\nTableau de signatures généré:")
for row_idx, row in enumerate(signature_table.rows):
    print(f"\n  Ligne {row_idx}:")
    for cell_idx, cell in enumerate(row.cells):
        text = cell.text.strip()
        marker = ""
        if "FORGEOT" in text or "PRESIDENT" in text or "[" in text:
            marker = "🎯 "
        print(f"    {marker}Col {cell_idx}: '{text}'")

# Résultat
print("\n" + "=" * 80)
print("RÉSULTAT:")
print("=" * 80)

# Vérifier que les deux noms sont présents
row1_text_0 = signature_table.rows[1].cells[0].text.strip()
row1_text_1 = signature_table.rows[1].cells[1].text.strip()

checks = []

# Check 1: Maxime FORGEOT présent
if "Maxime FORGEOT" in row1_text_0:
    checks.append("✅ Nom du Bailleur (Maxime FORGEOT) présent")
else:
    checks.append(f"❌ Nom du Bailleur manquant (trouvé: '{row1_text_0}')")

# Check 2: Président du Preneur présent et pas de placeholder rouge
if president_final and "[PRESIDENT DE LA SOCIETE]" not in row1_text_1:
    checks.append(f"✅ Nom du Preneur remplacé: '{row1_text_1}'")
elif "[PRESIDENT DE LA SOCIETE]" in row1_text_1:
    checks.append(f"⚠️  Placeholder non remplacé: {row1_text_1}")
else:
    checks.append(f"❓ Statut incertain: '{row1_text_1}'")

for check in checks:
    print(check)

print("=" * 80 + "\n")
