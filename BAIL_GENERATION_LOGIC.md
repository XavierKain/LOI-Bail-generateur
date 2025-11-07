# Schéma de Génération BAIL - Logique Conditionnelle

## Vue d'ensemble du processus

```
┌─────────────────────────────────────────────────────────────┐
│  FICHIER EXCEL (Fiche de décision)                          │
│  - Données du Preneur                                        │
│  - Données du Bailleur                                       │
│  - Données du Bail (loyer, durée, surface, etc.)           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  ExcelParser                                                 │
│  - Extraction des variables depuis "Rédaction LOI.xlsx"     │
│  - Enrichissement INPI (facultatif)                         │
│  - output: Dict[str, str] variables                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  BailGenerator                                               │
│  1. Calcul des variables dérivées                           │
│  2. Génération conditionnelle des 16+ articles               │
│  - output: Dict[str, str] articles_generes                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  BailWordGenerator                                           │
│  1. Remplacement des placeholders {{ARTICLE}}               │
│  2. Remplacement des placeholders [Variable]                │
│     - Conversion "en lettres" pour montants                 │
│  - output: Document Word (.docx)                            │
└─────────────────────────────────────────────────────────────┘
```

## 1. Variables Dérivées (Calculées Automatiquement)

### 1.1 Surface R-1
```
IF Surface totale && Surface RDC:
    Surface R-1 = Surface totale - Surface RDC
ELSE:
    Surface R-1 = ""
```

### 1.2 Type de Bail
```
IF Durée Bail >= 9:
    Type Bail = "ferme"
ELSE:
    Type Bail = "3-6-9"
```

### 1.3 Montants de Paliers (Années 1, 2, 3)
```
IF Palier année 1:
    Montant palier année 1 = Montant loyer * (Palier année 1 / 100)
ELSE:
    Montant palier année 1 = ""

IF Palier année 2:
    Montant palier année 2 = Montant loyer * (Palier année 2 / 100)
ELSE:
    Montant palier année 2 = ""

IF Palier année 3:
    Montant palier année 3 = Montant loyer * (Palier année 3 / 100)
ELSE:
    Montant palier année 3 = ""
```

### 1.4 Loyers avec Paliers (Années 1, 2, 3)
```
Loyer avec palier année 1 = Montant loyer - Montant palier année 1
Loyer avec palier année 2 = Montant loyer - Montant palier année 2
Loyer avec palier année 3 = Montant loyer - Montant palier année 3
```

### 1.5 Montant du Loyer en Lettres
```
IF Montant du loyer (numérique):
    Montant du loyer en lettres = number_to_french_words(Montant du loyer)
    Example: 50000 → "CINQUANTE MILLE"
```

### 1.6 Montant du DG en Lettres
```
IF Montant du DG (numérique):
    Montant du DG en lettres = number_to_french_words(Montant du DG)
    Example: 12500 → "DOUZE MILLE CINQ CENTS"
```

## 2. Articles Conditionnels - Arbre de Décision

### 2.1 Comparution Bailleur et Preneur
```
TOUJOURS GÉNÉRÉ
├─ Comparution Bailleur
│  └─ Données du Bailleur depuis Excel
└─ Comparution Preneur
   └─ Données du Preneur depuis Excel
```

### 2.2 Article Préliminaire
```
IF "Conditions suspensives" existe ET non vide:
    ├─ GÉNÉRER Article préliminaire
    └─ Inclure les conditions suspensives
ELSE:
    └─ NE PAS GÉNÉRER (article vide)
```

### 2.3 Article 1 (Désignation)
```
TOUJOURS GÉNÉRÉ
└─ Adresse et description des locaux
```

### 2.4 Article 2 (Durée)
```
TOUJOURS GÉNÉRÉ
├─ Durée du bail
├─ Date de prise d'effet
└─ Période ferme (si Type Bail = "ferme")
```

### 2.5 Article 3 (Destination)
```
TOUJOURS GÉNÉRÉ
├─ Activité autorisée
└─ Enseigne
```

### 2.6 Article 5.3 (Option d'Accession)
```
IF "Option d'accession" == "Oui":
    ├─ GÉNÉRER Article 5.3
    └─ Conditions d'accession à la propriété
ELSE:
    └─ NE PAS GÉNÉRER
```

**Logique détaillée:**
- Vérification de la valeur "Option d'accession"
- Si "Oui" → article complet avec modalités
- Si "Non" ou vide → article non généré

### 2.7 Article 7.1 (Montant du Loyer)
```
TOUJOURS GÉNÉRÉ
├─ Montant du loyer HT HC
├─ Montant du loyer en lettres (CONVERSION)
└─ Format: "50 000 € HT HC (CINQUANTE MILLE EUROS...)"
```

