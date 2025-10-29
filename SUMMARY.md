# Projet FA_Baux_LOI_V2a - Résumé

## 🎯 Objectif

Génération automatique de Lettres d'Intention (LOI) pour des baux commerciaux à partir de fichiers Excel.

## ✨ Fonctionnalités principales

### 1. Interface web Streamlit
- Upload de fichiers Excel
- Visualisation des données extraites
- Génération en un clic
- Téléchargement direct

### 2. Extraction intelligente des données
- Lecture automatique depuis le fichier Excel source
- Configuration centralisée dans `Rédaction LOI.xlsx`
- Support des formules Excel

### 3. Calculs automatiques
- **Paliers de loyer** (remises années 1-6)
- **Adresse complète** (rue + ville)
- **Type de bail** (3/6/9 ou 6/9/10)
- **Date de signature** (aujourd'hui + 15 jours)
- **Surfaces** (calcul R-1)

### 4. Gestion intelligente des placeholders
- **Sections optionnelles** (bleu) → supprimées si pas de données
- **Sections obligatoires** (noir) → marquées en rouge si données manquantes
- Remplacement automatique dans tout le document

### 5. Headers/Footers dynamiques
- Adaptation automatique selon la société bailleur
- 10 sociétés préconfigurées

## 🚀 Démarrage rapide

### Installation
```bash
pip install -r requirements.txt
```

### Lancement
```bash
./run.sh
# ou
streamlit run app.py
```

### Accès
Ouvrir http://localhost:8501 dans votre navigateur

## 📁 Structure du projet

```
FA_Baux_LOI_V2a/
│
├── 🌐 INTERFACE
│   └── app.py                              Interface web Streamlit
│
├── ⚙️ MODULES
│   ├── modules/excel_parser.py             Extraction des données Excel
│   └── modules/loi_generator.py            Génération des documents
│
├── 📄 CONFIGURATION
│   ├── Rédaction LOI.xlsx                  Config: variables et sociétés
│   └── Template LOI avec placeholder.docx  Template Word
│
├── 📂 DONNÉES
│   ├── Exemples/                           Fichiers Excel exemples (4 fichiers)
│   └── output/                             Documents générés
│
├── 🧪 TESTS
│   └── test_generation.py                  Script de test CLI
│
├── 📚 DOCUMENTATION
│   ├── README.md                           Documentation complète
│   ├── QUICKSTART.md                       Guide de démarrage rapide
│   ├── GUIDE_PROJET.md                     Guide détaillé (ancienne version)
│   ├── NOTES.md                            Notes de développement
│   └── SUMMARY.md                          Ce fichier
│
└── 🔧 CONFIGURATION PROJET
    ├── requirements.txt                    Dépendances Python
    ├── run.sh                              Script de lancement
    └── .gitignore                          Fichiers à ignorer
```

## 📋 Fichiers de configuration

### `Rédaction LOI.xlsx`

#### Onglet "Rédaction LOI"
Définit les variables à extraire:
```
Colonne A: Nom de la variable
Colonne B: Source de la donnée (formule Excel)
```

Exemple:
```
Nom Preneur        | =Validation!B23
Montant du loyer   | ='3. Hypothèses'!E8
Date LOI           | =Validation!B22
```

#### Onglet "Société Bailleur"
Configure les headers/footers par société:
```
Colonne A: Nom de la société
Colonne B: Texte du header
Colonne C: Texte du footer
```

**10 sociétés préconfigurées:**
- SCI FORGEOT PROPERTY
- SCI FORGEOT RETAIL
- SCI HSR 1, 2, 3, 4, 5, 6
- SCI RETAIL RENNES 1, 2

### `Template LOI avec placeholder.docx`

Template Word avec:
- **30 placeholders** entre crochets: `[Nom Preneur]`, `[Montant du loyer]`, etc.
- **Sections optionnelles en bleu** (paliers années 4-6, etc.)
- **Sections obligatoires en noir**

## 🔄 Workflow

```
1. UPLOAD
   │
   ├─> Fichier Excel (Fiche de décision)
   │
   ↓
2. EXTRACTION
   │
   ├─> Lecture configuration (Rédaction LOI.xlsx)
   ├─> Extraction variables depuis onglets Excel
   ├─> Lecture infos sociétés bailleures
   │
   ↓
3. CALCULS
   │
   ├─> Paliers (loyer base - loyer année X)
   ├─> Adresse complète
   ├─> Type de bail
   ├─> Date de signature
   ├─> Surfaces
   │
   ↓
4. GÉNÉRATION
   │
   ├─> Chargement template Word
   ├─> Remplacement placeholders
   ├─> Suppression sections optionnelles sans données
   ├─> Marquage rouge sections obligatoires manquantes
   ├─> Mise à jour headers/footers
   │
   ↓
5. OUTPUT
   │
   └─> Document DOCX généré
       Format: "YYYY MM DD - LOI NomPreneur.docx"
```

## 📊 Variables extraites (40 variables)

### Informations principales
- Nom Preneur
- Société Bailleur
- Date LOI
- Enseigne
- Adresse (Ville, Rue)

### Bail
- Durée Bail
- Durée ferme Bail
- Type Bail (calculé)
- Date prise d'effet
- Date de signature (calculée)

### Surfaces
- Surface totale
- Surface RDC
- Surface R-1 (calculée)

### Loyers et paliers
- Montant du loyer
- Loyer années 1-6
- Montant paliers 1-6 (calculés)

### Conditions
- Conditions suspensives 1-4
- Durée Franchise
- Participation Travaux
- Remboursement
- Paiement

### Autres
- Statut Locaux loués
- Durée DG
- Durée GAPD

## 🎨 Gestion des couleurs

### Texte bleu = Section optionnelle
- **Avec données** → Affiché en noir
- **Sans données** → Supprimé

### Texte noir = Section obligatoire
- **Avec données** → Remplacé
- **Sans données** → Marqué en rouge

### Texte rouge = Données manquantes
- Placeholder à compléter manuellement

## ✅ Tests effectués

### Test 1: Fleux.xlsx
- ✅ Document généré: `2024 05 14 - LOI FLEUX.docx`
- ✅ 27 variables extraites
- ✅ Headers/Footers: SCI FORGEOT PROPERTY
- ⚠️ 16 placeholders manquants (marqués en rouge)

## 📈 Performance

- Chargement Excel: ~7 secondes
- Génération DOCX: < 1 seconde
- Taille fichier généré: ~22 KB

## 🔧 Technologies

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Backend | Python | 3.9+ |
| Interface | Streamlit | 1.31+ |
| Excel | openpyxl | 3.1+ |
| Word | python-docx | 1.1+ |
| Dates | python-dateutil | 2.8+ |

## 📝 Commandes utiles

```bash
# Lancer l'application web
./run.sh

# Lancer manuellement
streamlit run app.py

# Test en ligne de commande
python3 test_generation.py

# Installer les dépendances
pip install -r requirements.txt

# Changer le port
streamlit run app.py --server.port 8502
```

## 📚 Documentation

| Fichier | Description |
|---------|-------------|
| `README.md` | Documentation complète et technique |
| `QUICKSTART.md` | Guide de démarrage rapide |
| `GUIDE_PROJET.md` | Guide détaillé (ancienne architecture) |
| `NOTES.md` | Notes de développement et améliorations |
| `SUMMARY.md` | Ce résumé |

## 🐛 Problèmes connus

### Placeholders souvent manquants
- `[.]` - Fonction/destinataire
- `[Enseigne]` - Enseigne commerciale
- `[Statut Locaux Loués]` - Statut juridique
- `[Paiement]` - Mode de paiement
- `[Durée DG]` - Durée dépôt de garantie
- `[Durée GAPD]` - Durée GAPD

**Solution**: Ces placeholders sont marqués en rouge pour complétion manuelle.

## 🚀 Prochaines améliorations

### Court terme
- [ ] Validation des données avant génération
- [ ] Formatage des montants avec espaces
- [ ] Mapping automatique des variations de noms

### Moyen terme
- [ ] Génération PDF automatique
- [ ] Traitement par lot (plusieurs fichiers)
- [ ] Historique des documents

### Long terme
- [ ] Templates multiples (Bail, Annexes)
- [ ] Authentification et droits
- [ ] API REST

## 👥 Support

Pour toute question:
1. Consulter `QUICKSTART.md` pour l'utilisation
2. Consulter `README.md` pour la documentation technique
3. Consulter `NOTES.md` pour les détails de développement

---

**Version**: 2.0
**Date**: Octobre 2025
**Statut**: ✅ Fonctionnel et testé
