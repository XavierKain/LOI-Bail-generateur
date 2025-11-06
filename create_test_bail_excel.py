"""Crée un fichier Excel de test pour le générateur BAIL."""

import pandas as pd

# Données de test (similaires à test_bail_generator.py)
donnees_test = {
    "Variable": [
        "Nom Preneur",
        "Type Preneur",
        "Siret Preneur",
        "Société Bailleur",
        "Ville ou arrondissement",
        "Numéro et rue",
        "Date LOI",
        "Enseigne",
        "Statut Locaux loués",
        "Destination",
        "Durée Bail",
        "Durée ferme Bail",
        "Date prise d'effet",
        "Condition suspensive 1",
        "Condition suspensive 2",
        "Montant du loyer",
        "Loyer année 1",
        "Loyer année 2",
        "Droit d'entrée",
        "Accession",
        "Actualisation",
        "Durée Franchise",
        "Participation Travaux",
        "Remboursement",
        "Paiement",
        "Durée DG",
        "Surface totale",
        "Surface RDC",
        "Broker",
        "Honoraires Preneur",
        "Honoraires Bailleur",
        "DPE",
        "Restauration sans extraction",
    ],
    "Valeur": [
        "Jean DUPONT",
        "SAS",
        "12345678900001",
        "SCI FORGEOT PROPERTY",
        "PARIS (75017)",
        "267 boulevard Pereire",
        "01/12/2024",
        "Boutique Mode",
        "Vacant",
        "Commerce de prêt-à-porter",
        9,
        3,
        "01/01/2025",
        "Obtention du permis de construire",
        "Autorisation d'urbanisme commercial",
        120000,
        100000,
        110000,
        50000,
        "Immédiate",
        "Oui",
        6,
        30000,
        "Oui",
        "Prélèvement",
        3,
        150,
        100,
        "ABC Immobilier",
        10000,
        15000,
        "C",
        "Non",
    ]
}

# Créer le DataFrame
df = pd.DataFrame(donnees_test)

# Sauvegarder dans un fichier Excel
output_path = "Test_Donnees_BAIL.xlsx"
df.to_excel(output_path, sheet_name="Liste", index=False)

print(f"✅ Fichier de test créé: {output_path}")
print(f"   {len(donnees_test['Variable'])} variables")
