"""Test de génération des Comparutions"""

from modules.bail_generator import BailGenerator

# Données réalistes
donnees = {
    "Société Bailleur": "SCI FORGEOT PROPERTY",  # Doit matcher la "Donnée source"
    "Nom Preneur": "Test SAS",
    "Date de prise d'effet": "01/01/2025",
}

gen = BailGenerator("Redaction BAIL.xlsx")

# Générer les articles
articles = gen.generer_bail(donnees)

print(f"Articles générés: {len(articles)}")
print("\nListe des articles:")
for key, value in articles.items():
    preview = value[:100] + "..." if len(value) > 100 else value
    print(f"\n{key}:")
    print(f"  {preview}")

# Vérifier spécifiquement les Comparutions
if "Comparution Bailleur" in articles:
    print("\n✅ Comparution Bailleur trouvée!")
    print(f"Longueur: {len(articles['Comparution Bailleur'])} caractères")
else:
    print("\n❌ Comparution Bailleur MANQUANTE")

if "Comparution Preneur" in articles:
    print("✅ Comparution Preneur trouvée!")
    print(f"Longueur: {len(articles['Comparution Preneur'])} caractères")
else:
    print("❌ Comparution Preneur MANQUANTE")
