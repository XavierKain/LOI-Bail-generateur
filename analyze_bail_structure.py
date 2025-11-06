"""Analyse détaillée de la structure du BAIL pour comprendre la logique."""

import pandas as pd
import json

# Lire l'onglet Rédaction BAIL
df = pd.read_excel("Redaction BAIL.xlsx", sheet_name="Rédaction BAIL")

print("=" * 100)
print("ANALYSE STRUCTURE RÉDACTION BAIL")
print("=" * 100)

# Grouper par Article pour comprendre la structure
articles = {}
current_article = None

for idx, row in df.iterrows():
    # Si on a un nouvel article
    if pd.notna(row['Article']):
        current_article = row['Article']
        articles[current_article] = []

    # Ajouter la ligne à l'article courant
    if current_article:
        articles[current_article].append({
            'index': idx,
            'designation': row['Désignation'] if pd.notna(row['Désignation']) else None,
            'nom_source': row['Nom Source'] if pd.notna(row['Nom Source']) else None,
            'donnee_source': row['Donnée source'] if pd.notna(row['Donnée source']) else None,
            'condition': row['Condition'] if pd.notna(row['Condition']) else None,
            'option1': row['Entrée correspondante - Option 1'] if pd.notna(row['Entrée correspondante - Option 1']) else None,
            'condition_option2': row['Condition Option 2'] if pd.notna(row['Condition Option 2']) else None,
            'option2': row['Entrée correspondante - Option 2'] if pd.notna(row['Entrée correspondante - Option 2']) else None,
        })

# Afficher la structure par article
print(f"\n📋 Nombre d'articles: {len(articles)}\n")

for article_name, rows in articles.items():
    print("=" * 100)
    print(f"\n📌 ARTICLE: {article_name}")
    print(f"   Nombre de lignes: {len(rows)}\n")

    for i, row_data in enumerate(rows, 1):
        print(f"   {i}. Ligne {row_data['index']}")

        if row_data['designation']:
            print(f"      Désignation: {row_data['designation']}")

        if row_data['nom_source']:
            print(f"      Source: {row_data['nom_source']}")

        if row_data['donnee_source']:
            print(f"      Donnée: {row_data['donnee_source']}")

        if row_data['condition']:
            print(f"      ⚠️  Condition: {row_data['condition'][:100]}..." if len(str(row_data['condition'])) > 100 else f"      ⚠️  Condition: {row_data['condition']}")

        if row_data['option1']:
            preview = str(row_data['option1'])[:150].replace('\n', ' ')
            print(f"      ✅ Option 1: {preview}...")

        if row_data['condition_option2']:
            print(f"      ⚠️  Condition Option 2: {row_data['condition_option2'][:100]}..." if len(str(row_data['condition_option2'])) > 100 else f"      ⚠️  Condition Option 2: {row_data['condition_option2']}")

        if row_data['option2']:
            preview = str(row_data['option2'])[:150].replace('\n', ' ')
            print(f"      ✅ Option 2: {preview}...")

        print()

# Sauvegarder la structure JSON
with open('bail_structure_analyzed.json', 'w', encoding='utf-8') as f:
    json.dump(articles, f, indent=2, ensure_ascii=False, default=str)

print("\n" + "=" * 100)
print("✅ Structure sauvegardée dans bail_structure_analyzed.json")
print("=" * 100)
