# Guide de démarrage rapide

## Installation rapide

```bash
# Installer les dépendances
pip install -r requirements.txt
```

## Lancement de l'application

### Option 1: Script automatique (recommandé)

```bash
./run.sh
```

### Option 2: Lancement manuel

```bash
streamlit run app.py
```

L'application sera accessible à l'adresse: http://localhost:8501

## Utilisation

1. **Ouvrez votre navigateur** à l'adresse http://localhost:8501
2. **Uploadez** votre fichier Excel (Fiche de décision)
3. **Vérifiez** les données extraites
4. **Cliquez** sur "Générer le document LOI"
5. **Téléchargez** le fichier DOCX généré

## Test rapide en ligne de commande

```bash
python3 test_generation.py
```

Ce script teste la génération avec un fichier exemple et crée un document dans le dossier `output/`.

## Structure des fichiers

```
FA_Baux_LOI_V2a/
├── app.py                              # Interface Streamlit (🌐 WEB)
├── test_generation.py                  # Script de test (⚙️ CLI)
├── modules/
│   ├── excel_parser.py                 # Extraction des données Excel
│   └── loi_generator.py                # Génération des documents LOI
├── Exemples/                           # Fichiers Excel exemples
├── output/                             # 📁 Documents générés (DOCX)
├── Rédaction LOI.xlsx                  # ⚙️ Configuration
└── Template LOI avec placeholder.docx  # 📄 Template Word
```

## Fichiers requis

Ces fichiers doivent être présents à la racine du projet:

- ✅ `Rédaction LOI.xlsx` - Configuration des variables et sociétés
- ✅ `Template LOI avec placeholder.docx` - Template Word avec placeholders

## Exemples de fichiers Excel

Des fichiers exemples sont disponibles dans le dossier `Exemples/`:

- `2024 05 15 - Fiche de décision - Fleux.xlsx`
- `2024 07 23 - Fiche de decision BOIS COLOMBES.xlsx`
- `2024 12 05 - Fiche de décision 49 Greneta.xlsx`
- `2025 01 30 - Fiche de décision - EXKI.xlsx`

## Troubleshooting

### Erreur "Module not found"

```bash
pip install -r requirements.txt
```

### Erreur "Fichier de configuration manquant"

Vérifiez que `Rédaction LOI.xlsx` est présent à la racine.

### Erreur "Template manquant"

Vérifiez que `Template LOI avec placeholder.docx` est présent à la racine.

### Port 8501 déjà utilisé

```bash
streamlit run app.py --server.port 8502
```

## Configuration avancée

### Ajouter une nouvelle société bailleur

Éditez le fichier `Rédaction LOI.xlsx`, onglet "Société Bailleur":

- **Colonne A**: Nom de la société
- **Colonne B**: Texte du header
- **Colonne C**: Texte du footer (peut contenir plusieurs lignes)

### Ajouter/Modifier des variables

Éditez le fichier `Rédaction LOI.xlsx`, onglet "Rédaction LOI":

- **Colonne A**: Nom de la variable (doit correspondre au placeholder dans le template)
- **Colonne B**: Formule Excel pointant vers la source de données

Exemple:
```
Nom Preneur | =Validation!B23
```

### Modifier le template

Éditez le fichier `Template LOI avec placeholder.docx`:

- Utilisez des placeholders entre crochets: `[Nom de la variable]`
- Pour les sections optionnelles, mettez le texte en **bleu**
- Les sections obligatoires restent en **noir**

## Support

Pour plus de détails, consultez:
- `README.md` - Documentation complète
- `GUIDE_PROJET.md` - Guide détaillé du projet

---

**Version**: 2.0
**Dernière mise à jour**: Octobre 2025
