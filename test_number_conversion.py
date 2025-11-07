"""Test rapide de la conversion nombre -> mots français"""

from modules.number_to_french import number_to_french_words, format_amount_with_words

# Tests basés sur les exemples du PDF
test_cases = [
    (5000, "CINQ MILLE"),
    (40000, "QUARANTE MILLE"),
    (160000, "CENT SOIXANTE MILLE"),
    (80, "QUATRE-VINGTS"),
    (81, "QUATRE-VINGT-UN"),
    (71, "SOIXANTE-ONZE"),
    (91, "QUATRE-VINGT-ONZE"),
    (100, "CENT"),
    (200, "DEUX CENTS"),
    (201, "DEUX CENT UN"),
    (1000, "MILLE"),
    (2000, "DEUX MILLE"),
    (1000000, "UN MILLION"),
]

print("Test de conversion nombre -> mots français\n")
print("=" * 60)

all_passed = True
for number, expected in test_cases:
    result = number_to_french_words(number)
    passed = result == expected
    all_passed = all_passed and passed

    status = "✓" if passed else "✗"
    print(f"{status} {number:>10} -> {result}")
    if not passed:
        print(f"           Attendu: {expected}")

print("=" * 60)

# Test avec montants complets
print("\nTest avec montants complets:\n")
print(f"160000 € -> {format_amount_with_words(160000)}")
print(f"40000 € -> {format_amount_with_words(40000)}")
print(f"5000 € -> {format_amount_with_words(5000)}")

if all_passed:
    print("\n✓ Tous les tests sont passés!")
else:
    print("\n✗ Certains tests ont échoué")
