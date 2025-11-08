"""Test de génération des Comparutions avec Type Preneur"""

from modules.bail_generator import BailGenerator

# Données réalistes avec Type Preneur
donnees = {
    "Société Bailleur": "SCI FORGEOT PROPERTY",
    "Type Preneur": "Personne Physique",  # Pour matcher Comparution Preneur
    "Nom Preneur": "Jean DUPONT",
    "Date de prise d'effet": "01/01/2025",
}

gen = BailGenerator("Redaction BAIL.xlsx")

# Générer les articles
articles = gen.generer_bail(donnees)

print(f"Articles générés: {len(articles)}")

# Vérifier spécifiquement les Comparutions
if "Comparution Bailleur" in articles:
    print("\n✅ Comparution Bailleur trouvée!")
    print(f"Longueur: {len(articles['Comparution Bailleur'])} caractères")
else:
    print("\n❌ Comparution Bailleur MANQUANTE")

if "Comparution Preneur" in articles:
    print("✅ Comparution Preneur trouvée!")
    print(f"Longueur: {len(articles['Comparution Preneur'])} caractères")
    print(f"\nAperçu:")
    print(articles['Comparution Preneur'][:200] + "...")
else:
    print("❌ Comparution Preneur MANQUANTE")
