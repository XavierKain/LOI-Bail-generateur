"""Debug conditions suspensives"""

from modules import ExcelParser

parser = ExcelParser('Fiche de décision test.xlsx', 'Rédaction LOI.xlsx')
variables = parser.extract_variables()

# Compter les conditions suspensives non vides
conditions = []
for i in range(1, 5):
    key = f'Condition suspensive {i}'
    value = variables.get(key)
    if value and str(value).strip() and str(value).lower() != 'none':
        conditions.append((key, value))
        print(f'{key}: {value}')

print(f'\nNombre de conditions suspensives: {len(conditions)}')

# Selon la logique utilisateur:
# - Si 1 seule → Colonne G
# - Si plusieurs → Colonne J avec liste a, b, c

if len(conditions) == 1:
    print('→ Utiliser colonne G (Option 1): texte unique')
elif len(conditions) > 1:
    print('→ Utiliser colonne J (Option 2): liste a, b, c')
else:
    print('→ Aucune condition suspensive')
