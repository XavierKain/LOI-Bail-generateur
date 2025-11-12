"""
Test de génération du BAIL pour vérifier Article préliminaire.
"""

from modules.bail_generator import BailGenerator

print('=' * 80)
print('TEST DE GÉNÉRATION BAIL - ARTICLE PRÉLIMINAIRE')
print('=' * 80)

# Créer le générateur
generator = BailGenerator()

# Données de test minimales
donnees = {
    'Dénomination du bailleur': 'FORGEOT PROPERTY',
    'Forme juridique du bailleur': 'SCI',
    'Capital du bailleur': '310000',
    'Adresse du siège social du bailleur': '123 rue Test',
    'Code postal du siège social du bailleur': '75001',
    'Ville du siège social du bailleur': 'PARIS',
    'SIREN du bailleur': '123 456 789',
    'RCS du bailleur': 'Paris',

    'Dénomination du preneur': 'DUPONT AUTOMOBILES',
    'Forme juridique du preneur': 'SARL',
    'Capital du preneur': '50000',
    'Adresse du siège social du preneur': '456 avenue Test',
    'Code postal du siège social du preneur': '75011',
    'Ville du siège social du preneur': 'PARIS',
    'SIREN du preneur': '987 654 321',
    'RCS du preneur': 'Paris',

    # Conditions suspensives
    'Condition suspensive 1': 'Obtention du financement',
    'Condition suspensive 2': 'Autorisation de la mairie',
}

print('\n1️⃣  Génération du BAIL...')
articles = generator.generer_bail(donnees)

print(f'\n📊 Articles générés: {len(articles)}')
print(f'   Clés: {list(articles.keys())}')

print('\n2️⃣  Vérification Article préliminaire...')
if 'Article préliminaire' in articles:
    article_text = articles['Article préliminaire']
    print(f'   ✅ Article préliminaire trouvé!')
    print(f'   📄 Longueur: {len(article_text)} caractères')
    print(f'   📄 Texte (premiers 200 caractères):')
    print(f'      {article_text[:200]}...')
else:
    print(f'   ❌ Article préliminaire NON TROUVÉ!')
    print(f'   ⚠️  Clés disponibles: {list(articles.keys())}')

print('\n' + '=' * 80)
print('TEST TERMINÉ')
print('=' * 80)
