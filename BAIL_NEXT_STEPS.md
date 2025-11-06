# BAIL - Prochaines Étapes

## ✅ Ce qui est fait

1. **Module `bail_generator.py`** : Générateur fonctionnel
   - Calcul des variables dérivées
   - Évaluation des conditions
   - Génération de 13/16 articles
   - Tests unitaires passants

2. **Analyse des règles Excel** : Compréhension complète
   - Onglet "Rédaction BAIL" : 56 lignes de règles
   - Onglet "Liste données BAIL" : 54 variables
   - Onglet "Liste" : Nouveau, ajouté récemment

## 📋 Ce qu'il reste à faire

### 1. Créer le Template Word avec Placeholders

**Fichiers disponibles :**
- `2024 - Bail type.doc` : Template de style (SANS placeholders)
- `Exemples/*.pdf` : 2 baux clients déjà rédigés (référence)

**Action** : Créer `Template BAIL avec placeholder.docx`
- Utiliser le style du template `2024 - Bail type.doc`
- Insérer les textes depuis l'onglet "Rédaction BAIL" de l'Excel
- Ajouter les placeholders `[Variable]` aux bons endroits
- Structure :
  ```
  BAIL COMMERCIAL

  ENTRE LES SOUSSIGNES :

  [Comparution Bailleur]

  D'UNE PART,

  ET :

  [Comparution Preneur]

  D'AUTRE PART,

  IL A ETE CONVENU ET ARRETE CE QUI SUIT :

  [Article préliminaire]  (si conditions suspensives)

  ARTICLE 1 - DESIGNATION
  [Article 1]

  ARTICLE 2 - DUREE
  [Article 2]

  ... etc pour tous les articles
  ```

### 2. Adapter le Générateur

**Problèmes identifiés** :
- Articles 5.3, 7.3, 26.2 non générés (conditionnels)
- Certains placeholders manquants (montants en lettres, etc.)
- Besoin de gérer les variations de noms de variables

**Actions** :
- Tester avec données réelles depuis l'onglet "Liste"
- Déboguer les articles conditionnels manquants
- Ajouter fonction de conversion montants en lettres
- Vérifier tous les mappings de variables

### 3. Intégration Streamlit

**Actions** :
- Ajouter une section "Génération BAIL" dans l'interface
- Permettre l'upload du fichier Excel avec données
- Afficher preview du BAIL généré
- Bouton de téléchargement du document Word final

### 4. Tests avec Données Réelles

**Sources de données** :
- Onglet "Liste" du fichier Excel
- Données historiques des clients
- Comparer avec les PDFs d'exemple

## 🎯 Priorités

1. **URGENT** : Créer le template Word avec placeholders
2. **IMPORTANT** : Tester avec données réelles de l'onglet "Liste"
3. **MOYEN** : Déboguer les articles manquants
4. **BAS** : Conversion montants en lettres (peut être fait manuellement au début)

## 📝 Notes

- Le générateur utilise les textes de l'Excel, PAS du template Word
- Le template Word sert uniquement pour le style et la structure
- Les placeholders doivent matcher EXACTEMENT les noms de variables de l'Excel
- Prévoir fallback pour les données manquantes

## 🔄 Workflow de Génération

```
1. Utilisateur upload Excel avec données
2. Extraction des variables (54 au total)
3. Calcul des variables dérivées (7)
4. Pour chaque article :
   a. Évaluer conditions
   b. Sélectionner texte approprié
   c. Remplacer placeholders
5. Insérer dans template Word
6. Générer document final
7. Permettre téléchargement
```

## ✨ Améliorations Futures

- Export PDF direct
- Historique des baux générés
- Templates multiples (différents types de baux)
- Validation automatique des données
- Suggestions de valeurs manquantes
