"""
Test end-to-end de génération BAIL sans interface
"""

from modules import ExcelParser, BailGenerator, BailWordGenerator
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_bail_generation():
    """Test complet de génération BAIL"""

    print("\n" + "="*60)
    print("TEST DE GÉNÉRATION BAIL")
    print("="*60 + "\n")

    # 1. Charger le fichier test
    test_file = "Fiche de décision test.xlsx"
    config_loi = "Rédaction LOI.xlsx"
    config_bail = "Redaction BAIL.xlsx"
    template_bail = "Template BAIL avec placeholder.docx"

    print(f"📁 Fichier test: {test_file}")

    # 2. Extraire les données
    print("\n1️⃣ EXTRACTION DES DONNÉES")
    print("-" * 60)

    parser = ExcelParser(test_file, config_loi)
    variables = parser.extract_variables()
    societes_info = parser.extract_societe_info()

    print(f"✅ {len(variables)} variables extraites")

    # Afficher les variables importantes
    important_vars = [
        "Nom Preneur",
        "Société Bailleur",
        "Type Preneur",
        "Montant du loyer",
        "Durée Bail",
        "Date de prise d'effet",
        "Destination",
        "N° DE SIRET",
    ]

    for var in important_vars:
        value = variables.get(var, "❌ NON TROUVÉ")
        print(f"  {var}: {value}")

    # 3. Générer le BAIL
    print("\n2️⃣ GÉNÉRATION DU BAIL")
    print("-" * 60)

    bail_generator = BailGenerator(config_bail, source_file=test_file)

    # Générer les articles
    articles_generes = bail_generator.generer_bail(variables)
    print(f"✅ {len(articles_generes)} articles générés:")
    for article in articles_generes.keys():
        print(f"  - {article}")

    # Calculer variables dérivées
    donnees_complete = bail_generator.calculer_variables_derivees(variables)

    # Afficher variables dérivées
    print("\n   Variables dérivées calculées:")
    derived = {k: v for k, v in donnees_complete.items() if k not in variables}
    for var, val in sorted(derived.items()):
        print(f"  + {var}: {val}")

    # 4. Générer le document Word
    print("\n3️⃣ GÉNÉRATION DU DOCUMENT WORD")
    print("-" * 60)

    word_generator = BailWordGenerator(template_bail)

    output_path = Path("output") / "TEST_BAIL_AUTO.docx"
    output_path.parent.mkdir(exist_ok=True)

    word_generator.generer_document(
        articles_generes,
        donnees_complete,
        str(output_path)
    )

    print(f"✅ Document généré: {output_path}")

    # 5. Vérifier les placeholders
    print("\n4️⃣ VÉRIFICATION DES PLACEHOLDERS")
    print("-" * 60)

    from modules.placeholder_extractor import extract_all_placeholders, categorize_placeholders

    all_placeholders = extract_all_placeholders(template_bail)
    categorized = categorize_placeholders(all_placeholders)

    # Vérifier quels placeholders sont remplis
    missing = []
    found = []

    for placeholder in categorized["variables_normales"]:
        value = donnees_complete.get(placeholder)
        if not value or str(value).strip() == "":
            # Essayer normalisation
            wg = BailWordGenerator()
            normalized = wg._normalize_variable_name(placeholder, donnees_complete)
            value = donnees_complete.get(normalized)

        if value and str(value).strip():
            found.append(placeholder)
        else:
            missing.append(placeholder)

    print(f"✅ {len(found)} placeholders remplis")
    print(f"❌ {len(missing)} placeholders manquants:")
    for p in missing[:10]:  # Afficher les 10 premiers
        print(f"  - [{p}]")
    if len(missing) > 10:
        print(f"  ... et {len(missing) - 10} autres")

    # 6. Vérifier spécifiquement les problèmes signalés
    print("\n5️⃣ VÉRIFICATION DES PROBLÈMES SIGNALÉS")
    print("-" * 60)

    # Destination
    dest = donnees_complete.get("Destination")
    if dest:
        print(f"✅ Destination trouvée: {dest}")
    else:
        print(f"❌ Destination MANQUANTE")

    # Date + 9 ans
    date_9ans = donnees_complete.get("Date de Prise d'effet + 9 ans") or donnees_complete.get("Date de prise d'effet + 9 ans")
    if date_9ans:
        print(f"✅ Date + 9 ans trouvée: {date_9ans}")
    else:
        print(f"❌ Date + 9 ans MANQUANTE")

    # Comparutions
    comp_bailleur = articles_generes.get("Comparution Bailleur")
    comp_preneur = articles_generes.get("Comparution Preneur")

    if comp_bailleur:
        print(f"✅ Comparution Bailleur générée ({len(comp_bailleur)} car.)")
    else:
        print(f"❌ Comparution Bailleur MANQUANTE")

    if comp_preneur:
        print(f"✅ Comparution Preneur générée ({len(comp_preneur)} car.)")
    else:
        print(f"❌ Comparution Preneur MANQUANTE")

    # Résultat final
    print("\n" + "="*60)
    if not missing:
        print("✅ TEST RÉUSSI - Tous les placeholders sont remplis!")
    else:
        print(f"⚠️  TEST PARTIELLEMENT RÉUSSI - {len(missing)} placeholders manquants")
    print("="*60 + "\n")

    return len(missing) == 0


if __name__ == "__main__":
    success = test_bail_generation()
    exit(0 if success else 1)
