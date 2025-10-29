# Générateur automatique de LOI v2.0

Application web pour générer automatiquement des Lettres d'Intention (LOI) pour des baux commerciaux à partir de fichiers Excel.

## Fonctionnalités

- Upload de fichiers Excel (Fiche de décision)
- Extraction automatique des données depuis les onglets configurés
- Génération de documents DOCX avec remplacement des placeholders
- Gestion des sections optionnelles (suppression automatique si pas de données)
- Headers/Footers dynamiques selon la société bailleur
- Calculs automatiques (paliers, dates, surfaces, type de bail)
- Interface web intuitive avec Streamlit

## Installation

### Prérequis

- Python 3.9+
- pip

### Installation des dépendances

```bash
pip install -r requirements.txt
```

## Utilisation

### Lancer l'application web

```bash
streamlit run app.py
```

L'application sera accessible à l'adresse: http://localhost:8501

### Utilisation via l'interface

1. **Uploadez** votre fichier Excel (Fiche de décision)
2. **Vérifiez** les données extraites
3. **Cliquez** sur "Générer le document LOI"
4. **Téléchargez** le fichier DOCX généré

## Structure du projet

```
FA_Baux_LOI_V2a/
├── app.py                              # Interface Streamlit
├── modules/
│   ├── __init__.py
│   ├── excel_parser.py                 # Extraction des données Excel
│   └── loi_generator.py                # Génération des documents LOI
├── Exemples/                           # Fichiers Excel exemples
├── output/                             # Documents générés
├── Rédaction LOI.xlsx                  # Fichier de configuration
├── Template LOI avec placeholder.docx  # Template Word
├── requirements.txt                    # Dépendances Python
└── README.md                           # Ce fichier
```

## Configuration

### Fichier "Rédaction LOI.xlsx"

Ce fichier contient deux onglets importants:

#### Onglet "Rédaction LOI"
- **Colonne A**: Nom de la variable
- **Colonne B**: Source de la donnée (formule Excel)

Exemple:
```
Nom Preneur | =Validation!B23
Montant du loyer | ='3. Hypothèses'!E8
```

#### Onglet "Société Bailleur"
- **Colonne A**: Nom de la société
- **Colonne B**: Texte du header
- **Colonne C**: Texte du footer

### Template Word

Le template `Template LOI avec placeholder.docx` contient des placeholders entre crochets:
- `[Nom Preneur]`
- `[Montant du loyer]`
- `[Date LOI]`
- etc.

**Sections optionnelles**: Mettre le texte en **bleu** dans le template pour les sections optionnelles (paliers années 4-6, etc.)

## Calculs automatiques

L'application effectue automatiquement les calculs suivants:

### Paliers (remises)
```
Montant du palier 1 = Montant du loyer - Loyer année 1
```

### Adresse complète
```
Adresse Locaux Loués = [Numéro et rue], [Ville ou arrondissement]
```

### Type de bail
```
Si Durée Bail = 9 → "3/6/9"
Si Durée Bail = 10 → "6/9/10"
```

### Date de signature
```
Date de signature = Date d'aujourd'hui + 15 jours
```

### Surfaces
```
Surface R-1 = Surface totale - Surface RDC
```

## Gestion des placeholders

### Placeholders obligatoires (texte noir)
- Si données présentes → Remplacés normalement
- Si données manquantes → **Marqués en ROUGE** pour complétion manuelle

### Sections optionnelles (texte bleu)
- Si données présentes → Affichées en **noir**
- Si données manquantes → **Supprimées** automatiquement

## Exemples

Des fichiers Excel exemples sont disponibles dans le dossier `Exemples/`:
- 2024 05 15 - Fiche de décision - Fleux.xlsx
- 2024 07 23 - Fiche de decision BOIS COLOMBES.xlsx
- etc.

## Dépannage

### Erreur "Fichier de configuration manquant"
Vérifiez que `Rédaction LOI.xlsx` est présent à la racine du projet.

### Erreur "Template manquant"
Vérifiez que `Template LOI avec placeholder.docx` est présent à la racine du projet.

### Placeholders non remplacés
1. Vérifiez que la variable existe dans "Rédaction LOI.xlsx"
2. Vérifiez que la formule pointe vers la bonne cellule
3. Vérifiez que le nom du placeholder correspond exactement

### Headers/Footers non mis à jour
Vérifiez que la société bailleur est bien configurée dans l'onglet "Société Bailleur".

## Logs

Les logs sont affichés dans la console lors de l'exécution. Pour plus de détails, niveau de log peut être modifié dans `app.py`.

## Support

Pour toute question ou problème, consultez le fichier `GUIDE_PROJET.md` qui contient des informations détaillées sur le fonctionnement du système.

---

**Version**: 2.0
**Dernière mise à jour**: Octobre 2025
