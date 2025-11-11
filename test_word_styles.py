"""
Test du chargement des styles depuis le document Word.
"""

from modules.word_text_loader import WordTextLoader
from docx import Document

print('=' * 80)
print('TEST DU CHARGEMENT DES STYLES DEPUIS WORD')
print('=' * 80)

# Charger le loader
print('\n1️⃣  Chargement du document Word...')
loader = WordTextLoader("Textes BAIL avec styles.docx")

print(f'\n📊 Résultats:')
print(f'   Sections chargées: {len(loader.get_section_ids())}')

# Afficher quelques exemples
print('\n2️⃣  Exemples de sections chargées:')
for i, section_id in enumerate(loader.get_section_ids()[:10], 1):
    para = loader.get_formatted_paragraph(section_id)
    if para:
        text_preview = para.text[:60].replace('\n', ' ')
        print(f'   {i}. {section_id}')
        print(f'      → {text_preview}...')
        # Vérifier si le paragraphe a des runs formatés
        has_bold = any(run.bold for run in para.runs if run.bold)
        has_italic = any(run.italic for run in para.runs if run.italic)
        if has_bold or has_italic:
            print(f'      ✨ Formatage détecté: {"gras " if has_bold else ""}{"italique" if has_italic else ""}')

# Test de copie de formatage
print('\n3️⃣  Test de copie de formatage...')
test_doc = Document()
test_para = test_doc.add_paragraph()

# Prendre la première section comme test
first_section_id = loader.get_section_ids()[0]
source_para = loader.get_formatted_paragraph(first_section_id)

if source_para:
    loader.copy_formatted_text_to_paragraph(source_para, test_para)
    print(f'   ✅ Texte copié: {test_para.text[:80]}...')
    print(f'   ✅ Runs copiés: {len(test_para.runs)}')

    # Sauvegarder pour vérification manuelle
    test_doc.save('test_formatage_output.docx')
    print(f'   ✅ Document test sauvegardé: test_formatage_output.docx')
else:
    print('   ❌ Impossible de récupérer le paragraphe source')

print('\n' + '=' * 80)
print('TEST TERMINÉ')
print('=' * 80)
