# Algorithme de Génération du Document BAIL

## Vue d'ensemble

Le document BAIL est composé de **16 articles** avec des règles conditionnelles complexes. Chaque article peut avoir plusieurs variantes selon les données d'entrée.

## Structure des Données

###1. Sources de données ("Liste données BAIL")
- **54 variables** au total
- Sources : Validation, Données historiques, Hypothèses, Grille ESG
- **Variables calculées** : Adresse Locaux Loués, Montants des paliers, Surface R-1, Type Bail, Date de signature, Montant du DG, Période DG

### 2. Règles de Rédaction ("Rédaction BAIL")
- **Chaque ligne** représente une variante conditionnelle
- **Colonnes clés** :
  - `Article` : Numéro de l'article
  - `Désignation` : Titre/description
  - `Nom Source` : Variable(s) utilisée(s)
  - `Donnée source` : Valeur de référence pour la condition
  - `Condition` : Condition pour sélectionner l'option 1
  - `Entrée correspondante - Option 1` : Texte à insérer si condition vraie
  - `Condition Option 2` : Condition alternative
  - `Entrée correspondante - Option 2` : Texte alternatif

## Structure des Articles

### Article: **Comparution** (5 variantes)
**Logique** :
1. **Comparution Bailleur** : Hardcodé selon `Société Bailleur`
   - SCI FORGEOT PROPERTY → Texte spécifique
   - SCI FORGEOT RETAIL → Texte spécifique
   - SCI HSR 1, 2, 5, 6 → Textes spécifiques
   - SARL HSR 3 → Texte spécifique
   - SAS HSR 4 → Texte spécifique

2. **Comparution Preneur** : Dépend de `Type Preneur`
   - Personne physique → Template avec placeholders
   - SAS → Récupérer infos depuis SIRET (nom, capital, siège, RCS, représentant)
   - SARL → Idem SAS
   - EURL → Idem SAS
   - Société en formation → Template spécifique

### Article: **Article préliminaire** (Conditions suspensives)
**Logique** :
- Si 1 condition suspensive → "CONDITION SUSPENSIVE" (singulier)
- Si plusieurs conditions → "CONDITIONS SUSPENSIVES" (pluriel)
- Lister toutes les conditions suspensives 1, 2, 3, 4 (non vides)

### Article: **Article 1** (Désignation)
**Données** : Surface totale
**Logique** : Utiliser le template avec `[Surface totale]`

### Article: **Article 2** (Durée)
**Condition** : Si `Durée du Bail` > 9
**Données** : Durée ferme Bail
**Logique** : Template avec durée ferme pour baux > 9 ans

### Article: **Article 3** (Destination)
**Logique** :
1. Base : Template avec `[Destination]` et `[Enseigne]`
2. Si `Restauration sans extraction` = "Oui" → Ajouter clause spécifique

### Article: **Article 5.3** (Entretien et réparation - Accession)
**Condition** : Selon `Option Accession`
- "Immédiate" → Clause accession immédiate
- "Fin de Bail" → Clause accession fin de bail

### Article: **Article 7.1** (Montant du loyer)
**Données** : Montant du loyer
**Logique** : Template simple avec montant

### Article: **Article 7.2** (Actualisation et indexation)
**Condition** : Selon `Actualisation`
- "Oui" → Clause avec actualisation + indexation
- "Non" → Clause indexation uniquement

### Article: **Article 7.3** (Paiement des loyers)
**Condition** : Selon `Paiement`
- "Prélèvement" → Clause prélèvement automatique
- "Virement" → Clause virement bancaire

### Article: **Article 7.6** (Droit d'entrée)
**Condition** : Si `Droit d'entrée` non vide
**Logique** : Insérer clause avec montant du droit d'entrée

### Article: **Article 8** (Garanties)
**Logique** :
1. Si `Durée DG` non vide → Clause Dépôt de Garantie
2. Si `Durée GAPD` non vide → Clause Garantie à Première Demande

### Article: **Article 19** (Frais et honoraires)
**Condition** : Si `Honoraires Preneur` non vide
**Données** : Broker, Honoraires Preneur, Honoraires Bailleur
**Logique** : Template avec répartition des honoraires

### Article: **Article 22.2** (Validité DPE)
**Condition** : Si `DPE` non vide
**Logique** : Clause reconnaissance réception DPE

### Article: **Article 26** (Dispositions particulières)
**Données** : Nom Preneur
**Logique** : Clause standard personnalisée

### Article: **Article 26.1** (Paliers de loyer)
**Condition** : Si `Loyer année 1` non vide (= présence de paliers)
**Logique** :
- Lister tous les paliers (années 1 à 6 non vides)
- Calculer montants : `Montant du palier X = Montant du loyer - Loyer année X`
- Durée ferme Bail pour la clause finale

### Article: **Article 26.2** (Franchise de loyer)
**Condition** : Si `Durée Franchise` non vide
**Logique** : Template avec durée de franchise

---

