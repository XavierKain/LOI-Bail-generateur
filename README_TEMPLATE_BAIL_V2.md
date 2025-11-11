# Template BAIL V2 - Complétion Manuelle

## 📋 Objectif

Compléter le template BAIL avec tous les articles du document original, en conservant la mise en forme Word et en ajoutant :
- ✅ Table des matières dynamique
- ✅ Numérotation des pages
- ✅ Tous les articles (PRELIMINAIRE + 1-28)

## 📁 Fichiers et Dossiers

### Documents principaux

| Fichier | Description | Status |
|---------|-------------|--------|
| `2024 - Bail type.doc` | Document source original (avec mise en forme) | ✅ Source de référence |
| `Template BAIL avec placeholder.docx` | Template actuel (11 articles partiels) | ✅ Point de départ |
| `Template BAIL avec placeholder V2.docx` | **À créer** - Template complété manuellement | 🎯 **Objectif** |

### Fichiers de référence

| Fichier | Description | Utilité |
|---------|-------------|---------|
| `GUIDE_COMPLETION_TEMPLATE_BAIL.md` | **Guide principal** - Instructions détaillées | 📖 À suivre étape par étape |
| `article_*_extracted.txt` (18 fichiers) | Contenu texte des articles manquants | 📝 Référence texte (sans mise en forme) |
| `2024 - Bail type.txt` | Conversion texte du document original | 📝 Référence complète |
| `test_new_template.py` | Script de validation du template | ✅ Test automatique |

### Scripts (archivés)

Dossier : `scripts_template_generation/`

Ces scripts Python ont été utilisés pour les tentatives de génération automatique mais ne sont plus nécessaires. Conservés pour référence.

## 🚀 Procédure de Complétion

### Résumé en 5 étapes

1. **Préparer** : Dupliquer `Template BAIL avec placeholder.docx` → `Template BAIL avec placeholder V2.docx`
2. **Ajouter articles** : Copier-coller depuis `2024 - Bail type.doc` (18 articles manquants)
3. **Table des matières** : Insérer une TOC Word dynamique
4. **Numérotation** : Ajouter numéros de page au pied de page
5. **Valider** : Exécuter `python3 test_new_template.py`

### Guide détaillé

👉 **Consulter** : [`GUIDE_COMPLETION_TEMPLATE_BAIL.md`](GUIDE_COMPLETION_TEMPLATE_BAIL.md)

Le guide contient :
- ✅ Liste complète des 18 articles à ajouter
- ✅ Position exacte où insérer chaque article
- ✅ Instructions pour créer la TOC dynamique
- ✅ Instructions pour la numérotation des pages
- ✅ Checklist de validation
- ✅ Détails article par article

### Temps estimé

⏱ **2h00 - 2h45** de travail manuel

## 📊 État Actuel vs Objectif

### Template actuel

```
Articles présents: 11
- ARTICLE 1 à 8
- ARTICLE 19
- ARTICLE 22.2 (partiel)
- ARTICLE 26

Manquants: 18 articles
TOC: ❌ Absente
Numérotation: ❌ Absente
```

### Template V2 (objectif)

```
Articles présents: 29
- ARTICLE PRELIMINAIRE
- ARTICLES 1 à 28 (complets)

TOC: ✅ Dynamique Word
Numérotation: ✅ Au pied de page
Mise en forme: ✅ Conservée
```

## 🔍 Articles à Ajouter

### Articles manquants complets

| # | Titre | Position | Priorité |
|---|-------|----------|----------|
| PREL | BAIL SOUS CONDITIONS SUSPENSIVES | Avant Article 1 | ⭐⭐⭐ |
| 9 | CHARGES, TRAVAUX, IMPOTS, TAXES | Entre 8 et 19 | ⭐⭐⭐ |
| 10 | INTERETS DE RETARD | Entre 8 et 19 | ⭐⭐ |
| 11 | EXPLOITATION – LOCATION-GERANCE | Entre 8 et 19 | ⭐⭐⭐ |
| 12 | DESTRUCTION DES LOCAUX | Entre 8 et 19 | ⭐⭐ |
| 13 | RESTITUTION DES LOCAUX | Entre 8 et 19 | ⭐⭐ |
| 14 | ASSURANCES | Entre 8 et 19 | ⭐⭐⭐ |
| 15 | RESPONSABILITE ET RECOURS | Entre 8 et 19 | ⭐⭐ |
| 16 | PROCEDURE COLLECTIVE | Entre 8 et 19 | ⭐⭐ |
| 17 | CLAUSE RESOLUTOIRE | Entre 8 et 19 | ⭐⭐⭐ |
| 18 | INDEMNITE D'OCCUPATION | Entre 8 et 19 | ⭐ |
| 20 | ACTES ANTERIEURS | Entre 19 et 22 | ⭐ |
| 21 | MODIFICATIONS – TOLERANCES | Entre 19 et 22 | ⭐⭐ |
| 23 | LUTTE CONTRE LE BLANCHIMENT | Entre 22 et 26 | ⭐ |
| 24 | ELECTION DE DOMICILE | Entre 22 et 26 | ⭐ |
| 25 | EXECUTION INTEGRALE | Entre 22 et 26 | ⭐⭐ |
| 27 | SIGNATURE ELECTRONIQUE | Après 26 | ⭐ |
| 28 | ANNEXES | Après 26 | ⭐ |

