"""Compare template BAIL with original to find missing elements."""

from docx import Document
import re

def analyze_template():
    """Analyze current template structure."""
    doc = Document('Template BAIL avec placeholder.docx')

    print('=' * 80)
    print('STRUCTURE DU TEMPLATE ACTUEL')
    print('=' * 80)

    articles = []
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if text.startswith('ARTICLE'):
            articles.append((i, text[:100]))

    print(f'\nNombre total d articles: {len(articles)}\n')
    for idx, (para_idx, art_text) in enumerate(articles, 1):
        print(f'{idx:2d}. Paragraphe {para_idx:3d}: {art_text}')

    return articles

def analyze_original():
    """Analyze original BAIL type document."""
    with open('2024 - Bail type.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print('\n' + '=' * 80)
    print('STRUCTURE DU BAIL TYPE ORIGINAL')
    print('=' * 80)

    articles = []
    for i, line in enumerate(lines):
        if line.strip().startswith('ARTICLE'):
            articles.append((i, line.strip()[:100]))

    print(f'\nNombre total d articles: {len(articles)}\n')
    for idx, (line_num, art_text) in enumerate(articles, 1):
        print(f'{idx:2d}. Ligne {line_num:4d}: {art_text}')

    return articles

def extract_article_numbers(articles_list):
    """Extract article numbers from list."""
    numbers = []
    for _, text in articles_list:
        # Try to extract number
        match = re.search(r'ARTICLE\s+(?:PRELIMINAIRE|(\d+))', text)
        if match:
            if match.group(1):
                numbers.append(int(match.group(1)))
            else:
                numbers.append(0)  # PRELIMINAIRE
    return numbers

if __name__ == "__main__":
    template_articles = analyze_template()
    original_articles = analyze_original()

    template_nums = extract_article_numbers(template_articles)
    original_nums = extract_article_numbers(original_articles)

    print('\n' + '=' * 80)
    print('COMPARAISON DES NUMEROS D ARTICLES')
    print('=' * 80)
    print(f'\nTemplate: {sorted(template_nums)}')
    print(f'Original: {sorted(original_nums)}')

    missing = set(original_nums) - set(template_nums)
    if missing:
        print(f'\n⚠️  Articles manquants dans le template: {sorted(missing)}')
    else:
        print('\n✅ Tous les articles sont présents')

    # Check for TOC
    print('\n' + '=' * 80)
    print('VERIFICATION TABLE DES MATIERES')
    print('=' * 80)

    with open('2024 - Bail type.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'TOC' in content or 'TERMINOLOGIE' in content:
            print('✅ Table des matières présente dans l original')
            # Extract TOC section
            toc_start = content.find('TOC')
            if toc_start > 0:
                toc_section = content[toc_start:toc_start+2000]
                print('\nExtrait de la table des matières:')
                print('-' * 80)
                print(toc_section[:1000])