## Algorithme de Génération

```python
def generer_bail(donnees):
    """
    Génère le document BAIL à partir des données d'entrée.

    Args:
        donnees: Dict avec toutes les variables (54 au total)

    Returns:
        String ou Document Word avec le contenu généré
    """

    # 1. Calculer les variables dérivées
    donnees_complete = calculer_variables_derivees(donnees)

    # 2. Pour chaque article
    articles_generes = {}

    for article in ARTICLES:
        # 3. Évaluer les conditions pour trouver la bonne variante
        texte = evaluer_conditions_article(article, donnees_complete)

        # 4. Remplacer les placeholders
        texte_final = remplacer_placeholders(texte, donnees_complete)

        articles_generes[article.nom] = texte_final

    # 5. Assembler le document final
    document = assembler_document(articles_generes)

    return document


def calculer_variables_derivees(donnees):
    """Calcule les variables dérivées."""
    derivees = donnees.copy()

    # Adresse Locaux Loués
    derivees["Adresse Locaux Loués"] = f"{donnees['Ville ou arrondissement']}, {donnees['Numéro et rue']}"

    # Montants des paliers
    for i in range(1, 7):
        key = f"Loyer année {i}"
        if donnees.get(key):
            derivees[f"Montant du palier {i}"] = donnees["Montant du loyer"] - donnees[key]

    # Surface R-1
    derivees["Surface R-1"] = donnees["Surface totale"] - donnees["Surface RDC"]

    # Type Bail
    if donnees["Durée Bail"] == 9:
        derivees["Type Bail"] = "3/6/9"
    elif donnees["Durée Bail"] == 10:
        derivees["Type Bail"] = "6/9/10"

    # Date de signature
    from datetime import datetime, timedelta
    derivees["Date de signature"] = (datetime.now() + timedelta(days=15)).strftime("%d/%m/%Y")

    # Montant du DG
    derivees["Montant du DG"] = (donnees["Montant du loyer"] / 12) * donnees.get("Durée DG", 0)

    # Période DG
    periode_map = {3: "quart", 4: "tiers", 6: "moitier"}
    derivees["Période DG"] = periode_map.get(donnees.get("Durée DG"))

    return derivees


def evaluer_conditions_article(article, donnees):
    """Évalue les conditions d'un article pour trouver la bonne variante."""

    # Charger les règles depuis l'Excel
    regles = charger_regles_article(article)

    for regle in regles:
        # Condition principale (Option 1)
        if evaluer_condition(regle.condition, donnees):
            return regle.option1

        # Condition alternative (Option 2)
        if regle.condition_option2 and evaluer_condition(regle.condition_option2, donnees):
            return regle.option2

    # Pas de condition → utiliser option 1 par défaut
    return regles[0].option1 if regles else ""


def evaluer_condition(condition_str, donnees):
    """
    Évalue une condition textuelle.

    Exemples:
    - "Si [Durée Bail] > 9" → donnees["Durée Bail"] > 9
    - "Si [Actualisation] = 'Oui'" → donnees["Actualisation"] == "Oui"
    - "Si [Loyer année 1] non vide" → bool(donnees.get("Loyer année 1"))
    - "Si plusieurs conditions suspensives" → compter conditions non vides > 1
    """

    if not condition_str:
        return False

    # Parser et évaluer la condition
    # ... logique de parsing des conditions

    return True  # ou False selon évaluation
```

## Variables Calculées à Implémenter

1. **Adresse Locaux Loués** = `[Ville ou arrondissement], [Numéro et rue]`
2. **Montant du palier X** = `[Montant du loyer] - [Loyer année X]`
3. **Surface R-1** = `[Surface totale] - [Surface RDC]`
4. **Type Bail** :
   - Si Durée Bail = 9 → "3/6/9"
   - Si Durée Bail = 10 → "6/9/10"
5. **Date de signature** = Date d'aujourd'hui + 15 jours
6. **Montant du DG** = `[Montant du loyer] / 12 * [Durée DG]`
7. **Période DG** :
   - Si Durée DG = 3 → "quart"
   - Si Durée DG = 4 → "tiers"
   - Si Durée DG = 6 → "moitier"

## Complexité des Conditions

### Types de conditions rencontrées :
1. **Égalité** : `Si [Variable] = "valeur"`
2. **Non vide** : `Si [Variable] non vide`
3. **Comparaison** : `Si [Variable] > nombre`
4. **Comptage** : `Si plusieurs conditions suspensives` (compter > 1)
5. **Matching** : Selon `Société Bailleur` → lookup table

## Prochaines Étapes

1. ✅ **Analyse complète** de la structure Excel
2. ⏭️ **Parser les conditions** depuis l'Excel
3. ⏭️ **Créer module `bail_generator.py`** similaire à `loi_generator.py`
4. ⏭️ **Implémenter l'évaluateur de conditions**
5. ⏭️ **Tester avec données réelles**
6. ⏭️ **Intégrer dans l'interface Streamlit**
