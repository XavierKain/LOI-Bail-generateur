# Notes de développement

## Résumé du projet

Application web Streamlit pour générer automatiquement des documents LOI (Lettres d'Intention) pour des baux commerciaux.

## Architecture

```
modules/
├── excel_parser.py      → Extrait les données depuis les fichiers Excel sources
└── loi_generator.py     → Génère les documents DOCX depuis le template

app.py                   → Interface web Streamlit
test_generation.py       → Script de test en ligne de commande
```

## Fonctionnalités implémentées

### ✅ Extraction des données Excel
- Lecture du fichier de configuration (`Rédaction LOI.xlsx`)
- Extraction des variables depuis les différents onglets
- Support des formules Excel (références de cellules)
- Extraction des informations des sociétés bailleures

### ✅ Calculs automatiques
- **Paliers (remises)**: `Montant du palier X = Montant du loyer - Loyer année X`
- **Adresse complète**: Combinaison rue + ville
- **Type de bail**: Déterminé selon la durée (9 ans → "3/6/9", 10 ans → "6/9/10")
- **Date de signature**: Date d'aujourd'hui + 15 jours
- **Surfaces**: Surface R-1 = Surface totale - Surface RDC

### ✅ Génération du document
- Remplacement des placeholders
- Gestion des sections optionnelles (texte bleu → suppression si pas de données)
- Marquage en rouge des placeholders obligatoires manquants
- Mise à jour des headers/footers selon la société bailleur

### ✅ Interface Streamlit
- Upload de fichiers Excel
- Visualisation des données extraites
- Génération en un clic
- Téléchargement du document généré
- Messages d'erreur détaillés

## Points d'attention

### Placeholders manquants dans les fichiers exemples

D'après le test avec `Fleux.xlsx`, ces placeholders sont souvent manquants:
- `[.]` - Destinataire/fonction (utilisé 3 fois)
- `[Statut Locaux Loués]` - Statut juridique de l'immeuble
- `[Paiement]` - Mode de paiement
- `[Durée DG]` - Durée du dépôt de garantie
- `[Durée GAPD]` - Durée GAPD
- `[Enseigne]` - Enseigne commerciale

**Solution actuelle**: Ces placeholders sont marqués en **rouge** dans le document généré pour être complétés manuellement.

### Variables avec mapping spécial

Certaines variables nécessitent un mapping de nom:
- `Statut Locaux loués` (Excel) → `Statut Locaux Loués` (Template)
- `Duré GAPD` (Excel, typo) → `Durée GAPD` (Template)

### Gestion des dates

Le système gère les dates au format DD/MM/YYYY. Les dates Excel sont automatiquement converties.

### Détection des sections optionnelles

La détection de couleur bleue fonctionne en vérifiant si:
```python
B > R and B > G  # Composante bleue dominante
```

## Améliorations possibles

### Court terme

1. **Normalisation des noms de variables**
   - Ajouter un mapping automatique pour gérer les variations de noms
   - Exemple: "Durée Franchise" vs "Duree Franchise"

2. **Validation des données**
   - Vérifier que les données critiques sont présentes avant génération
   - Afficher un avertissement dans l'interface

3. **Amélioration du formatage des nombres**
   - Formater les montants avec espaces pour les milliers
   - Exemple: 160000 → "160 000"

4. **Support des conditions suspensives**
   - Gérer dynamiquement 1 à N conditions suspensives
   - Supprimer les lignes vides si < 4 conditions

### Moyen terme

5. **Génération PDF automatique**
   - Ajouter conversion DOCX → PDF via LibreOffice
   - Option dans l'interface Streamlit

6. **Historique des documents**
   - Archiver les documents générés
   - Interface pour consulter l'historique

7. **Traitement par lot**
   - Uploader plusieurs fichiers Excel
   - Générer plusieurs LOI en une fois

8. **Export des données extraites**
   - Télécharger un CSV avec toutes les variables
   - Utile pour vérification

### Long terme

9. **Templates multiples**
   - Support de différents types de documents (Bail, Annexes, etc.)
   - Sélection du template dans l'interface

10. **Authentification et droits**
    - Système de login
    - Gestion des accès par société

11. **Notifications**
    - Email automatique avec le document généré
    - Notifications des documents en attente

12. **API REST**
    - Endpoint pour générer des documents programmatiquement
    - Intégration avec d'autres systèmes

## Bugs connus et résolutions

### ✅ RÉSOLU: RGBColor object has no attribute 'blue'

**Problème**: `RGBColor` est un objet indexable, pas un objet avec attributs.

**Solution**: Utiliser `rgb[0], rgb[1], rgb[2]` au lieu de `rgb.red, rgb.green, rgb.blue`

### En cours: Placeholders avec point "."

**Problème**: Le placeholder `[.]` est utilisé dans le template mais sa signification n'est pas claire.

**Solution possible**:
- Renommer en `[Fonction destinataire]` ou `[Contact]`
- Ou configurer une valeur par défaut

## Tests effectués

### ✅ Test 1: Génération basique
- Fichier: `2024 05 15 - Fiche de décision - Fleux.xlsx`
- Résultat: Document généré avec succès
- Placeholders manquants: 16 (marqués en rouge)

### À tester

- [ ] Test avec tous les fichiers du dossier Exemples
- [ ] Test avec données complètes (0 placeholder rouge)
- [ ] Test avec société bailleur différente de SCI FORGEOT PROPERTY
- [ ] Test des paliers années 4-6 (sections optionnelles)
- [ ] Test de la détection de couleur bleue

## Maintenance

### Ajouter une nouvelle société bailleur

Éditer `Rédaction LOI.xlsx`, onglet "Société Bailleur":

```
SCI NOUVELLE SOCIETE | NOM AFFICHÉ | Adresse ligne 1
S.C.I. au capital...
N° TVA...
```

### Ajouter un nouveau placeholder

1. Ajouter dans le template: `[Nouveau Placeholder]`
2. Ajouter dans `Rédaction LOI.xlsx`, onglet "Rédaction LOI":
   ```
   Nouveau Placeholder | ='Source'!CellRef
   ```

### Modifier les calculs

Éditer `modules/loi_generator.py`, méthode `_calculate_derived_values()`

## Dépendances

- `python-docx>=1.1.0` - Manipulation de documents Word
- `openpyxl>=3.1.2` - Lecture de fichiers Excel
- `streamlit>=1.31.0` - Interface web
- `python-dateutil>=2.8.2` - Manipulation de dates

## Performance

- Temps de chargement Excel: ~7 secondes (avec warnings openpyxl)
- Temps de génération DOCX: < 1 seconde
- Taille document généré: ~22 KB

## Sécurité

- Pas d'authentification pour le moment
- Fichiers temporaires supprimés après traitement
- Pas de persistance des données uploadées

---

**Dernière mise à jour**: 29 octobre 2025