**Priorités** :
- ⭐⭐⭐ = Essentiel (clauses juridiques importantes)
- ⭐⭐ = Important
- ⭐ = Standard

## ✅ Validation

### Test automatique

```bash
python3 test_new_template.py
```

**Vérifications** :
- ✅ Table des matières présente
- ✅ Numérotation des pages présente
- ✅ Tous les articles (PRELIMINAIRE + 1-28)
- ✅ Structure correcte

### Checklist manuelle

Avant de considérer le template terminé :

- [ ] Tous les 29 articles présents
- [ ] Articles dans l'ordre numérique
- [ ] Table des matières dynamique fonctionnelle
- [ ] Numéros de page au pied de page
- [ ] Mise en forme conservée (gras, styles, etc.)
- [ ] Aucun texte explicatif résiduel (ex: "PRÉVOIR si...")
- [ ] Sous-sections complètes pour chaque article
- [ ] Placeholders du template actuel préservés

## 📝 Notes Importantes

### ⚠️ Ce qu'il NE faut PAS faire

1. ❌ **Utiliser les fichiers `.txt` extraits** pour copier le contenu
   - Ils n'ont pas la mise en forme
   - Utiliser uniquement le `.doc` original

2. ❌ **Copier en texte brut** (collage spécial texte brut)
   - Toujours copier avec mise en forme (Ctrl+C / Ctrl+V normal)

3. ❌ **Inclure les textes explicatifs**
   - Supprimer : "PRÉVOIR si...", commentaires entre crochets
   - Garder uniquement le contenu légal

4. ❌ **Modifier les placeholders existants**
   - Les articles 1-8, 19, 22, 26 ont déjà des placeholders qui fonctionnent
   - Ne pas les changer

### ✅ Bonnes pratiques

1. ✅ **Travailler article par article**
   - Ne pas tout faire d'un coup
   - Sauvegarder après chaque article

2. ✅ **Vérifier la mise en forme après collage**
   - Titres en gras
   - Numérotation des sous-sections
   - Alignement correct

3. ✅ **Utiliser les styles Word**
   - Titre 2 pour les articles
   - Titre 3 pour les sous-sections
   - Corps de texte pour le contenu

4. ✅ **Mettre à jour la TOC régulièrement**
   - Après ajout de plusieurs articles
   - Clic droit → Mettre à jour les champs

## 🔗 Liens et Références

### Documentation

- [Guide de complétion détaillé](GUIDE_COMPLETION_TEMPLATE_BAIL.md)
- [Documentation générale du système BAIL](DOCUMENTATION_BAIL_SYSTEM.md)
- [Référence des placeholders](PLACEHOLDERS_BAIL_REFERENCE.md)
- [Tests et conditions logiques](TESTS_CONDITIONS_LOGIQUES_BAIL.md)

### Fichiers source

- Document original : `2024 - Bail type.doc`
- Template actuel : `Template BAIL avec placeholder.docx`
- Articles extraits (texte) : `article_*_extracted.txt`

## 📞 Support

En cas de problème :

1. **Consulter le guide** : [`GUIDE_COMPLETION_TEMPLATE_BAIL.md`](GUIDE_COMPLETION_TEMPLATE_BAIL.md)
2. **Vérifier les fichiers extraits** : `article_X_extracted.txt` pour le contenu texte
3. **Utiliser le test** : `python3 test_new_template.py` pour valider

## 🎯 Prochaines Étapes

1. Suivre le guide de complétion manuelle
2. Créer `Template BAIL avec placeholder V2.docx` complet
3. Valider avec le script de test
4. Mettre à jour `app.py` pour utiliser le nouveau template
5. Tester la génération de documents avec le nouveau template

**Bonne complétion !** 🚀
