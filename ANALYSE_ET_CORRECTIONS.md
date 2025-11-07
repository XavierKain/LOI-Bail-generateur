# Analyse Complète et Plan de Correction

## État des Lieux

### 1. Ce qui fonctionnait parfaitement (Version `beca9aa`)

#### Application LOI Originale
- **Interface simple** : Upload unique → Extraction → Génération → Téléchargement
- **ExcelParser** :
  - Constructeur : `ExcelParser(excel_path, config_path)`
  - Méthodes : `extract_variables()`, `extract_societe_info()`, `get_output_filename()`
  - Lisait depuis "Rédaction LOI.xlsx" pour savoir quelles cellules extraire
  - Utilisait des formules Excel (ex: `=Validation!B23`) dans la config
- **LOIGenerator** :
  - Constructeur : `LOIGenerator(variables, societes_info, template_path)`
  - Méthode : `generate(output_path)` retourne le chemin du fichier généré
  - Enrichissement INPI automatique
  - Gestion des sections optionnelles (bleu)
  - Placeholders manquants en rouge
  - Headers/Footers personnalisés par société
- **Affichage** : Variables principales en metrics + expander avec toutes les variables

### 2. Problèmes introduits lors de l'ajout BAIL

#### Problème 1 : Changement du ExcelParser
**Avant** (fonctionnel) :
```python
parser = ExcelParser(str(temp_path), str(config_path))
variables = parser.extract_variables()
societes_info = parser.extract_societe_info()
output_filename = parser.get_output_filename(variables)
```

**Après** (cassé) :
```python
parser = ExcelParser(str(temp_path))  # Plus de config_path !
donnees = parser.extract_variables()   # Plus de extract_societe_info() !
# parser.get_output_filename() n'est plus appelé
```

**Conséquences** :
- Le parser ne sait plus quelles variables extraire (pas de config)
- Pas d'informations sur les sociétés bailleures
- Pas de génération automatique du nom de fichier
- Certains champs ne sont plus détectés

#### Problème 2 : Interface séparée LOI/BAIL
**Actuel** :
- Page d'accueil avec deux boutons
- `show_loi()` avec son propre file_uploader
- `show_bail()` avec son propre file_uploader
- Deux uploads nécessaires si on veut générer les deux documents

**Attendu** :
- Upload unique du fichier Excel
- Extraction et enrichissement INPI une seule fois
- Affichage des données extraites
- Deux boutons : "Générer LOI" et "Générer BAIL"

#### Problème 3 : BAIL Generation
**Problèmes identifiés** :
- Conversions string → float résolues ✓
- Mais le document généré ne ressemble pas aux exemples attendus
- Besoin de vérifier :
  - Structure des articles
  - Format du texte
  - Logique conditionnelle
  - Variables dérivées

### 3. Architecture des fichiers

```
FA_Baux_LOI_V2a/
├── app.py                          # Interface Streamlit (à corriger)
├── modules/
│   ├── __init__.py
│   ├── excel_parser.py             # ❌ Modifié (cassé pour LOI)
│   ├── loi_generator.py            # ✓ Intact
│   ├── inpi_client.py              # ✓ Intact
│   ├── config.py                   # ✓ Intact
│   ├── bail_generator.py           # ✓ Fixé (conversions)
│   ├── bail_word_generator.py      # ❓ À vérifier
│   └── bail_excel_parser.py        # ❓ Utilisé ?
├── Rédaction LOI.xlsx              # Config LOI
├── Redaction BAIL.xlsx             # Config BAIL
├── Template LOI avec placeholder.docx
├── Template BAIL avec placeholder.docx
└── Test_Donnees_BAIL.xlsx          # Fichier de test
```

## Plan de Correction

### Phase 1 : Restaurer la fonctionnalité LOI (PRIORITÉ ABSOLUE)

#### A. Restaurer ExcelParser original
```python
class ExcelParser:
    def __init__(self, excel_path: str, config_path: str = "Rédaction LOI.xlsx"):
        # Comme dans beca9aa

    def extract_variables(self) -> Dict[str, str]:
        # Lire depuis config_path pour savoir quoi extraire

    def extract_societe_info(self) -> Dict[str, Dict[str, str]]:
        # Lire les infos sociétés depuis config

    def get_output_filename(self, variables: Dict) -> str:
        # Générer le nom du fichier
```

