"""
Script de test pour la génération de LOI.
"""

import logging
from pathlib import Path
from modules import ExcelParser, LOIGenerator

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_generation(excel_file: str):
    """Teste la génération d'un document LOI."""
    logger.info(f"\n{'='*80}")
    logger.info(f"Test de génération avec: {excel_file}")
    logger.info(f"{'='*80}\n")

    try:
        # 1. Parser le fichier Excel
        logger.info("Étape 1: Parsing du fichier Excel...")
        parser = ExcelParser(excel_file, "Rédaction LOI.xlsx")
        variables = parser.extract_variables()
        societes_info = parser.extract_societe_info()
        output_filename = parser.get_output_filename(variables)

        logger.info(f"✓ {len(variables)} variables extraites")
        logger.info(f"✓ {len(societes_info)} sociétés bailleures configurées")
        logger.info(f"✓ Nom du fichier de sortie: {output_filename}")

        # Afficher quelques variables importantes
        logger.info("\nVariables principales:")
        important_vars = [
            "Nom Preneur", "Société Bailleur", "Date LOI",
            "Montant du loyer", "Durée Bail", "Enseigne"
        ]
        for var in important_vars:
            value = variables.get(var, "Non défini")
            logger.info(f"  - {var}: {value}")

        # 2. Générer le document
        logger.info("\nÉtape 2: Génération du document LOI...")
        generator = LOIGenerator(variables, societes_info, "Template LOI avec placeholder.docx")

        output_path = Path("output") / output_filename
        generated_path = generator.generate(str(output_path))

        logger.info(f"✓ Document généré: {generated_path}")

        # Vérifier que le fichier existe
        if Path(generated_path).exists():
            file_size = Path(generated_path).stat().st_size
            logger.info(f"✓ Taille du fichier: {file_size:,} octets")
            logger.info("\n✅ TEST RÉUSSI!\n")
            return True
        else:
            logger.error("❌ Le fichier n'a pas été créé")
            return False

    except Exception as e:
        logger.error(f"❌ ERREUR: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    # Tester avec le premier fichier exemple
    excel_files = [
        "Exemples/2024 05 15 - Fiche de décision - Fleux.xlsx",
        # "Exemples/2024 07 23 - Fiche de decision BOIS COLOMBES.xlsx",
        # "Exemples/2024 12 05 - Fiche de décision 49 Greneta.xlsx",
        # "Exemples/2025 01 30 - Fiche de décision - EXKI.xlsx",
    ]

    success_count = 0
    for excel_file in excel_files:
        if test_generation(excel_file):
            success_count += 1

    logger.info(f"\n{'='*80}")
    logger.info(f"Résumé: {success_count}/{len(excel_files)} tests réussis")
    logger.info(f"{'='*80}\n")
