"""Debug matching Comparution Preneur"""

from modules.bail_generator import BailGenerator
import pandas as pd
import re

gen = BailGenerator('Redaction BAIL.xlsx', source_file='Fiche de décision test.xlsx')

# Données de test
donnees = {'Type Preneur': 'SAS'}

print('DEBUG MATCHING COMPARUTION PRENEUR')
print('=' * 80)

# Trouver les lignes candidates
lignes_candidates = []
found_start = False

for idx, row in gen.regles_df.iterrows():
    article_val = row['Article']
    designation_val = row['Désignation']

    # Nouvelle section d'article
    if article_val == 'Comparution' and designation_val == 'Comparution Preneur':
        found_start = True
        lignes_candidates.append((idx, row))
    elif found_start and article_val and article_val != 'Comparution':
        break
    elif found_start and not article_val:
        lignes_candidates.append((idx, row))

print(f'Lignes candidates: {len(lignes_candidates)}')

# Tester chaque ligne
for idx, ligne in lignes_candidates:
    donnee_source = ligne.get('Donnée source')
    nom_source = ligne.get('Nom Source')

    print(f'\nLigne {idx + 2}:')
    print(f'  Nom Source: "{nom_source}"')
    print(f'  Donnée source: "{donnee_source}"')

    # Test matching
    if pd.notna(donnee_source) and pd.notna(nom_source):
        print(f'  → Test lookup...')

        # Parser noms sources
        noms_sources = []
        pattern_match = re.match(r'^(.+?)\s+(\d+)(?:,\s*(\d+))*', str(nom_source))
        if pattern_match and ',' in str(nom_source):
            base = pattern_match.group(1).strip().rstrip('.')
            numbers = re.findall(r'\d+', str(nom_source))
            for num in numbers:
                noms_sources.append(f"{base} {num}")
        else:
            for n in str(nom_source).split('\n'):
                n = n.strip().rstrip('.')
                if n:
                    noms_sources.append(n)

        print(f'  Noms sources parsed: {noms_sources}')

        # Chercher match
        match_found = False
        for nom in noms_sources:
            valeur_actuelle = donnees.get(nom)
            print(f'    Cherche "{nom}" → {valeur_actuelle}')
            if str(valeur_actuelle) == str(donnee_source):
                print(f'      ✅ MATCH!')
                match_found = True
                break

        if match_found:
            texte = ligne.get('Entrée correspondante - Option 1')
            print(f'  → Texte retourné ({len(texte) if texte else 0} car.)')
            print(f'  Preview: {texte[:100] if texte else "None"}...')
            break
        else:
            print(f'  → Pas de match, continue...')
    else:
        print(f'  → Skipped (Donnée source={donnee_source}, Nom Source={nom_source})')