### 2.8 Article 7.2 (Indexation)
```
TOUJOURS GÉNÉRÉ
└─ Formule d'indexation ILC
```

### 2.9 Article 7.3 (Paiement des Loyers)
```
TOUJOURS GÉNÉRÉ
├─ Modalités de paiement (trimestriel)
└─ Date d'exigibilité
```

### 2.10 Article 7.6 (Droit d'Entrée)
```
IF "Droit d'entrée" existe ET > 0:
    ├─ GÉNÉRER Article 7.6
    ├─ Montant du droit d'entrée
    └─ Modalités de paiement
ELSE:
    └─ NE PAS GÉNÉRER
```

**Logique détaillée:**
- Vérification du montant "Droit d'entrée"
- Si montant > 0 → article avec détails
- Si 0 ou vide → article non généré

### 2.11 Article 8 (Garanties)
```
TOUJOURS GÉNÉRÉ (dans PDFs analysés)
├─ Article 8.1 - Dépôt de Garantie
│  ├─ Montant du DG
│  └─ Montant du DG en lettres (CONVERSION)
└─ Article 8.2 - Garantie à Première Demande
   └─ Montant et conditions
```

### 2.12 Article 19 (Frais et Honoraires)
```
IF "Frais agence" existe ET > 0:
    ├─ GÉNÉRER Article 19 spécifique
    ├─ Montant des honoraires
    └─ Répartition Bailleur/Preneur
ELSE:
    └─ Article 19 standard (frais à la charge du Preneur)
```

### 2.13 Article 22.2 (Règlement Copropriété - variation selon contexte)
```
IF Immeuble en copropriété:
    ├─ GÉNÉRER référence au règlement
    └─ Annexer le règlement
ELSE:
    └─ Article standard sans copropriété
```

### 2.14 Article 26 (Dispositions Particulières)
```
Article 26 est TOUJOURS généré mais contient 2 sous-articles conditionnels:

├─ Article 26.1 - Paliers de Loyer
│  IF Palier année 1 OU Palier année 2 OU Palier année 3:
│     ├─ GÉNÉRER Article 26.1
│     └─ Détailler les paliers:
│         ├─ Année 1: Loyer réduit de [Montant palier année 1]
│         ├─ Année 2: Loyer réduit de [Montant palier année 2]
│         └─ Année 3: Loyer réduit de [Montant palier année 3]
│  ELSE:
│     └─ NE PAS GÉNÉRER 26.1
│
└─ Article 26.2 - Franchise de Loyer
   IF "Franchise de loyer" existe ET > 0 mois:
      ├─ GÉNÉRER Article 26.2
      ├─ Durée de la franchise (en mois)
      └─ Date de début du paiement
   ELSE:
      └─ NE PAS GÉNÉRER 26.2
```

**Exemple de paliers (PDF MARTEDI PIZZA):**
```
Article 26.1 détaille:
- Année 1: 50 000€ - 12 000€ = 38 000€ HT HC
- Année 2: 50 000€ + indexation - 6 000€ HT HC
- Année 3+: 50 000€ + indexation (loyer plein)
```

### 2.15 Article 26.1 (Paliers de Loyer)
```
IF Palier année 1 OU Palier année 2 OU Palier année 3:
    ├─ GÉNÉRER Article 26.1
    └─ Détailler chaque palier avec:
        ├─ Loyer de base
        ├─ Réduction
        └─ Loyer effectif
ELSE:
    └─ NE PAS GÉNÉRER
```

**Conditions multiples:**
```python
has_paliers = (
    donnees.get("Palier année 1") or
    donnees.get("Palier année 2") or
    donnees.get("Palier année 3")
)

if has_paliers:
    # Générer article avec tous les paliers présents
    if donnees.get("Palier année 1"):
        texte += f"Année 1: réduction de {Montant palier année 1}€"
    if donnees.get("Palier année 2"):
        texte += f"Année 2: réduction de {Montant palier année 2}€"
    if donnees.get("Palier année 3"):
        texte += f"Année 3: réduction de {Montant palier année 3}€"
```

### 2.16 Article 26.2 (Franchise de Loyer)
```
IF "Franchise de loyer" > 0:
    ├─ GÉNÉRER Article 26.2
    ├─ Durée de la franchise (en mois)
    ├─ Date de début paiement
    └─ Note: Charges restent dues
ELSE:
    └─ NE PAS GÉNÉRER
```

## 3. Système de Remplacement des Placeholders

