# GUIDE DU PROJET - Générateur automatique de LOI

## 🎯 Objectif du projet

Automatiser la génération de documents LOI (Lettres d'Intention) pour des baux commerciaux à partir de données Excel, en utilisant un template Word avec placeholders.

---

## 📁 Architecture du projet

```
FA_Baux_LOI_nospeckit/
├── Exemples/                          # Fichiers Excel sources (fiches de décision)
│   ├── 2024 05 15 - Fiche de décision - Fleux.xlsx
│   ├── 2024 07 23 - Fiche de decision BOIS COLOMBES.xlsx
│   ├── 2024 12 05 - Fiche de décision 49 Greneta.xlsx
│   └── 2025 01 30 - Fiche de décision - EXKI.xlsx
│
├── Template LOI avec placeholder.docx  # Template Word avec [Placeholders]
│
├── modules/
│   ├── excel_parser.py                # Extraction des données Excel
│   └── loi_generator_docx.py          # Génération LOI depuis template
│
└── output/                            # Fichiers DOCX générés
    ├── 2024 05 14 - LOI FLEUX.docx
    ├── 2024 07 18 - LOI La Pizza Du Dimanche Soir.docx
    ├── 2024 11 20 - LOI ZHU Xin.docx
    └── 2025 01 22 - LOI MARKI&CO.docx
```

---

## 🔄 Flux de données (Comment ça marche)

```
1. FICHIER EXCEL (Fiche de décision)
   │
   ├─ Onglet "Validation" → Données candidat, date LOI, loyers
   ├─ Onglet "Rédaction LOI" → Variables définies (40 variables)
   └─ Onglet "3. Hypothèses" → Loyers années 1-6 pour calcul paliers
   │
   ↓
2. EXTRACTION (excel_parser.py)
   │
   ├─ extract_loi_variables() → 40 variables depuis "Rédaction LOI"
   ├─ extract_validation_data() → Candidat, date LOI, société bailleur
   └─ Mapping vers placeholders du template
   │
   ↓
3. TRAITEMENT (loi_generator_docx.py)
   │
   ├─ Calcul automatique des paliers (remises)
   ├─ Formatage des dates (DD/MM/YYYY)
   ├─ Détection sections optionnelles (texte bleu)
   └─ Mise à jour headers/footers société bailleur
   │
   ↓
4. GÉNÉRATION DOCX
   │
   ├─ Remplacement des [Placeholders]
   ├─ Suppression sections optionnelles sans données
   ├─ Mise en NOIR des sections optionnelles avec données
   └─ Mise en ROUGE des placeholders obligatoires manquants
   │
   ↓
5. FICHIER FINAL
   └─ output/2024 05 14 - LOI FLEUX.docx
```

---

## 🔑 Concepts clés à comprendre

### 1. Template avec Placeholders

Le template Word contient des placeholders entre crochets qui sont remplacés par les vraies valeurs:

- `[Nom Preneur]` → "FLEUX"
- `[Montant du loyer]` → "160000"
- `[Date LOI]` → "14/05/2024"

### 2. Sections optionnelles (texte bleu)

Certaines lignes sont en **bleu** dans le template = optionnelles

- **SI données présentes** → Afficher en NOIR
- **SI pas de données** → Supprimer la ligne complètement
- Exemple: Paliers années 4-6 (souvent vides)

### 3. Placeholders obligatoires (texte noir)

- **SI données présentes** → Remplacer normalement
- **SI pas de données** → Laisser en ROUGE pour complétion manuelle
- Exemple: `[Adresse Locaux Loués]`, `[Enseigne]`

### 4. Calcul automatique des paliers

```
Loyer de base = 160 000 €
Loyer année 1 = 130 000 €
→ Palier année 1 = 160 000 - 130 000 = 30 000 €
→ Affiche: "Palier année 1 : - 30 000 € soit 130 000 € HT HC"
```

### 5. Headers & Footers dynamiques

Selon la société bailleur détectée dans Excel:

- **SCI FORGEOT PROPERTY** → Header "SCI Forgeot Property" + Footer avec adresse/RCS/TVA
- **SCI HSR 1** → Utilise le nom de la société (infos incomplètes)

---

## 🛠️ Technologies utilisées

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| Lecture Excel | `openpyxl` | Extraction données depuis .xlsx |
| Manipulation Word | `python-docx` | Lecture/modification .docx |
| Parser | `regex` (re) | Détection placeholders `[...]` |
| Détection couleur | `RGBColor` | Identifier sections optionnelles (bleu) |

---

## 📝 Fichiers clés et leur rôle

### 1. excel_parser.py (Extraction des données)

```python
class ExcelParser:
    """Parse les fichiers Excel de décision pour extraire les variables LOI."""

    def extract_loi_variables(self):
        """
        Lit lignes 3-44 de l'onglet "Rédaction LOI"
        Retourne dict: {'Nom Preneur': 'FLEUX', 'Montant du loyer': '160000', ...}
        """

    def extract_validation_data(self):
        """
        Lit l'onglet "Validation"
        Retourne: candidat, date_loi, société bailleur
        """
```

**Emplacement des données dans Excel:**
- **Onglet "Rédaction LOI"**: Lignes 3-44, Colonnes A-D
  - Colonne A: Nom de la variable
  - Colonne B: Formule pointant vers les données
- **Onglet "Validation"**: Données du candidat
  - C22: Date LOI
  - C23: Nom du candidat
  - C24: Durée ferme
  - C27: Nouveau loyer

### 2. loi_generator_docx.py (Génération du document)

```python
class LOIGeneratorDOCX:
    """Générateur de LOI basé sur template DOCX."""

    # Configuration des sociétés bailleurs
    SOCIETE_INFO = {
        'SCI FORGEOT PROPERTY': {
            'header': 'SCI Forgeot Property',
            'footer': [
                '267, boulevard Pereire – 75017 PARIS',
                'S.C.I. au capital de 310.000 € - RCS PARIS n° 804 088 094',
                'N° TVA intracommunautaire FR 06 804 088 094'
            ]
        }
    }

    def _calculate_paliers(self, variables):
        """Calcule les remises: loyer_base - loyer_année"""

    def _is_paragraph_optional(self, paragraph):
        """Détecte texte bleu (RGB: B > R et B > G)"""

    def _replace_placeholders_in_paragraph(self, paragraph, variables):
        """
        Logique principale de remplacement:
        - Optionnel + pas de données → Supprimer
        - Optionnel + données → Noir + Remplacer
        - Obligatoire + pas de données → ROUGE
        - Obligatoire + données → Remplacer
        """

    def _update_headers_footers(self, doc):
        """Applique header/footer de la société bailleur"""

    def generate(self, output_dir="output"):
        """Orchestre tout le processus de génération"""
```

---

## 📊 Mapping des variables importantes

| Placeholder Template | Variable Excel | Source Excel |
|---------------------|----------------|--------------|
| `[Nom Preneur]` | Candidat | Validation!C23 |
| `[Date LOI]` | Date LOI | Validation!C22 |
| `[Montant du loyer]` | Nouveau loyer | Validation!C27 |
| `[Société Bailleur]` | Société Bailleur | Rédaction LOI (Row 4) |
| `[Type Bail]` | Durée Bail | Validation!C24 |
| `[Durée ferme bail]` | Durée ferme | Validation!C24 |
| `[Durée Franchise]` | Durée Franchise | Rédaction LOI |
| `[Montant du palier 1]` | **Calculé** | loyer_base - loyer_année_1 |
| `[Montant du palier 2]` | **Calculé** | loyer_base - loyer_année_2 |
| `[Montant du palier 3]` | **Calculé** | loyer_base - loyer_année_3 |

---

## 🎨 Logique de formatage et couleurs

### Détection de la couleur du paragraphe

```
COULEURS:
├─ RGB Blue (0, 0, 255) → Optionnel
├─ RGB Black (0, 0, 0) → Obligatoire
└─ RGB Red (255, 0, 0) → Placeholder manquant (généré)
```

### Traitement des paragraphes

```
┌────────────────────────────────────────┐
│ Paragraphe optionnel (BLEU)           │
│ ↓                                      │
│ A-t-il des données?                   │
│ ├─ OUI → Afficher en NOIR             │
│ └─ NON → SUPPRIMER le paragraphe      │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ Paragraphe obligatoire (NOIR)          │
│ ↓                                      │
│ A-t-il des données?                   │
│ ├─ OUI → Remplacer placeholder        │
│ └─ NON → Mettre en ROUGE              │
└────────────────────────────────────────┘
```

### Exemples concrets

**Paragraphe optionnel avec données:**
- Template (BLEU): `Palier année 1 : - [Montant du palier 1] € HT ;`
- Si loyer année 1 existe → Calculer palier
- Résultat (NOIR): `Palier année 1 : - 30 000 € HT ;`

**Paragraphe optionnel sans données:**
- Template (BLEU): `Palier année 6 : - [Montant du palier 6] € HT ;`
- Si loyer année 6 n'existe pas
- Résultat: Ligne supprimée complètement

**Paragraphe obligatoire avec données:**
- Template (NOIR): `Loyer annuel : [Montant du loyer] € HT HC ;`
- Données: 160000
- Résultat (NOIR): `Loyer annuel : 160000 € HT HC ;`

**Paragraphe obligatoire sans données:**
- Template (NOIR): `Enseigne : [Enseigne]`
- Données: Non trouvées
- Résultat (ROUGE): `Enseigne : [Enseigne]`

---

## 🚀 Comment utiliser le système

### Utilisation basique

```python
# Importer le générateur
from modules.loi_generator_docx import LOIGeneratorDOCX

# Créer une instance avec le fichier Excel
generator = LOIGeneratorDOCX("Exemples/2024 05 15 - Fiche de décision - Fleux.xlsx")

# Générer le DOCX
docx_path = generator.generate()

# Résultat: output/2024 05 14 - LOI FLEUX.docx
print(f"LOI générée: {docx_path}")
```

### Générer plusieurs fichiers

```python
from modules.loi_generator_docx import LOIGeneratorDOCX
from pathlib import Path

fichiers_excel = [
    "Exemples/2024 05 15 - Fiche de décision - Fleux.xlsx",
    "Exemples/2024 07 23 - Fiche de decision BOIS COLOMBES.xlsx",
    "Exemples/2024 12 05 - Fiche de décision 49 Greneta.xlsx",
    "Exemples/2025 01 30 - Fiche de décision - EXKI.xlsx",
]

for fichier in fichiers_excel:
    generator = LOIGeneratorDOCX(fichier)
    output = generator.generate()
    print(f"✓ Généré: {Path(output).name}")
```

---

## ⚙️ Configuration et personnalisation

### Ajouter une nouvelle société bailleur

Dans `modules/loi_generator_docx.py`, modifier le dictionnaire `SOCIETE_INFO` (ligne 24):

```python
SOCIETE_INFO = {
    'SCI FORGEOT PROPERTY': {
        'header': 'SCI Forgeot Property',
        'footer': [
            '267, boulevard Pereire – 75017 PARIS',
            'S.C.I. au capital de 310.000 € - RCS PARIS n° 804 088 094',
            'N° TVA intracommunautaire FR 06 804 088 094'
        ]
    },
    'NOUVELLE SCI': {
        'header': 'Nom affiché en header',
        'footer': [
            'Adresse ligne 1',
            'RCS + Capital',
            'N° TVA'
        ]
    }
}
```

### Ajouter un nouveau placeholder

**Option 1: Ajouter dans Excel**
1. Aller dans l'onglet "Rédaction LOI"
2. Ajouter une nouvelle ligne avec:
   - Colonne A: Nom du placeholder (ex: "Nouvelle Variable")
   - Colonne B: Formule pointant vers la donnée (ex: `='Validation'!C50`)

**Option 2: Ajouter dans le mapping**
Dans `_map_variable_names()` de `loi_generator_docx.py`:

```python
mapping = {
    'Nom Excel': 'Nom Placeholder Template',
    'Nouvelle Variable Excel': 'Nouveau Placeholder',
}
```

**Option 3: Ajouter une valeur par défaut**
Dans `_add_default_values()`:

```python
defaults = {
    'Nouveau Placeholder': 'Valeur par défaut',
}
```

### Modifier le calcul des paliers

Dans `_calculate_paliers()` (ligne 90):

```python
def _calculate_paliers(self, variables: Dict[str, str]):
    """Calcule les paliers de remise automatiquement."""
    try:
        loyer_base_str = variables.get('Montant du loyer', '0')
        loyer_base = float(loyer_base_str) if loyer_base_str else 0

        for annee in range(1, 7):  # Modifier ici pour plus/moins d'années
            loyer_annee_key = f'Loyer année {annee}'
            loyer_annee_str = variables.get(loyer_annee_key, '')

            if loyer_annee_str:
                loyer_annee = float(loyer_annee_str)
                remise = loyer_base - loyer_annee

                if remise > 0:
                    # Modifier le format ici
                    variables[f'Montant du palier {annee}'] = f"{int(remise):,}".replace(',', ' ')
```

---

## 📋 Points importants à retenir

### 1. Données Excel structurées = Clé du succès

- **Onglet "Rédaction LOI"** définit les 40 variables
- **Onglet "Validation"** contient les valeurs
- Cohérence des noms de variables est critique
- Les formules Excel doivent pointer vers les bonnes cellules

### 2. Template = Modèle flexible

- Placeholders `[Nom]` remplacés automatiquement
- Sections bleues = optionnelles
- Sections noires = obligatoires
- Headers/Footers configurables par société

### 3. Calculs automatiques

- **Paliers (remises)** calculés depuis loyers
- **Dates** formatées DD/MM/YYYY automatiquement
- **Headers/footers** dynamiques selon société bailleur
- **Format nombres** avec espaces (30 000 au lieu de 30000)

### 4. Gestion des données manquantes

- **Optionnel** → Suppression silencieuse du paragraphe
- **Obligatoire** → Marquage en rouge pour complétion manuelle
- Permet de finaliser le document manuellement

### 5. Output DOCX seulement

- Permet modifications manuelles finales
- Conversion PDF manuelle via Word/Pages
- Préserve le formatage Word natif
- Conserve la possibilité d'édition

---

## 🔧 Maintenance et évolution

### Pour ajouter un nouveau placeholder

1. **Ajouter dans template Word:** `[Nouveau Placeholder]`
2. **Ajouter mapping dans code** (si besoin):
   ```python
   mapping = {
       'Variable Excel': 'Nouveau Placeholder',
   }
   ```
3. **Ou ajouter extraction dans Excel** (préféré):
   - Onglet "Rédaction LOI", nouvelle ligne
   - Colonne A: "Nouveau Placeholder"
   - Colonne B: `='Source'!CellRef`

### Pour modifier le calcul des paliers

1. Ouvrir `modules/loi_generator_docx.py`
2. Modifier la méthode `_calculate_paliers()` (ligne 90)
3. Ajuster le format d'affichage si nécessaire
4. Tester avec un fichier exemple

### Pour ajouter une société bailleur

1. Ouvrir `modules/loi_generator_docx.py`
2. Modifier le dictionnaire `SOCIETE_INFO` (ligne 24)
3. Ajouter les informations de la nouvelle société
4. Tester avec un fichier Excel de cette société

### Pour déboguer

Activer les logs détaillés:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from modules.loi_generator_docx import LOIGeneratorDOCX
generator = LOIGeneratorDOCX("fichier.xlsx")
generator.generate()
```

---

## 🐛 Problèmes courants et solutions

### Placeholder non remplacé (reste en noir)

**Problème:** `[Nom Placeholder]` apparaît tel quel dans le document
**Causes possibles:**
1. Variable non trouvée dans Excel
2. Nom du placeholder différent entre template et Excel
3. Formule Excel incorrecte

**Solution:**
1. Vérifier le nom exact du placeholder dans le template
2. Vérifier que la variable existe dans Excel "Rédaction LOI"
3. Vérifier que la formule Excel pointe vers la bonne cellule
4. Ajouter un mapping manuel si besoin

### Placeholder en rouge

**Problème:** Placeholder obligatoire marqué en rouge
**Cause:** Donnée non trouvée dans Excel

**Solution:**
1. Compléter manuellement dans le DOCX généré
2. Ou ajouter la donnée dans le fichier Excel source
3. Ou rendre le placeholder optionnel (mettre en bleu dans template)

### Section optionnelle non supprimée

**Problème:** Section bleue sans données toujours présente
**Causes possibles:**
1. Détection de couleur échouée
2. Placeholder a une valeur vide ("")

**Solution:**
1. Vérifier que le texte est bien en bleu (RGB: 0, 0, 255)
2. Vérifier que tous les runs du paragraphe sont bleus
3. Vérifier les logs pour voir si la section est détectée comme optionnelle

### Headers/Footers non mis à jour

**Problème:** Headers/footers restent ceux du template
**Causes possibles:**
1. Société Bailleur non trouvée dans Excel
2. Société non configurée dans SOCIETE_INFO

**Solution:**
1. Vérifier que "Société Bailleur" existe dans les variables Excel
2. Ajouter la société dans SOCIETE_INFO si nécessaire
3. Vérifier les logs: "Headers/Footers mis à jour pour: XXX"

### Dates au mauvais format

**Problème:** Dates affichées comme "2024-05-14 00:00:00" au lieu de "14/05/2024"
**Cause:** Format date Excel non converti

**Solution:**
1. Vérifier que le champ est dans `date_fields` de `_format_dates()`
2. Ajouter le champ si nécessaire:
   ```python
   date_fields = ['Date LOI', 'Nouvelle Date', ...]
   ```

---

## 📚 Ressources et documentation

### Fichiers de référence

- **Template:** `Template LOI avec placeholder.docx`
- **Exemple Excel:** `Exemples/2024 05 15 - Fiche de décision - Fleux.xlsx`
- **Exemple PDF:** `Exemples/2024 07 02 - LOI Fleux vDef.pdf`

### Code source

- **Parser Excel:** `modules/excel_parser.py`
- **Générateur DOCX:** `modules/loi_generator_docx.py`

### Documentation externe

- **python-docx:** https://python-docx.readthedocs.io/
- **openpyxl:** https://openpyxl.readthedocs.io/

---

## ✅ Checklist de validation

Avant de considérer une LOI comme complète:

- [ ] Tous les placeholders noirs sont remplacés (pas de `[...]` en noir)
- [ ] Tous les placeholders rouges sont complétés manuellement
- [ ] Les sections optionnelles pertinentes sont présentes
- [ ] Les paliers sont calculés correctement
- [ ] Les dates sont au format DD/MM/YYYY
- [ ] Le header affiche la bonne société bailleur
- [ ] Le footer contient les bonnes coordonnées
- [ ] Le formatage (gras, alignement) est correct
- [ ] Pas de lignes vides inappropriées
- [ ] Conversion PDF finale effectuée

---

## 🎓 Pour aller plus loin

### Améliorations possibles

1. **Génération PDF automatique**
   - Installer LibreOffice
   - Activer la conversion automatique

2. **Interface utilisateur**
   - Créer une interface Streamlit
   - Permettre upload Excel + génération en un clic

3. **Validation des données**
   - Vérifier la complétude des données Excel
   - Alerter sur les champs manquants avant génération

4. **Historique et versioning**
   - Archiver les LOI générées
   - Tracer les modifications

5. **Support multi-templates**
   - Gérer plusieurs types de documents (BAIL, etc.)
   - Sélection du template selon le type

---

**Version du guide:** 1.0
**Dernière mise à jour:** 29 octobre 2025
**Auteur:** Projet FA_Baux_LOI
