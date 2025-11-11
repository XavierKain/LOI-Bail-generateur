"""Extrait les articles manquants du fichier original pour les ajouter au template."""

import re

def extract_article_content(text_file, article_name):
    """Extrait le contenu complet d'un article."""
    with open(text_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Trouver le début de l'article
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith(article_name):
            start_idx = i
            break

    if start_idx is None:
        return None

    # Trouver la fin (prochain article ou fin de document)
    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        if re.match(r'^ARTICLE\s+\d+', lines[i].strip()):
            end_idx = i
            break

    # Extraire le contenu
    content = ''.join(lines[start_idx:end_idx])
    return content.strip()

def extract_all_missing_articles():
    """Extrait tous les articles manquants."""
    text_file = "2024 - Bail type.txt"

    # Articles manquants selon l'analyse
    missing_articles = {
        'PRELIMINAIRE': 'ARTICLE PRELIMINAIRE',
        '9': 'ARTICLE 9',
        '10': 'ARTICLE 10',
        '11': 'ARTICLE 11',
        '12': 'ARTICLE 12',
        '13': 'ARTICLE 13',
        '14': 'ARTICLE 14',
        '15': 'ARTICLE 15',
        '16': 'ARTICLE 16',
        '17': 'ARTICLE 17',
        '18': 'ARTICLE 18',
        '20': 'ARTICLE 20',
        '21': 'ARTICLE 21',
        '23': 'ARTICLE 23',
        '24': 'ARTICLE 24',
        '25': 'ARTICLE 25',
        '27': 'ARTICLE 27',
        '28': 'ARTICLE 28',
    }

    print('=' * 80)
    print('EXTRACTION DES ARTICLES MANQUANTS')
    print('=' * 80)

    extracted = {}
    for art_num, art_name in missing_articles.items():
        print(f'\n📄 Extraction: {art_name}')
        content = extract_article_content(text_file, art_name)
        if content:
            # Compter les lignes
            lines = content.split('\n')
            print(f'   ✅ {len(lines)} lignes extraites')
            print(f'   Premier 100 caractères: {content[:100]}...')
            extracted[art_num] = content
        else:
            print(f'   ❌ Non trouvé')

    # Sauvegarder dans des fichiers séparés
    print('\n' + '=' * 80)
    print('SAUVEGARDE DES ARTICLES')
    print('=' * 80)

    for art_num, content in extracted.items():
        filename = f'article_{art_num}_extracted.txt'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'✅ {filename}')

    return extracted

if __name__ == "__main__":
    extracted = extract_all_missing_articles()

    print('\n' + '=' * 80)
    print(f'RÉSUMÉ: {len(extracted)} articles extraits')
    print('=' * 80)