### 3.1 Niveau 1: Placeholders {{ARTICLE}}
```
Template Word contient:
├─ {{COMPARUTION_BAILLEUR}}
├─ {{COMPARUTION_PRENEUR}}
├─ {{ARTICLE_PRELIMINAIRE}}
├─ {{ARTICLE_1}}
├─ {{ARTICLE_2}}
├─ {{ARTICLE_3}}
├─ {{ARTICLE_5_3}}
├─ {{ARTICLE_7_1}}
├─ {{ARTICLE_7_2}}
├─ {{ARTICLE_7_3}}
├─ {{ARTICLE_7_6}}
├─ {{ARTICLE_8}}
├─ {{ARTICLE_19}}
├─ {{ARTICLE_22_2}}
├─ {{ARTICLE_26}}
├─ {{ARTICLE_26_1}}
├─ {{ARTICLE_26_2}}
├─ {{VILLE}}
└─ {{DATE_SIGNATURE}}

Remplacement:
FOR each {{placeholder}} in document:
    IF articles_generes.get(article_key):
        replace {{placeholder}} with article text
    ELSE:
        replace {{placeholder}} with "" (remove placeholder)
```

### 3.2 Niveau 2: Placeholders [Variable]
```
Dans les articles générés, on trouve:
├─ [Nom Preneur]
├─ [Société Bailleur]
├─ [Montant du loyer]
├─ [Montant du loyer en lettres] ← CONVERSION NUMÉRIQUE
├─ [Montant du DG]
├─ [Montant du DG en lettres] ← CONVERSION NUMÉRIQUE
├─ [Durée Bail]
├─ [Date LOI]
├─ [Montant palier année 1]
├─ [Loyer avec palier année 1]
└─ ... (50+ variables possibles)

Remplacement:
FOR each [Variable] in document:
    IF Variable ends with "en lettres":
        ├─ Extract base variable name
        ├─ Get numeric value from donnees
        ├─ Convert to French words: number_to_french_words()
        └─ Replace with UPPERCASE text
    ELSE:
        └─ Replace with donnees.get(Variable)

    IF value missing or empty:
        └─ Display [Variable] in RED (indication manuelle)
```

## 4. Logique de Conversion "en Lettres"

### 4.1 Détection
```python
if placeholder.endswith(" en lettres"):
    # C'est une conversion numérique
    base_variable = placeholder.replace(" en lettres", "")
    # Exemple: "Montant du loyer en lettres" → "Montant du loyer"
```

### 4.2 Conversion
```python
def number_to_french_words(number: float) -> str:
    """
    Exemples:
    50000 → "CINQUANTE MILLE"
    12500 → "DOUZE MILLE CINQ CENTS"
    160000 → "CENT SOIXANTE MILLE"
    40000 → "QUARANTE MILLE"
    """
    # Gère:
    # - Unités (0-9)
    # - Dizaines (10-99)
    # - Centaines (100-999)
    # - Milliers (1 000-999 999)
    # - Millions (1 000 000+)
    # - Règles spéciales françaises (70, 80, 90)
```

### 4.3 Format dans le Document
```
Exemple Article 7.1:
"Le loyer annuel est fixé, à compter de prise d'effet du Bail,
à la somme de 50.000 € HT HC (CINQUANTE MILLE EUROS HORS TAXES
ET HORS CHARGES)."

Template:
"à la somme de [Montant du loyer] € HT HC ([Montant du loyer en lettres]
EUROS HORS TAXES ET HORS CHARGES)."

Résultat après remplacement:
"à la somme de 50 000 € HT HC (CINQUANTE MILLE EUROS HORS TAXES
ET HORS CHARGES)."
```

## 5. Fichiers de Configuration

### 5.1 Redaction BAIL.xlsx
```
Structure:
├─ Onglet "Rédaction BAIL"
│  ├─ Colonne A: Nom article
│  ├─ Colonne B: Condition (formule Excel)
│  ├─ Colonne C: Template texte
│  └─ Lignes 2-60+: Définitions des articles
│
└─ Onglet "Liste données BAIL"
   ├─ Colonne A: Nom variable
   ├─ Colonne B: Source (formule Excel pointant vers Fiche décision)
   └─ Colonne C: Description (optionnel)
```

