"""
Script de test pour vérifier le parsing des balises de formatage HTML-like.

Ce script teste la méthode _parse_formatting_tags() du BailWordGenerator
pour s'assurer que toutes les balises sont correctement parsées.
"""

from modules.bail_word_generator import BailWordGenerator

def test_parsing():
    """Test le parsing des balises de formatage."""

    test_cases = [
        # (input, expected_segments)
        (
            "Texte normal",
            [("Texte normal", {})]
        ),
        (
            "La <b>Société</b> est présente",
            [
                ("La ", {}),
                ("Société", {"bold": True}),
                (" est présente", {})
            ]
        ),
        (
            "Texte <i>italique</i> et <b>gras</b>",
            [
                ("Texte ", {}),
                ("italique", {"italic": True}),
                (" et ", {}),
                ("gras", {"bold": True})
            ]
        ),
        (
            "Texte <b><i>gras et italique</i></b>",
            [
                ("Texte ", {}),
                ("gras et italique", {"bold": True, "italic": True})
            ]
        ),
        (
            "<u>Souligné</u> et normal",
            [
                ("Souligné", {"underline": True}),
                (" et normal", {})
            ]
        ),
        (
            "La <b>[Dénomination]</b> société",
            [
                ("La ", {}),
                ("[Dénomination]", {"bold": True}),
                (" société", {})
            ]
        ),
    ]

    print("=" * 80)
    print("TEST DU PARSING DES BALISES DE FORMATAGE")
    print("=" * 80)
    print()

    all_passed = True

    for i, (input_text, expected) in enumerate(test_cases, 1):
        print(f"Test {i}: {input_text}")
        print(f"  Attendu: {expected}")

        # Parser le texte
        result = BailWordGenerator._parse_formatting_tags(input_text)

        print(f"  Résultat: {result}")

        # Vérifier le résultat
        if result == expected:
            print(f"  ✅ PASSÉ")
        else:
            print(f"  ❌ ÉCHOUÉ")
            all_passed = False

        print()

    print("=" * 80)
    if all_passed:
        print("✅ TOUS LES TESTS ONT RÉUSSI")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
    print("=" * 80)

if __name__ == "__main__":
    test_parsing()