#### B. Conserver BailExcelParser séparé
- Ne pas toucher à ExcelParser qui fonctionne pour LOI
- Utiliser BailExcelParser pour BAIL uniquement
- Deux parsers différents pour deux besoins différents

### Phase 2 : Refonte de l'interface

#### Interface unifiée
```python
# 1. Upload unique
uploaded_file = st.file_uploader("Fichier Excel (Fiche de décision)")

if uploaded_file:
    # 2. Extraction UNIQUE
    parser = ExcelParser(temp_path, config_loi_path)
    variables = parser.extract_variables()
    societes_info = parser.extract_societe_info()

    # 3. Affichage des données
    st.header("Données extraites")
    # ... metrics ...

    # 4. Deux boutons côte à côte
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 Générer LOI"):
            # Logique LOI

    with col2:
        if st.button("📜 Générer BAIL"):
            # Logique BAIL (avec BailGenerator)
```

### Phase 3 : Vérifier BAIL Generation

#### Checklist
- [ ] Comparer articles générés avec template
- [ ] Vérifier que toutes les conditions sont évaluées
- [ ] Vérifier les variables dérivées
- [ ] Vérifier le formatage Word
- [ ] Tester avec Test_Donnees_BAIL.xlsx

### Phase 4 : Tests complets

#### Tests LOI
- [ ] Upload fichier Excel
- [ ] Vérifier toutes les variables extraites
- [ ] Enrichissement INPI fonctionne
- [ ] Document généré correct
- [ ] Headers/footers corrects
- [ ] Sections optionnelles gérées

#### Tests BAIL
- [ ] Mêmes données que LOI
- [ ] Articles générés corrects
- [ ] Logique conditionnelle fonctionne
- [ ] Document Word conforme au template

## Solutions Proposées

### Solution 1 : Restauration complète (RECOMMANDÉ)

**Avantages** :
- LOI fonctionne à 100% comme avant
- Pas de régression
- Code testé et validé

**Actions** :
1. Restaurer `modules/excel_parser.py` depuis `beca9aa`
2. Renommer l'actuel en `modules/excel_parser_bail.py` ou supprimer si redondant
3. Garder `modules/bail_excel_parser.py` pour BAIL si nécessaire
4. Refaire `app.py` avec interface unifiée

### Solution 2 : Parser générique avec modes

**Avantages** :
- Un seul parser
- Code mutualisé

**Inconvénients** :
- Plus complexe
- Risque de casser LOI à nouveau

**Décision** : Solution 1 recommandée pour garantir zéro régression sur LOI.

## Code à implémenter

### app.py (Structure cible)