### 5.2 Template BAIL avec placeholder.docx
```
Structure du document:
├─ En-tête: Informations société
├─ Titre: "BAIL COMMERCIAL"
├─ Section COMPARUTION:
│  ├─ {{COMPARUTION_BAILLEUR}}
│  ├─ D'UNE PART
│  ├─ ET :
│  ├─ {{COMPARUTION_PRENEUR}}
│  └─ D'AUTRE PART
├─ {{ARTICLE_PRELIMINAIRE}}
├─ {{ARTICLE_1}} - DESIGNATION
├─ {{ARTICLE_2}} - DUREE
├─ {{ARTICLE_3}} - DESTINATION
├─ Article 4 - ENTREE EN JOUISSANCE (texte fixe)
├─ Article 5 - CHARGES ET CONDITIONS
│  └─ {{ARTICLE_5_3}}
├─ Article 6 - CONTRIBUTIONS (texte fixe)
├─ Article 7 - LOYER
│  ├─ {{ARTICLE_7_1}}
│  ├─ {{ARTICLE_7_2}}
│  ├─ {{ARTICLE_7_3}}
│  └─ {{ARTICLE_7_6}}
├─ {{ARTICLE_8}} - GARANTIES
├─ Article 9-18 - (texte fixe standard)
├─ {{ARTICLE_19}} - FRAIS ET HONORAIRES
├─ Article 20-25 - (texte fixe standard)
├─ {{ARTICLE_26}} - DISPOSITIONS PARTICULIERES
│  ├─ {{ARTICLE_26_1}}
│  └─ {{ARTICLE_26_2}}
└─ Article 27-28 - (texte fixe standard)
```

## 6. Flux de Données Complet

```
ÉTAPE 1: Extraction
├─ Excel (Fiche de décision)
│  └─ ExcelParser.extract_variables()
└─ Output: Dict[str, str] variables (50+ clés)

ÉTAPE 2: Enrichissement
├─ variables (brutes)
│  └─ BailGenerator.calculer_variables_derivees()
└─ Output: Dict[str, Any] donnees_complete (70+ clés)
    ├─ Variables originales
    └─ Variables dérivées calculées

ÉTAPE 3: Génération Articles
├─ donnees_complete
│  └─ BailGenerator.generer_bail()
└─ Output: Dict[str, str] articles_generes (16+ articles)
    ├─ Pour chaque article:
    │  ├─ Évaluer condition
    │  ├─ Si True: générer texte
    │  └─ Si False: article vide ""
    └─ Remplacer [Variable] dans templates

ÉTAPE 4: Génération Document Word
├─ articles_generes + donnees_complete + template.docx
│  └─ BailWordGenerator.generer_document()
└─ Output: Document Word final
    ├─ Passe 1: Remplacer {{ARTICLE}}
    │  └─ Pour chaque {{placeholder}}:
    │      ├─ Si article existe: insérer texte
    │      └─ Sinon: supprimer placeholder
    └─ Passe 2: Remplacer [Variable]
       └─ Pour chaque [placeholder]:
           ├─ Si "en lettres": convertir nombre → texte
           ├─ Si valeur existe: remplacer
           └─ Sinon: afficher en ROUGE
```

## 7. Règles de Gestion Importantes

### 7.1 Priorité des Articles
```
Articles OBLIGATOIRES (toujours générés):
├─ Comparution Bailleur et Preneur
├─ Article 1 - Désignation
├─ Article 2 - Durée
├─ Article 3 - Destination
├─ Articles 4-6 (texte fixe)
├─ Article 7.1, 7.2, 7.3 - Loyer
├─ Article 8 - Garanties
└─ Articles 9-25 (texte fixe standard)

Articles CONDITIONNELS (selon données):
├─ Article préliminaire (si conditions suspensives)
├─ Article 5.3 (si option d'accession)
├─ Article 7.6 (si droit d'entrée)
├─ Article 26.1 (si paliers)
└─ Article 26.2 (si franchise)
```

### 7.2 Validation des Données
```
Avant génération:
├─ Vérifier présence données obligatoires:
│  ├─ Nom Preneur
│  ├─ Société Bailleur
│  ├─ Montant du loyer
│  ├─ Durée Bail
│  └─ Date LOI / Date de signature
│
└─ Vérifier cohérence:
   ├─ Surface totale >= Surface RDC
   ├─ Montant DG >= 0
   ├─ Durée Bail > 0
   └─ Paliers < 100%
```

### 7.3 Gestion des Erreurs
```
Si données manquantes:
├─ Variables obligatoires → Afficher en ROUGE
├─ Variables optionnelles → Article non généré
└─ Variables dérivées → Calcul ignoré, valeur vide

Si conversion échoue:
├─ "en lettres" → Afficher placeholder en ROUGE
└─ Logger l'erreur pour debug
```

## 8. Exemples de Scénarios

