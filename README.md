# LOI Bail Générateur

Générateur automatique de Lettres d'Intention (LOI) pour contrats de location commerciale.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

### Credentials INPI (optionnel)

Pour activer l'enrichissement automatique des données d'entreprises via l'API INPI:

1. Créez un fichier `.env` à la racine du projet
2. Ajoutez vos identifiants INPI:

```env
INPI_USERNAME=votre_email@example.com
INPI_PASSWORD=votre_mot_de_passe
```

> **Note**: Sans ces credentials, l'application fonctionnera normalement mais les données INPI devront être saisies manuellement.

## Utilisation

```bash
streamlit run app.py
```

L'application sera accessible à `http://localhost:8501`

## Fonctionnalités

- 📤 Upload de fichiers Excel (Fiche de décision)
- 🔄 Extraction automatique des données
- 🏢 **Enrichissement automatique via API INPI**
  - Récupération automatique des informations d'entreprise à partir du SIRET
  - Nom de la société, forme juridique, adresse de domiciliation
  - Mise en cache des résultats pour optimiser les performances
  - Rate limiting (5 requêtes/minute)
- 📄 Génération de documents Word avec template
- 🎨 Préservation du formatage (gras, couleurs, etc.)
- 🔴 Marquage des données manquantes en rouge
- 🗑️ Suppression automatique des sections optionnelles

## Fichiers requis

- `Rédaction LOI.xlsx` - Configuration et mapping des variables
- `Template LOI avec placeholder.docx` - Template Word avec placeholders

## Configuration (Enrichissement INPI)

### Développement local

Créez un fichier `.env` à la racine du projet:

```bash
INPI_USERNAME=votre_username
INPI_PASSWORD=votre_password
```

### Déploiement Streamlit Cloud

1. Allez dans les paramètres de votre app sur https://share.streamlit.io
2. Cliquez sur "Secrets" dans le menu latéral
3. Ajoutez vos credentials:

```toml
INPI_USERNAME = "votre_username"
INPI_PASSWORD = "votre_password"
```

Voir [`.streamlit/secrets.toml.example`](.streamlit/secrets.toml.example) pour un template.

## Auteur

Xavier Kain
