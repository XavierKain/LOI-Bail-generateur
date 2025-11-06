"""Test du générateur de BAIL avec des données d'exemple."""

from modules.bail_generator import BailGenerator
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(name)s - %(message)s'
)

# Données de test
donnees_test = {
    # Informations de base
    "Nom Preneur": "Jean DUPONT",
    "Type Preneur": "SAS",
    "Siret Preneur": "12345678900001",
    "Société Bailleur": "SCI FORGEOT PROPERTY",
    "Ville ou arrondissement": "PARIS (75017)",
    "Numéro et rue": "267 boulevard Pereire",
    "Date LOI": "01/12/2024",
    "Enseigne": "Boutique Mode",
    "Statut Locaux loués": "Vacant",
    "Destination": "Commerce de prêt-à-porter",

    # Bail
    "Durée Bail": 9,
    "Durée ferme Bail": 3,
    "Date prise d'effet": "01/01/2025",

    # Conditions suspensives
    "Condition suspensive 1": "Obtention du permis de construire",
    "Condition suspensive 2": "Autorisation d'urbanisme commercial",
    "Condition suspensive 3": None,
    "Condition suspensive 4": None,

    # Loyers
    "Montant du loyer": 120000,
    "Loyer année 1": 100000,
    "Loyer année 2": 110000,
    "Loyer année 3": None,
    "Loyer année 4": None,
    "Loyer année 5": None,
    "Loyer année 6": None,

    # Financier
    "Droit d'entrée": 50000,
    "Accession": "Immédiate",
    "Actualisation": "Oui",
    "Durée Franchise": 6,
    "Participation Travaux": 30000,
    "Remboursement": "Oui",
    "Paiement": "Prélèvement",

    # Garanties
    "Durée DG": 3,
    "Duré GAPD": None,

    # Surfaces
    "Surface totale": 150,
    "Surface RDC": 100,

    # Honoraires
    "Broker": "ABC Immobilier",
    "Honoraires Preneur": 10000,
    "Honoraires Bailleur": 15000,

    # Divers
    "DPE": "C",
    "Restauration sans extraction": "Non"
}

print("=" * 80)
print("TEST DU GÉNÉRATEUR DE BAIL")
print("=" * 80)

# Initialiser le générateur
generator = BailGenerator("Redaction BAIL.xlsx")

print("\n1. Test du calcul des variables dérivées...")
print("-" * 80)
donnees_complete = generator.calculer_variables_derivees(donnees_test)

print("\nVariables dérivées:")
derivees_keys = [
    "Adresse Locaux Loués",
    "Montant du palier 1",
    "Montant du palier 2",
    "Surface R-1",
    "Type Bail",
    "Date de signature",
    "Montant du DG",
    "Période DG"
]

for key in derivees_keys:
    valeur = donnees_complete.get(key)
    print(f"  {key:30} = {valeur}")

print("\n2. Test de l'évaluateur de conditions...")
print("-" * 80)

tests_conditions = [
    ("Si [Durée Bail] > 8", True),
    ("Si [Durée Bail] = 9", True),
    ("Si [Actualisation] = 'Oui'", True),
    ("Si [Droit d'entrée] non vide", True),
    ("Si [Loyer année 1] non vide", True),
    ("Si [Loyer année 3] non vide", False),
    ("Si plusieurs conditions suspensives", True),
]

for condition, attendu in tests_conditions:
    resultat = generator.evaluer_condition(condition, donnees_complete)
    statut = "✅" if resultat == attendu else "❌"
    print(f"  {statut} {condition:50} → {resultat} (attendu: {attendu})")

print("\n3. Test de génération des articles...")
print("-" * 80)

articles = generator.generer_bail(donnees_test)

print(f"\nNombre d'articles générés: {len(articles)}")
print("\nAperçu des articles:")

for article_name, texte in articles.items():
    preview = texte[:200].replace('\n', ' ') if texte else "VIDE"
    print(f"\n  📄 {article_name}")
    print(f"     {preview}...")
    print(f"     Longueur: {len(texte)} caractères")

print("\n" + "=" * 80)
print("TEST TERMINÉ")
print("=" * 80)
