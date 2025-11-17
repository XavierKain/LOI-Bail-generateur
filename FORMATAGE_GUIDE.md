# Guide d'utilisation du formatage de texte dans BAIL

## Vue d'ensemble

Le système de génération BAIL supporte maintenant les balises de formatage HTML-like directement dans le fichier Excel "Redaction BAIL.xlsx".

## Balises supportées

| Balise | Effet | Exemple |
|--------|-------|---------|
| `<b>...</b>` | **Gras** | `La <b>Société</b>` → La **Société** |
| `<i>...</i>` | *Italique* | `<i>Article 5</i>` → *Article 5* |
| `<u>...</u>` | <u>Souligné</u> | `<u>Important</u>` → <u>Important</u> |

## Utilisation dans Excel

### 1. Formatage de texte statique

Dans votre fichier "Redaction BAIL.xlsx", ajoutez les balises directement dans le texte :

```
La <b>Société HIGH STREET RETAIL 2</b>, société civile Immobilière...
```

### 2. Formatage autour des placeholders

Vous pouvez combiner balises de formatage et placeholders `[Variable]` :

```
La <b>[Dénomination du bailleur]</b>, société [Type de société]...
```

Le nom de la société sera en gras, le type en format normal.

### 3. Formatage imbriqué

Les balises peuvent être combinées :

```
<b><i>Texte en gras et italique</i></b>
```

### 4. Formatage de parties spécifiques

```
Le <b>Bailleur</b> s'engage à <i>respecter les conditions</i> suivantes.
```

## Exemples concrets

### Exemple 1: Comparution du Bailleur

**Dans Excel** :
```
La <b>Société HIGH STREET RETAIL 2</b>, société civile Immobilière au capital de 10.000 €,
dont le siège social est à PARIS (75017), 267 boulevard Pereire...

Représentée par son <b>Président Monsieur Maxime FORGEOT</b>, dument habilité à l'effet des présentes.

<b>Ci-après dénommée : le « Bailleur »</b>
```

**Résultat dans Word** :
- "Société HIGH STREET RETAIL 2" → **en gras**
- "Président Monsieur Maxime FORGEOT" → **en gras**
- "Ci-après dénommée : le « Bailleur »" → **en gras**
- Le reste du texte → format normal (Calibri 11)

### Exemple 2: Avec placeholders dynamiques

**Dans Excel** :
```
La société <b>[Dénomination du preneur]</b>, Société [Type de Societe] au capital de [Capital social],
immatriculée au Registre du Commerce et des Sociétés de [Localite RCS] sous le numéro <b>[N° DE SIRET]</b>
```

**Résultat** :
- La valeur du placeholder `[Dénomination du preneur]` sera en gras
- `[Type de Societe]` et `[Capital social]` seront en format normal
- La valeur du `[N° DE SIRET]` sera en gras

## Règles importantes

### ✅ Ce qui fonctionne

1. **Balises dans le texte Excel** : `La <b>Société</b> est présente`
2. **Balises autour des placeholders** : `<b>[Nom Bailleur]</b>`
3. **Balises imbriquées** : `<b><i>texte</i></b>`
4. **Plusieurs balises dans un paragraphe** : `<b>Bailleur</b> et <i>Preneur</i>`

### ❌ Ce qu'il ne faut PAS faire

1. **Balises mal fermées** : `<b>texte` (manque `</b>`)
2. **Balises croisées** : `<b><i>texte</b></i>` (incorrect)
3. **Majuscules dans balises** : `<B>texte</B>` (utiliser minuscules)

## Cas d'usage recommandés

### Noms des parties
```
<b>[Dénomination du bailleur]</b>
<b>[Nom Preneur]</b>
```

### Montants importants
```
Le loyer annuel s'élève à <b>[Montant du loyer] euros</b>
```

### Termes juridiques clés
```
<i>Ci-après dénommée : le « Bailleur »</i>
```

### Titres et en-têtes (si générés dynamiquement)
```
<b><u>Article 5.3 - Destination des locaux</u></b>
```

## Dépannage

### Les balises apparaissent dans le document final

**Problème** : Vous voyez `<b>Société</b>` au lieu de **Société**

**Cause** : Balise mal formée ou typage incorrect

**Solution** :
- Vérifier que les balises sont bien `<b>` (minuscules)
- Vérifier que chaque balise ouvrante a sa balise fermante
- S'assurer que la cellule Excel contient du texte (pas une formule)

### Le formatage n'est pas appliqué

**Problème** : Le texte reste en format normal

**Cause** : Balises dans une colonne non traitée ou syntaxe incorrecte

**Solution** :
- Vérifier que vous modifiez la bonne colonne dans "Redaction BAIL.xlsx"
- Tester avec un cas simple : `<b>TEST</b>`
- Regénérer le document BAIL

### Formatage partiel

**Problème** : Seule une partie du texte est formatée

**Vérification** : C'est probablement intentionnel ! Le système formate uniquement le texte entre les balises.

## Technique

### Comment ça marche

1. **Parsing** : Le système lit le texte Excel et détecte les balises `<b>`, `<i>`, `<u>`
2. **Segmentation** : Le texte est divisé en segments avec leur formatage respectif
3. **Application** : Chaque segment est inséré dans Word avec le formatage approprié
4. **Nettoyage** : Les balises HTML sont supprimées, seul le formatage reste

### Ordre de traitement

1. Remplacement des `{{ARTICLE}}` → Parsing des balises → Application formatage
2. Remplacement des `[Variable]` → Parsing des balises → Application formatage

Les balises peuvent donc être présentes :
- Dans le texte Excel (colonnes "Texte")
- Dans les valeurs des variables (si elles contiennent des balises)
- Dans le texte généré dynamiquement par BailGenerator

## Support

Pour toute question ou problème, consultez :
- [ANALYSE_FORMATAGE_OPTIONS.md](ANALYSE_FORMATAGE_OPTIONS.md) - Analyse complète des options de formatage
- Code source : [modules/bail_word_generator.py](modules/bail_word_generator.py) (méthodes `_parse_formatting_tags` et `_apply_formatting`)

---

**Note** : Cette fonctionnalité remplace l'approche complexe WordTextLoader qui causait des bugs de duplication et de formatage. Le système actuel est plus simple, robuste et maintenable.
