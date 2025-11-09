# Référence des Placeholders - Système BAIL

## Date de mise à jour
2025-11-09

## Introduction

Ce document liste tous les placeholders utilisés dans le système de génération de BAIL, leur source (Excel, INPI, ou calcul), leur format, et leurs variations possibles.

---

## Table des matières

1. [Placeholders d'identité](#1-placeholders-didentité)
2. [Placeholders de dates](#2-placeholders-de-dates)
3. [Placeholders financiers](#3-placeholders-financiers)
4. [Placeholders de localisation](#4-placeholders-de-localisation)
5. [Placeholders conditionnels](#5-placeholders-conditionnels)
6. [Placeholders calculés](#6-placeholders-calculés)
7. [Mapping Excel → Placeholder](#7-mapping-excel--placeholder)

---

## 1. Placeholders d'identité

### Bailleur

| Placeholder | Source | Format | Exemple | Notes |
|-------------|--------|--------|---------|-------|
| `[NOM DU BAILLEUR]` | Excel | Texte | FORGEOT & AL | Nom de la société bailleresse |
| `[SIREN BAILLEUR]` | Excel | 9 chiffres | 123456789 | Numéro SIREN du bailleur |
| `[TYPE DE SOCIETE BAILLEUR]` | Excel ou INPI | Texte | SAS, Société par actions simplifiée | Forme juridique |
| `[CAPITAL SOCIAL BAILLEUR]` | Excel ou INPI | "XXX XXX XXX €" | 145 131 987 € | Formaté avec espaces |
| `[ADRESSE BAILLEUR]` | Excel ou INPI | Adresse complète | 17 RUE DE L'ECHIQUIER 75010 PARIS | |
| `[RCS BAILLEUR]` | Excel ou INPI | Ville | PARIS | Localité du RCS |
| `[PRESIDENT BAILLEUR]` | Hardcodé | Texte | Monsieur Maxime FORGEOT | Toujours cette valeur |

### Preneur

| Placeholder | Source | Format | Exemple | Notes |
|-------------|--------|--------|---------|-------|
| `[NOM DU PRENEUR]` | Excel | Texte | KARAVEL | Nom de la société preneuse |
| `[SIREN PRENEUR]` | Excel | 9 chiffres | 532321916 | Numéro SIREN du preneur |
| `[NOM DE LA SOCIETE]` | INPI (enrichi) | Texte | KARAVEL | Nom officiel depuis INPI |
| `[TYPE DE SOCIETE]` | INPI (enrichi) | Texte long | SASU, Société par actions simplifiée unipersonnelle | Forme juridique complète |
| `[CAPITAL SOCIAL]` | INPI (enrichi) | "XXX XXX XXX €" | 145 131 987 € | **Formaté avec espaces** |
| `[ADRESSE DE DOMICILIATION]` | INPI (enrichi) | Adresse complète | 17 RUE DE L'ECHIQUIER 75010 PARIS 10E ARRONDISSEMENT FRANCE | Adresse du siège social |
| `[LOCALITE RCS]` | INPI (enrichi) | Ville | PARIS | Extraite de l'adresse, arrondissements supprimés |
| `[PRESIDENT DE LA SOCIETE]` | INPI (enrichi) | Nom complet | CHARLES | Président/Gérant (commissaires exclus) |

**Notes importantes :**
- Les placeholders INPI sont remplis automatiquement si SIREN fourni
- Si INPI échoue, utilise les valeurs Excel en fallback
- Le président filtré : seuls Gérant, Président, Directeur général acceptés (pas les commissaires)

---

## 2. Placeholders de dates

| Placeholder | Source | Format | Exemple | Calcul |
|-------------|--------|--------|---------|--------|
| `[Date de prise d'effet du bail]` | Excel | DD/MM/YYYY | 01/01/2025 | Date de début du bail |
| `[DATE DE FIN INITIALE]` | Calculé | DD/MM/YYYY | 01/01/2034 | Date début + durée initiale |
| `[DATE DE FIN AVEC GAPD]` | Calculé | DD/MM/YYYY | 01/01/2037 | Date début + durée totale |
| `[Date de signature du bail]` | Excel | DD/MM/YYYY | 15/12/2024 | Date de signature |

**Formules de calcul :**
```python
# Date de fin initiale
date_fin_initiale = date_debut + relativedelta(years=duree_initiale)

# Date de fin avec GAPD
duree_totale = duree_initiale + duree_gapd
date_fin_gapd = date_debut + relativedelta(years=duree_totale)
```

---

## 3. Placeholders financiers

### Loyers

| Placeholder | Source | Format | Exemple | Calcul |
|-------------|--------|--------|---------|--------|
| `[Montant loyer HT mensuel]` | Excel | "X XXX,XX €" | 1 500,00 € | Base mensuelle |
| `[LOYER ANNUEL HT]` | Calculé | "XX XXX,XX €" | 18 000,00 € | Loyer mensuel × 12 |
| `[LOYER ANNUEL TTC]` | Calculé | "XX XXX,XX €" | 21 600,00 € | Loyer annuel HT × (1 + TVA/100) |
| `[LOYER TRIMESTRIEL]` | Calculé | "X XXX,XX €" | 4 500,00 € | Loyer mensuel × 3 |
| `[TVA]` | Excel | "XX" ou "XX%" | 20 | Taux de TVA (défaut: 20) |

### Charges

| Placeholder | Source | Format | Exemple | Calcul |
|-------------|--------|--------|---------|--------|
| `[Provision pour charges mensuelles]` | Excel | "XXX,XX €" | 150,00 € | Charges mensuelles |
| `[PROVISION CHARGES ANNUELLE]` | Calculé | "X XXX,XX €" | 1 800,00 € | Charges mensuelles × 12 |
| `[TOTAL LOYER + CHARGES MENSUEL]` | Calculé | "X XXX,XX €" | 1 650,00 € | Loyer + charges mensuels |
| `[TOTAL LOYER + CHARGES TRIMESTRIEL]` | Calculé | "X XXX,XX €" | 4 950,00 € | (Loyer + charges) × 3 |

### Dépôt de garantie

| Placeholder | Source | Format | Exemple | Calcul |
|-------------|--------|--------|---------|--------|
| `[Dépôt de garantie Nombre de mois]` | Excel | Chiffre | 3 | Nombre de mois |
| `[DEPOT DE GARANTIE]` | Calculé | "X XXX,XX €" | 4 500,00 € | Loyer mensuel HT × nb_mois |

### Honoraires

| Placeholder | Source | Format | Exemple | Notes |
|-------------|--------|--------|---------|-------|
| `[HONORAIRES TTC ANNEE 1]` | Excel | Texte + montant | Oui - 1 200,00 € | Si commence par "Oui" → inclure Article 8.2 |
| `[HONORAIRES TTC ANNEE 2]` | Excel | Montant ou vide | 1 200,00 € | Optionnel |
| `[HONORAIRES TTC ANNEE 3]` | Excel | Montant ou vide | 1 200,00 € | Optionnel |

---

## 4. Placeholders de localisation

### Local commercial

| Placeholder | Source | Format | Exemple | Notes |
|-------------|--------|--------|---------|-------|
| `[Adresse du local]` | Excel | Adresse | 123 Rue de la Paix 75001 PARIS | Adresse du bien loué |
| `[Numéro de lot]` | Excel | Numéro | 12 | Numéro de lot |
| `[Surface du local]` | Excel | "XX,XX m²" | 50,00 m² | Surface en m² |
| `[Etage]` | Excel | Texte | Rez-de-chaussée | Étage du local |
| `[Destination des locaux]` | Excel | Texte | Commerce de détail | Usage prévu |

### Copropriété

| Placeholder | Source | Format | Exemple | Notes |
|-------------|--------|--------|---------|-------|
| `[Nom du syndic]` | Excel | Texte | Cabinet XYZ | Syndic de copropriété |
| `[Adresse du syndic]` | Excel | Adresse | 45 Avenue Victor Hugo 75016 PARIS | |

---

## 5. Placeholders conditionnels

### Article 8.2 - Charges et impôts

**Condition d'inclusion :**
```python
if "Oui" in data.get("HONORAIRES TTC ANNEE 1", ""):
    # Inclure Article 8.2 dans le document
```

| Placeholder | Source | Notes |
|-------------|--------|-------|
| `[HONORAIRES TTC ANNEE 1]` | Excel | Si commence par "Oui", inclure article |
| `[HONORAIRES TTC ANNEE 2]` | Excel | Optionnel |
| `[HONORAIRES TTC ANNEE 3]` | Excel | Optionnel |

### Article 26.2 - Clause résolutoire

**Condition d'inclusion :**
```python
if data.get("Clause résolutoire", "").strip().upper() == "OUI":
    # Inclure Article 26.2 dans le document
```

| Placeholder | Source | Format | Notes |
|-------------|--------|--------|-------|
| `[Clause résolutoire]` | Excel | "OUI" ou "NON" | Si "OUI", inclure clause |

---

## 6. Placeholders calculés

### Durées

| Placeholder | Source | Calcul | Exemple |
|-------------|--------|--------|---------|
| `[Durée initiale du bail]` | Excel | - | 9 |
| `[Durée GAPD]` | Excel | - | 3 |
| `[DUREE TOTALE]` | Calculé | Durée initiale + Durée GAPD | 12 |

**Formule :**
```python
duree_totale = int(duree_initiale) + int(duree_gapd)
```

### Indexation

| Placeholder | Source | Format | Exemple |
|-------------|--------|--------|---------|
| `[Indice de référence]` | Excel | Texte | ILC (Indice des Loyers Commerciaux) |
| `[Date de l'indice de référence]` | Excel | Texte | 2ème trimestre 2024 |
| `[Valeur de l'indice de référence]` | Excel | Nombre | 120,45 |

### Travaux

| Placeholder | Source | Format | Notes |
|-------------|--------|--------|-------|
| `[Travaux à la charge du preneur]` | Excel | Texte long | Description des travaux |
| `[Délai de réalisation des travaux]` | Excel | Texte | 3 mois à compter de la prise d'effet |

---

## 7. Mapping Excel → Placeholder

### Tableau de correspondance

| Nom dans Excel | Placeholder dans template | Type | Transformation |
|----------------|---------------------------|------|----------------|
| NOM DU BAILLEUR | [NOM DU BAILLEUR] | Direct | Aucune |
| SIREN BAILLEUR | [SIREN BAILLEUR] | Direct | Aucune |
| NOM DU PRENEUR | [NOM DU PRENEUR] | Direct | Aucune |
| SIREN PRENEUR | [SIREN PRENEUR] | Direct | Aucune → Déclenche enrichissement INPI |
| Date de prise d'effet du bail | [Date de prise d'effet du bail] | Direct | Format DD/MM/YYYY |
| Durée initiale du bail | [Durée initiale du bail] | Direct | Nombre d'années |
| Durée GAPD | [Durée GAPD] | Direct | Nombre d'années |
| - | [DUREE TOTALE] | Calculé | Durée initiale + Durée GAPD |
| - | [DATE DE FIN INITIALE] | Calculé | Date début + durée initiale |
| - | [DATE DE FIN AVEC GAPD] | Calculé | Date début + durée totale |
| Montant loyer HT mensuel | [Montant loyer HT mensuel] | Direct | Format monétaire |
| - | [LOYER ANNUEL HT] | Calculé | Loyer mensuel × 12 |
| - | [LOYER ANNUEL TTC] | Calculé | Loyer annuel HT × (1 + TVA/100) |
| - | [LOYER TRIMESTRIEL] | Calculé | Loyer mensuel × 3 |
| TVA | [TVA] | Direct | Nombre (défaut: 20) |
| Provision pour charges mensuelles | [Provision pour charges mensuelles] | Direct | Format monétaire |
| - | [PROVISION CHARGES ANNUELLE] | Calculé | Charges mensuelles × 12 |
| - | [TOTAL LOYER + CHARGES MENSUEL] | Calculé | Loyer + charges mensuels |
| - | [TOTAL LOYER + CHARGES TRIMESTRIEL] | Calculé | (Loyer + charges) × 3 |
| Dépôt de garantie Nombre de mois | [Dépôt de garantie Nombre de mois] | Direct | Nombre |
| - | [DEPOT DE GARANTIE] | Calculé | Loyer mensuel HT × nb_mois |
| HONORAIRES TTC ANNEE 1 | [HONORAIRES TTC ANNEE 1] | Direct | Si "Oui" → Article 8.2 |
| HONORAIRES TTC ANNEE 2 | [HONORAIRES TTC ANNEE 2] | Direct | Optionnel |
| HONORAIRES TTC ANNEE 3 | [HONORAIRES TTC ANNEE 3] | Direct | Optionnel |
| Clause résolutoire | [Clause résolutoire] | Direct | Si "OUI" → Article 26.2 |
| Adresse du local | [Adresse du local] | Direct | Aucune |
| Surface du local | [Surface du local] | Direct | Format avec m² |
| Destination des locaux | [Destination des locaux] | Direct | Aucune |

### Enrichissement INPI (si SIREN PRENEUR fourni)

| Champ INPI | Placeholder | Source | Format |
|------------|-------------|--------|--------|
| Nom entreprise | [NOM DE LA SOCIETE] | INPI API ou Scraping | Texte brut |
| Forme juridique | [TYPE DE SOCIETE] | INPI API ou Scraping | Ex: "SASU, Société par actions..." |
| Capital | [CAPITAL SOCIAL] | INPI API ou Scraping | "145 131 987 €" (avec espaces) |
| Adresse siège | [ADRESSE DE DOMICILIATION] | INPI API ou Scraping | Adresse complète |
| Greffe RCS | [LOCALITE RCS] | INPI API ou Scraping | Ville (ex: "PARIS") |
| Dirigeant | [PRESIDENT DE LA SOCIETE] | INPI API ou Scraping | Nom complet (filtré) |

**Notes sur l'enrichissement :**
- Automatique si `SIREN PRENEUR` fourni
- Fallback sur scraping si API rate limit
- Filtre les commissaires aux comptes
- Formate automatiquement le capital avec espaces

---

## Variations et synonymes

### Placeholders avec variations possibles

Certains placeholders peuvent avoir plusieurs noms selon le contexte :

| Placeholder principal | Variations acceptées | Notes |
|----------------------|---------------------|-------|
| [NOM DE LA SOCIETE] | [NOM DU PRENEUR] | Même valeur, contextes différents |
| [PRESIDENT DE LA SOCIETE] | [GERANT], [DIRIGEANT] | Selon la forme juridique |
| [ADRESSE DE DOMICILIATION] | [ADRESSE DU SIEGE] | Même valeur |
| [LOCALITE RCS] | [RCS], [GREFFE] | Ville du RCS |

---

## Format des valeurs

### Formatage monétaire

**Standard :**
```
Format Excel : 1500.00
Format document : 1 500,00 €
```

**Grands montants :**
```
Format Excel : 145131987
Format document : 145 131 987 €
```

**Règles :**
- Espaces tous les 3 chiffres (séparateur de milliers)
- Virgule pour les décimales
- Symbole € après le montant
- Deux décimales pour les cents

### Formatage des dates

**Standard :**
```
Format Excel : 2025-01-01 ou 01/01/2025
Format document : 01/01/2025
```

**Règles :**
- Format DD/MM/YYYY
- Zéros devant les jours/mois < 10

### Formatage des durées

**Standard :**
```
Format : Nombre entier d'années
Exemple : 9 (pour 9 ans)
```

---

## Placeholders non utilisés / Obsolètes

Liste des placeholders qui ont existé mais ne sont plus utilisés :

| Placeholder obsolète | Raison | Remplacement |
|---------------------|--------|--------------|
| [FORME JURIDIQUE] | Renommé | [TYPE DE SOCIETE] |
| [PRESIDENT] | Ambiguïté | [PRESIDENT DE LA SOCIETE] |
| [CAPITAL] | Pas de format | [CAPITAL SOCIAL] |

---

## Checklist de validation

Avant génération d'un document, vérifier que les placeholders suivants sont présents :

### ✅ Obligatoires
- [ ] [NOM DU BAILLEUR]
- [ ] [SIREN BAILLEUR]
- [ ] [NOM DU PRENEUR]
- [ ] [SIREN PRENEUR]
- [ ] [Date de prise d'effet du bail]
- [ ] [Durée initiale du bail]
- [ ] [Montant loyer HT mensuel]
- [ ] [Adresse du local]

### ⚠️ Recommandés
- [ ] [Durée GAPD]
- [ ] [TVA]
- [ ] [Provision pour charges mensuelles]
- [ ] [Dépôt de garantie Nombre de mois]

### 🔄 Enrichissement INPI
- [ ] [NOM DE LA SOCIETE]
- [ ] [TYPE DE SOCIETE]
- [ ] [CAPITAL SOCIAL]
- [ ] [ADRESSE DE DOMICILIATION]
- [ ] [LOCALITE RCS]
- [ ] [PRESIDENT DE LA SOCIETE]

---

## Notes techniques

### Ordre de priorité des sources

1. **INPI** (si SIREN fourni et enrichissement réussi)
2. **Excel** (fallback si INPI échoue)
3. **Calculé** (dérivé des autres valeurs)
4. **Valeur par défaut** (si rien trouvé)

### Gestion des valeurs manquantes

```python
# Si placeholder non trouvé
→ Laisser le placeholder dans le document : "[PLACEHOLDER]"
→ Logger un warning
→ Continuer la génération
```

### Encodage

Tous les placeholders utilisent l'encodage UTF-8 pour supporter les caractères accentués français.

---

## Glossaire

- **SIREN** : Système d'Identification du Répertoire des Entreprises (9 chiffres)
- **GAPD** : Garantie d'Appui au Paiement du Dépôt (durée supplémentaire)
- **RCS** : Registre du Commerce et des Sociétés
- **ILC** : Indice des Loyers Commerciaux
- **HT** : Hors Taxes
- **TTC** : Toutes Taxes Comprises