### Scénario A: BAIL Standard (pas de paliers, pas d'options)
```
Données:
├─ Montant du loyer: 50 000€
├─ Durée: 10 ans
├─ DG: 12 500€
├─ Pas de paliers
├─ Pas de franchise
├─ Pas d'option d'accession
└─ Pas de droit d'entrée

Articles générés:
├─ ✓ Comparution
├─ ✗ Article préliminaire (pas de conditions suspensives)
├─ ✓ Article 1, 2, 3, 4-7.3
├─ ✗ Article 5.3 (pas d'option)
├─ ✗ Article 7.6 (pas de droit d'entrée)
├─ ✓ Article 8, 9-25
├─ ✗ Article 26.1 (pas de paliers)
└─ ✗ Article 26.2 (pas de franchise)
```

### Scénario B: BAIL avec Paliers et Franchise (MARTEDI PIZZA)
```
Données:
├─ Montant du loyer: 50 000€
├─ Durée: 10 ans ferme (6 ans)
├─ DG: 12 500€
├─ Palier année 1: 24% (12 000€)
├─ Palier année 2: 12% (6 000€)
├─ Franchise: 3 mois
├─ Pas d'option d'accession
└─ Pas de droit d'entrée

Articles générés:
├─ ✓ Comparution
├─ ✗ Article préliminaire
├─ ✓ Article 1, 2, 3, 4-7.3
├─ ✗ Article 5.3
├─ ✗ Article 7.6
├─ ✓ Article 8, 9-25
├─ ✓ Article 26.1 avec paliers années 1 et 2:
│  ├─ "Année 1: loyer réduit de 12 000€ → 38 000€"
│  └─ "Année 2: loyer indexé réduit de 6 000€"
└─ ✓ Article 26.2 avec franchise 3 mois
```

### Scénario C: BAIL Complet (toutes options)
```
Données:
├─ Montant du loyer: 160 000€
├─ Durée: 12 ans ferme (9 ans)
├─ DG: 40 000€
├─ Droit d'entrée: 50 000€
├─ Paliers années 1, 2, 3
├─ Franchise: 6 mois
├─ Option d'accession: Oui
└─ Conditions suspensives

Articles générés:
├─ ✓ Comparution
├─ ✓ Article préliminaire (conditions suspensives)
├─ ✓ Article 1, 2, 3, 4-7.3
├─ ✓ Article 5.3 (option d'accession)
├─ ✓ Article 7.6 (droit d'entrée 50 000€)
├─ ✓ Article 8, 9-25
├─ ✓ Article 26.1 (3 paliers)
└─ ✓ Article 26.2 (franchise 6 mois)
```

## 9. Points d'Attention pour Développement

### 9.1 Performance
```
- Cache des conversions "en lettres" si même montant répété
- Pré-compiler les regex pour placeholder detection
- Utiliser lazy evaluation pour variables dérivées
```

### 9.2 Maintenance
```
- Documenter chaque condition dans le code
- Logger les décisions de génération d'articles
- Créer tests unitaires pour chaque scénario
```

### 9.3 Extension Future
```
Facile à ajouter:
├─ Nouveaux articles conditionnels
├─ Nouvelles variables dérivées
├─ Nouvelles règles de conversion
└─ Support multi-langues (conversion nombres)
```

---

## Résumé des 16+ Articles Conditionnels

| Article | Nom | Condition | Toujours Généré |
|---------|-----|-----------|-----------------|
| Comparution | Bailleur/Preneur | Aucune | ✓ Oui |
| Préliminaire | Conditions Suspensives | Si conditions suspensives | ✗ Non |
| 1 | Désignation | Aucune | ✓ Oui |
| 2 | Durée | Aucune | ✓ Oui |
| 3 | Destination | Aucune | ✓ Oui |
| 5.3 | Option Accession | Si "Option d'accession" == Oui | ✗ Non |
| 7.1 | Montant Loyer | Aucune | ✓ Oui |
| 7.2 | Indexation | Aucune | ✓ Oui |
| 7.3 | Paiement | Aucune | ✓ Oui |
| 7.6 | Droit d'Entrée | Si "Droit d'entrée" > 0 | ✗ Non |
| 8 | Garanties | Aucune | ✓ Oui |
| 19 | Frais | Aucune (variable si frais agence) | ✓ Oui |
| 22.2 | Règlement Copro | Variable selon contexte | ✓ Oui |
| 26 | Dispositions Particulières | Aucune (conteneur) | ✓ Oui |
| 26.1 | Paliers Loyer | Si paliers années 1/2/3 | ✗ Non |
| 26.2 | Franchise Loyer | Si "Franchise de loyer" > 0 | ✗ Non |

**Total: 16 articles principaux, dont 6 conditionnels**