```python
import streamlit as st
from pathlib import Path
from modules import ExcelParser, LOIGenerator, BailGenerator, BailWordGenerator
import logging

# Config page
st.set_page_config(
    page_title="Générateur LOI & BAIL",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Générateur de Documents Immobiliers")
st.markdown("Génération automatique de LOI et BAIL à partir d'une Fiche de décision")

# Upload UNIQUE
uploaded_file = st.file_uploader(
    "Fichier Excel (Fiche de décision)",
    type=["xlsx", "xls"]
)

if uploaded_file:
    # Sauvegarder temporairement
    temp_path = Path("temp_uploaded.xlsx")
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Extraction avec PARSER ORIGINAL
    with st.spinner("Extraction et enrichissement INPI..."):
        parser = ExcelParser(str(temp_path), "Rédaction LOI.xlsx")
        variables = parser.extract_variables()
        societes_info = parser.extract_societe_info()
        output_filename_loi = parser.get_output_filename(variables)

    st.success(f"✅ {len(variables)} variables extraites et enrichies")

    # Affichage des données (comme original)
    st.header("Données extraites")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Nom Preneur", variables.get("Nom Preneur", "N/A"))
        st.metric("Société Bailleur", variables.get("Société Bailleur", "N/A"))
    with col2:
        st.metric("Date LOI", variables.get("Date LOI", "N/A"))
        st.metric("Montant du loyer", variables.get("Montant du loyer", "N/A"))
    with col3:
        st.metric("Durée Bail", variables.get("Durée Bail", "N/A"))
        st.metric("Enseigne", variables.get("Enseigne", "N/A"))

    with st.expander("📋 Toutes les variables"):
        display_vars = {k: v for k, v in variables.items() if not k.startswith("_")}
        for key, value in sorted(display_vars.items()):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"**{key}**")
            with col2:
                st.text(value if value else "Non défini")

    st.markdown("---")
    st.header("Génération des documents")

    # DEUX BOUTONS CÔTE À CÔTE
    col_loi, col_bail = st.columns(2)

    with col_loi:
        if st.button("📄 Générer LOI", type="primary", use_container_width=True):
            try:
                with st.spinner("Génération LOI..."):
                    generator = LOIGenerator(
                        variables,
                        societes_info,
                        "Template LOI avec placeholder.docx"
                    )
                    output_path = Path("output") / output_filename_loi
                    output_path.parent.mkdir(exist_ok=True)
                    generated = generator.generate(str(output_path))

                st.success("✅ LOI générée !")
                with open(generated, "rb") as f:
                    st.download_button(
                        "📥 Télécharger LOI",
                        data=f,
                        file_name=output_filename_loi,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            except Exception as e:
                st.error(f"❌ Erreur LOI: {e}")

    with col_bail:
        if st.button("📜 Générer BAIL", type="primary", use_container_width=True):
            try:
                with st.spinner("Génération BAIL..."):
                    # Générer nom fichier BAIL
                    nom_preneur = variables.get("Nom Preneur", "Client")
                    date_loi = variables.get("Date LOI", "")
                    output_filename_bail = f"BAIL - {nom_preneur} - {date_loi}.docx"
                    output_filename_bail = output_filename_bail.replace("/", "-")

                    # Générer BAIL
                    bail_gen = BailGenerator("Redaction BAIL.xlsx")
                    articles = bail_gen.generer_bail(variables)
                    donnees_complete = bail_gen.calculer_variables_derivees(variables)

                    word_gen = BailWordGenerator("Template BAIL avec placeholder.docx")
                    output_path = Path("output") / output_filename_bail
                    output_path.parent.mkdir(exist_ok=True)
                    word_gen.generer_document(articles, donnees_complete, str(output_path))

                st.success("✅ BAIL généré !")
                with open(output_path, "rb") as f:
                    st.download_button(
                        "📥 Télécharger BAIL",
                        data=f,
                        file_name=output_filename_bail,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            except Exception as e:
                st.error(f"❌ Erreur BAIL: {e}")

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()

else:
    st.info("👆 Uploadez un fichier Excel pour commencer")
```

## Ordre d'Exécution

1. **[URGENT]** Restaurer ExcelParser original
2. **[URGENT]** Tester que LOI fonctionne à 100%
3. Refaire app.py avec interface unifiée
4. Tester LOI dans nouvelle interface
5. Vérifier BAIL generation
6. Tests complets

## Questions à Clarifier

1. **BailExcelParser** : Est-il nécessaire ? Peut-on réutiliser les mêmes variables LOI pour BAIL ?
2. **Template BAIL** : Y a-t-il des exemples de BAIL générés corrects à comparer ?
3. **Variables BAIL** : Liste des variables spécifiques au BAIL vs LOI ?

## Risques

- ❌ **Risque élevé** : Ne pas restaurer ExcelParser original = LOI reste cassé
- ⚠️ **Risque moyen** : BAIL peut nécessiter variables additionnelles
- ✅ **Risque faible** : Interface unifiée est simple à implémenter

## Recommandations

1. **Ne JAMAIS toucher à ce qui fonctionne** : LOI était parfait, on le restaure tel quel
2. **Séparation des concerns** : ExcelParser pour LOI, BailExcelParser pour BAIL si besoin
3. **Interface unifiée** : Un upload, deux boutons, zéro ambiguïté
4. **Tests après chaque étape** : Valider LOI avant de toucher BAIL
