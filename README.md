# LOI Bail Générateur

Générateur automatique de Lettres d'Intention (LOI) pour contrats de location commerciale.

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
streamlit run app.py
```

L'application sera accessible à `http://localhost:8501`

## Fonctionnalités

- 📤 Upload de fichiers Excel (Fiche de décision)
- 🔄 Extraction automatique des données
- 📄 Génération de documents Word avec template
- 🎨 Préservation du formatage (gras, couleurs, etc.)
- 🔴 Marquage des données manquantes en rouge
- 🗑️ Suppression automatique des sections optionnelles

## Fichiers requis

- `Rédaction LOI.xlsx` - Configuration et mapping des variables
- `Template LOI avec placeholder.docx` - Template Word avec placeholders

## Auteur

Xavier Kain
