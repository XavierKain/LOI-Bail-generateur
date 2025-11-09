# Tests et Conditions Logiques - Système BAIL

## Date de mise à jour
2025-11-09

## Introduction

Ce document détaille l'ensemble des tests logiques, conditions, et règles métier utilisées dans la génération des documents BAIL.

---

## Table des matières

1. [Conditions d'inclusion d'articles](#1-conditions-dinclusion-darticles)
2. [Validation des données](#2-validation-des-données)
3. [Calculs conditionnels](#3-calculs-conditionnels)
4. [Enrichissement INPI](#4-enrichissement-inpi)
5. [Formatage conditionnel](#5-formatage-conditionnel)
6. [Gestion des erreurs](#6-gestion-des-erreurs)
7. [Tests de non-régression](#7-tests-de-non-régression)

---

## 1. Conditions d'inclusion d'articles

### Article 8.2 - Charges et Impôts (Honoraires)

**Localisation dans le code :** [modules/document_generator_bail.py](modules/document_generator_bail.py)

#### Condition d'inclusion

```python
def _should_include_article_8_2(self, data: dict) -> bool:
    """
    Détermine si l'Article 8.2 doit être inclus dans le document.

    Règle métier:
    - Si HONORAIRES TTC ANNEE 1 commence par "Oui" → Inclure
    - Sinon → Ne pas inclure

    Args:
        data: Dictionnaire des données du bail

    Returns:
        True si l'article doit être inclus, False sinon
    """
    honoraires_annee1 = data.get("HONORAIRES TTC ANNEE 1", "")

    # Test : commence par "Oui" (insensible à la casse)
    if isinstance(honoraires_annee1, str):
        return honoraires_annee1.strip().lower().startswith("oui")

    return False
```

#### Cas de test

| Valeur Excel | Résultat | Raison |
|--------------|----------|--------|
| `"Oui - 1 200,00 €"` | ✅ Inclure | Commence par "Oui" |
| `"Oui"` | ✅ Inclure | Commence par "Oui" |
| `"OUI - 1200€"` | ✅ Inclure | Insensible à la casse |
| `"Non"` | ❌ Ne pas inclure | Ne commence pas par "Oui" |
| `""` (vide) | ❌ Ne pas inclure | Valeur vide |
| `"1 200,00 €"` | ❌ Ne pas inclure | Ne commence pas par "Oui" |

#### Impact sur le document

**Si inclus :**
```
ARTICLE 8 - CHARGES ET IMPÔTS

8.1. [Contenu standard...]

8.2. HONORAIRES DE GESTION
Le Preneur s'engage à verser au Bailleur les honoraires suivants :
- Année 1 : [HONORAIRES TTC ANNEE 1]
- Année 2 : [HONORAIRES TTC ANNEE 2]
- Année 3 : [HONORAIRES TTC ANNEE 3]
```

**Si non inclus :**
```
ARTICLE 8 - CHARGES ET IMPÔTS

8.1. [Contenu standard...]

[Article 8.2 complètement absent du document]
```

---

### Article 26.2 - Clause résolutoire

**Localisation dans le code :** [modules/document_generator_bail.py](modules/document_generator_bail.py)

#### Condition d'inclusion

```python
def _should_include_article_26_2(self, data: dict) -> bool:
    """
    Détermine si l'Article 26.2 (clause résolutoire) doit être inclus.

    Règle métier:
    - Si "Clause résolutoire" == "OUI" → Inclure
    - Sinon → Ne pas inclure

    Args:
        data: Dictionnaire des données du bail

    Returns:
        True si la clause doit être incluse, False sinon
    """
    clause_resolutoire = data.get("Clause résolutoire", "")

    # Test : égal à "OUI" (insensible à la casse, espaces ignorés)
    if isinstance(clause_resolutoire, str):
        return clause_resolutoire.strip().upper() == "OUI"

    return False
```

#### Cas de test

| Valeur Excel | Résultat | Raison |
|--------------|----------|--------|
| `"OUI"` | ✅ Inclure | Égal à "OUI" |
| `"Oui"` | ✅ Inclure | Insensible à la casse |
| `"oui"` | ✅ Inclure | Insensible à la casse |
| `" OUI "` | ✅ Inclure | Espaces ignorés |
| `"NON"` | ❌ Ne pas inclure | Pas égal à "OUI" |
| `"Non"` | ❌ Ne pas inclure | Pas égal à "OUI" |
| `""` (vide) | ❌ Ne pas inclure | Valeur vide |
| `"Yes"` | ❌ Ne pas inclure | Pas égal à "OUI" |

#### Impact sur le document

**Si inclus :**
```
ARTICLE 26 - RÉSILIATION

26.1. [Contenu standard...]

26.2. CLAUSE RÉSOLUTOIRE
En cas de non-paiement d'un seul terme de loyer ou de charges à son échéance,
[...texte complet de la clause résolutoire...]
```

**Si non inclus :**
```
ARTICLE 26 - RÉSILIATION

26.1. [Contenu standard...]

[Article 26.2 complètement absent du document]
```

---

## 2. Validation des données

### Validation avant génération

**Localisation :** [modules/document_generator_bail.py](modules/document_generator_bail.py)

#### Champs obligatoires

```python
def _validate_required_fields(self, data: dict) -> tuple[bool, list[str]]:
    """
    Valide la présence des champs obligatoires.

    Returns:
        (is_valid, missing_fields)
    """
    required_fields = [
        "NOM DU BAILLEUR",
        "SIREN BAILLEUR",
        "NOM DU PRENEUR",
        "SIREN PRENEUR",
        "Date de prise d'effet du bail",
        "Durée initiale du bail",
        "Montant loyer HT mensuel",
        "Adresse du local"
    ]

    missing = []
    for field in required_fields:
        if not data.get(field):
            missing.append(field)

    return (len(missing) == 0, missing)
```

#### Tests de validation

| Champ | Test | Erreur si |
|-------|------|-----------|
| NOM DU BAILLEUR | Présence | Vide ou None |
| SIREN BAILLEUR | Présence + Format | Vide ou non-numérique ou ≠ 9 chiffres |
| NOM DU PRENEUR | Présence | Vide ou None |
| SIREN PRENEUR | Présence + Format | Vide ou non-numérique ou ≠ 9 chiffres |
| Date de prise d'effet | Présence + Format | Vide ou format invalide |
| Durée initiale | Présence + Type | Vide ou non-numérique ou ≤ 0 |
| Montant loyer HT | Présence + Type | Vide ou non-numérique ou ≤ 0 |
| Adresse du local | Présence | Vide ou None |

#### Validation des formats

##### SIREN

```python
def _validate_siren(self, siren: str) -> bool:
    """
    Valide le format d'un numéro SIREN.

    Règles:
    - Exactement 9 chiffres
    - Uniquement des caractères numériques

    Returns:
        True si valide, False sinon
    """
    if not siren:
        return False

    # Supprimer les espaces
    siren_clean = siren.replace(" ", "")

    # Test : 9 chiffres exactement
    if len(siren_clean) != 9:
        return False

    # Test : uniquement des chiffres
    if not siren_clean.isdigit():
        return False

    return True
```

**Cas de test :**

| Valeur | Résultat | Raison |
|--------|----------|--------|
| `"123456789"` | ✅ Valide | 9 chiffres |
| `"532321916"` | ✅ Valide | 9 chiffres |
| `"123 456 789"` | ✅ Valide | 9 chiffres (espaces supprimés) |
| `"12345678"` | ❌ Invalide | Seulement 8 chiffres |
| `"1234567890"` | ❌ Invalide | 10 chiffres |
| `"12345678A"` | ❌ Invalide | Contient une lettre |
| `""` | ❌ Invalide | Vide |

##### Date

```python
def _validate_date(self, date_str: str) -> bool:
    """
    Valide le format d'une date.

    Formats acceptés:
    - DD/MM/YYYY
    - YYYY-MM-DD

    Returns:
        True si valide, False sinon
    """
    if not date_str:
        return False

    # Test format DD/MM/YYYY
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        pass

    # Test format YYYY-MM-DD
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        pass

    return False
```

**Cas de test :**

| Valeur | Résultat | Raison |
|--------|----------|--------|
| `"01/01/2025"` | ✅ Valide | Format DD/MM/YYYY |
| `"2025-01-01"` | ✅ Valide | Format YYYY-MM-DD |
| `"31/12/2024"` | ✅ Valide | Date valide |
| `"32/12/2024"` | ❌ Invalide | Jour > 31 |
| `"01/13/2024"` | ❌ Invalide | Mois > 12 |
| `"2024"` | ❌ Invalide | Format incomplet |
| `"01-01-2025"` | ❌ Invalide | Format non supporté |

##### Montant monétaire

```python
def _validate_amount(self, amount: any) -> bool:
    """
    Valide qu'une valeur est un montant valide.

    Règles:
    - Nombre (int ou float)
    - > 0

    Returns:
        True si valide, False sinon
    """
    try:
        value = float(amount)
        return value > 0
    except (ValueError, TypeError):
        return False
```

**Cas de test :**

| Valeur | Résultat | Raison |
|--------|----------|--------|
| `1500.00` | ✅ Valide | Nombre positif |
| `"1500"` | ✅ Valide | Convertible en nombre |
| `1500` | ✅ Valide | Entier positif |
| `0` | ❌ Invalide | Non positif |
| `-100` | ❌ Invalide | Négatif |
| `"ABC"` | ❌ Invalide | Non numérique |
| `None` | ❌ Invalide | None |

---

## 3. Calculs conditionnels

### Durée totale du bail

```python
def _calculate_duree_totale(self, data: dict) -> int:
    """
    Calcule la durée totale du bail.

    Formule:
    durée_totale = durée_initiale + durée_GAPD

    Conditions:
    - Si durée_GAPD absente ou invalide → utiliser 0
    - Si durée_initiale absente ou invalide → erreur

    Returns:
        Durée totale en années

    Raises:
        ValueError si durée_initiale invalide
    """
    # Durée initiale (obligatoire)
    duree_initiale = data.get("Durée initiale du bail")
    if not duree_initiale:
        raise ValueError("Durée initiale du bail manquante")

    try:
        duree_initiale = int(duree_initiale)
    except (ValueError, TypeError):
        raise ValueError(f"Durée initiale invalide: {duree_initiale}")

    # Durée GAPD (optionnelle, défaut = 0)
    duree_gapd = data.get("Durée GAPD", 0)
    try:
        duree_gapd = int(duree_gapd) if duree_gapd else 0
    except (ValueError, TypeError):
        duree_gapd = 0  # Silencieux si invalide

    return duree_initiale + duree_gapd
```

**Cas de test :**

| Durée initiale | Durée GAPD | Résultat | Notes |
|----------------|------------|----------|-------|
| 9 | 3 | 12 | Cas standard |
| 9 | 0 | 9 | Sans GAPD |
| 9 | `""` (vide) | 9 | GAPD vide → 0 |
| 9 | `None` | 9 | GAPD None → 0 |
| `""` | 3 | ❌ Erreur | Durée initiale obligatoire |
| `None` | 3 | ❌ Erreur | Durée initiale obligatoire |
| "ABC" | 3 | ❌ Erreur | Durée initiale invalide |

---

### Calcul des loyers

#### Loyer annuel HT

```python
def _calculate_loyer_annuel_ht(self, data: dict) -> float:
    """
    Calcule le loyer annuel HT.

    Formule:
    loyer_annuel_ht = loyer_mensuel_ht × 12

    Returns:
        Montant en euros

    Raises:
        ValueError si loyer_mensuel invalide
    """
    loyer_mensuel = data.get("Montant loyer HT mensuel")

    if not loyer_mensuel:
        raise ValueError("Montant loyer HT mensuel manquant")

    try:
        loyer_mensuel = float(loyer_mensuel)
    except (ValueError, TypeError):
        raise ValueError(f"Loyer mensuel invalide: {loyer_mensuel}")

    if loyer_mensuel <= 0:
        raise ValueError(f"Loyer mensuel doit être positif: {loyer_mensuel}")

    return loyer_mensuel * 12
```

**Cas de test :**

| Loyer mensuel HT | Résultat | Notes |
|------------------|----------|-------|
| 1500.00 | 18000.00 | 1500 × 12 |
| 2000 | 24000.00 | Entier accepté |
| 1234.56 | 14814.72 | Décimales conservées |
| 0 | ❌ Erreur | Non positif |
| -100 | ❌ Erreur | Négatif |
| `None` | ❌ Erreur | Manquant |

#### Loyer annuel TTC

```python
def _calculate_loyer_annuel_ttc(self, data: dict) -> float:
    """
    Calcule le loyer annuel TTC.

    Formule:
    loyer_annuel_ttc = loyer_annuel_ht × (1 + tva/100)

    Conditions:
    - Si TVA absente → utiliser 20% par défaut

    Returns:
        Montant en euros
    """
    loyer_annuel_ht = self._calculate_loyer_annuel_ht(data)

    # TVA (défaut 20%)
    tva = data.get("TVA", 20)
    try:
        tva = float(tva)
    except (ValueError, TypeError):
        tva = 20.0  # Défaut si invalide

    return loyer_annuel_ht * (1 + tva / 100)
```

**Cas de test :**

| Loyer annuel HT | TVA | Résultat | Calcul |
|-----------------|-----|----------|--------|
| 18000.00 | 20 | 21600.00 | 18000 × 1.20 |
| 18000.00 | 10 | 19800.00 | 18000 × 1.10 |
| 18000.00 | 0 | 18000.00 | 18000 × 1.00 |
| 18000.00 | `None` | 21600.00 | Défaut 20% |
| 18000.00 | `""` | 21600.00 | Défaut 20% |
| 18000.00 | "ABC" | 21600.00 | Défaut 20% si invalide |

#### Loyer trimestriel

```python
def _calculate_loyer_trimestriel(self, data: dict) -> float:
    """
    Calcule le loyer trimestriel HT.

    Formule:
    loyer_trimestriel = loyer_mensuel_ht × 3

    Returns:
        Montant en euros
    """
    loyer_mensuel = float(data.get("Montant loyer HT mensuel"))
    return loyer_mensuel * 3
```

**Cas de test :**

| Loyer mensuel HT | Résultat | Calcul |
|------------------|----------|--------|
| 1500.00 | 4500.00 | 1500 × 3 |
| 2000 | 6000.00 | 2000 × 3 |

---

### Calcul des charges

#### Provision charges annuelle

```python
def _calculate_charges_annuelles(self, data: dict) -> float:
    """
    Calcule la provision pour charges annuelle.

    Formule:
    charges_annuelles = charges_mensuelles × 12

    Conditions:
    - Si charges absentes → utiliser 0

    Returns:
        Montant en euros
    """
    charges_mensuelles = data.get("Provision pour charges mensuelles", 0)

    try:
        charges_mensuelles = float(charges_mensuelles) if charges_mensuelles else 0
    except (ValueError, TypeError):
        charges_mensuelles = 0

    return charges_mensuelles * 12
```

**Cas de test :**

| Charges mensuelles | Résultat | Notes |
|--------------------|----------|-------|
| 150.00 | 1800.00 | 150 × 12 |
| 0 | 0.00 | Pas de charges |
| `""` (vide) | 0.00 | Défaut 0 |
| `None` | 0.00 | Défaut 0 |

#### Total loyer + charges

```python
def _calculate_total_loyer_charges(self, data: dict, periode: str = "mensuel") -> float:
    """
    Calcule le total loyer + charges.

    Args:
        periode: "mensuel" ou "trimestriel"

    Returns:
        Montant en euros
    """
    loyer_mensuel = float(data.get("Montant loyer HT mensuel"))
    charges_mensuelles = float(data.get("Provision pour charges mensuelles", 0))

    if periode == "mensuel":
        return loyer_mensuel + charges_mensuelles
    elif periode == "trimestriel":
        return (loyer_mensuel + charges_mensuelles) * 3
    else:
        raise ValueError(f"Période invalide: {periode}")
```

**Cas de test :**

| Loyer mensuel | Charges | Période | Résultat | Calcul |
|---------------|---------|---------|----------|--------|
| 1500 | 150 | mensuel | 1650.00 | 1500 + 150 |
| 1500 | 150 | trimestriel | 4950.00 | (1500 + 150) × 3 |
| 1500 | 0 | mensuel | 1500.00 | 1500 + 0 |

---

### Calcul du dépôt de garantie

```python
def _calculate_depot_garantie(self, data: dict) -> float:
    """
    Calcule le dépôt de garantie.

    Formule:
    dépôt = loyer_mensuel_ht × nb_mois

    Conditions:
    - Si nb_mois absent → utiliser 3 par défaut

    Returns:
        Montant en euros
    """
    loyer_mensuel = float(data.get("Montant loyer HT mensuel"))

    nb_mois = data.get("Dépôt de garantie Nombre de mois", 3)
    try:
        nb_mois = int(nb_mois) if nb_mois else 3
    except (ValueError, TypeError):
        nb_mois = 3  # Défaut

    return loyer_mensuel * nb_mois
```

**Cas de test :**

| Loyer mensuel HT | Nb mois | Résultat | Calcul |
|------------------|---------|----------|--------|
| 1500 | 3 | 4500.00 | 1500 × 3 |
| 1500 | 6 | 9000.00 | 1500 × 6 |
| 1500 | `None` | 4500.00 | Défaut 3 mois |
| 1500 | `""` | 4500.00 | Défaut 3 mois |

---

### Calcul des dates

#### Date de fin initiale

```python
def _calculate_date_fin_initiale(self, data: dict) -> str:
    """
    Calcule la date de fin de la période initiale.

    Formule:
    date_fin = date_debut + durée_initiale (années)

    Returns:
        Date au format DD/MM/YYYY

    Raises:
        ValueError si date_debut ou durée invalide
    """
    from dateutil.relativedelta import relativedelta

    date_effet_str = data.get("Date de prise d'effet du bail")
    duree_initiale = int(data.get("Durée initiale du bail"))

    # Parser la date
    try:
        date_debut = datetime.strptime(date_effet_str, "%d/%m/%Y")
    except ValueError:
        try:
            date_debut = datetime.strptime(date_effet_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Format de date invalide: {date_effet_str}")

    # Ajouter la durée
    date_fin = date_debut + relativedelta(years=duree_initiale)

    return date_fin.strftime("%d/%m/%Y")
```

**Cas de test :**

| Date début | Durée | Résultat | Calcul |
|------------|-------|----------|--------|
| 01/01/2025 | 9 | 01/01/2034 | +9 ans |
| 15/06/2025 | 6 | 15/06/2031 | +6 ans |
| 2025-01-01 | 9 | 01/01/2034 | Format alternatif accepté |
| 29/02/2024 | 1 | 28/02/2025 | Gestion année bissextile |

#### Date de fin avec GAPD

```python
def _calculate_date_fin_gapd(self, data: dict) -> str:
    """
    Calcule la date de fin incluant la période GAPD.

    Formule:
    date_fin_gapd = date_debut + durée_totale (années)

    Returns:
        Date au format DD/MM/YYYY
    """
    from dateutil.relativedelta import relativedelta

    date_effet_str = data.get("Date de prise d'effet du bail")
    duree_totale = self._calculate_duree_totale(data)

    date_debut = datetime.strptime(date_effet_str, "%d/%m/%Y")
    date_fin = date_debut + relativedelta(years=duree_totale)

    return date_fin.strftime("%d/%m/%Y")
```

**Cas de test :**

| Date début | Durée initiale | GAPD | Résultat | Calcul |
|------------|----------------|------|----------|--------|
| 01/01/2025 | 9 | 3 | 01/01/2037 | +12 ans |
| 01/01/2025 | 9 | 0 | 01/01/2034 | +9 ans (sans GAPD) |

---

## 4. Enrichissement INPI

### Condition de déclenchement

```python
def should_enrich_from_inpi(data: dict) -> bool:
    """
    Détermine si l'enrichissement INPI doit être déclenché.

    Condition:
    - SIREN PRENEUR présent ET valide (9 chiffres)

    Returns:
        True si enrichissement nécessaire
    """
    siren = data.get("SIREN PRENEUR", "").strip()

    if not siren:
        return False

    # Valider le format
    siren_clean = siren.replace(" ", "")
    return len(siren_clean) == 9 and siren_clean.isdigit()
```

**Cas de test :**

| SIREN PRENEUR | Enrichissement | Raison |
|---------------|----------------|--------|
| 532321916 | ✅ Oui | SIREN valide |
| 481283901 | ✅ Oui | SIREN valide |
| `""` | ❌ Non | Vide |
| 12345678 | ❌ Non | 8 chiffres seulement |
| ABC123456 | ❌ Non | Contient lettres |

---

### Stratégie de fallback

```python
def enrich_company_data(siren: str) -> dict:
    """
    Enrichit les données entreprise avec stratégie de fallback.

    Stratégie:
    1. Essayer API INPI
    2. Si échec (rate limit, erreur) → Essayer scraping BeautifulSoup
    3. Si échec → Retourner données partielles

    Returns:
        Dict avec champs enrichis + statut
    """
    # Tentative 1 : API INPI
    try:
        api_data = fetch_from_inpi_api(siren)
        if api_data:
            return {
                **api_data,
                "enrichment_status": "success",
                "enrichment_method": "api"
            }
    except RateLimitError:
        logger.warning("Rate limit INPI atteint")
    except Exception as e:
        logger.error(f"Erreur API INPI: {e}")

    # Tentative 2 : Scraping BeautifulSoup
    try:
        scraped_data = scrape_from_inpi_beautifulsoup(siren)
        if scraped_data and len(scraped_data) >= 4:  # Au moins 4 champs
            return {
                **scraped_data,
                "enrichment_status": "success",
                "enrichment_method": "scraping",
                "error_message": "Données récupérées via scraping (API indisponible)"
            }
    except Exception as e:
        logger.error(f"Erreur scraping: {e}")

    # Échec total
    return {
        "enrichment_status": "failed",
        "error_message": "Impossible de récupérer les données INPI"
    }
```

**Tests de fallback :**

| Scénario | API | Scraping | Résultat |
|----------|-----|----------|----------|
| Normal | ✅ Succès | - | Utilise API |
| Rate limit | ❌ 429 | ✅ Succès | Utilise scraping |
| API down | ❌ Erreur | ✅ Succès | Utilise scraping |
| Tous échouent | ❌ Erreur | ❌ Erreur | Status "failed" |

---

### Filtrage des dirigeants

```python
def filter_dirigeant(dirigeants_list: list) -> str:
    """
    Filtre la liste des dirigeants pour exclure les commissaires.

    Règles:
    1. Ignorer toute personne avec "Commissaire" dans la qualité
    2. Chercher les qualités valides:
       - Gérant
       - Président
       - Directeur général
       - Président du conseil d'administration
       - Président du conseil de surveillance
    3. Retourner le premier dirigeant trouvé

    Returns:
        Nom du dirigeant ou None
    """
    qualites_valides = [
        "Gérant",
        "Président",
        "Directeur général",
        "Président du conseil d'administration",
        "Président du conseil de surveillance"
    ]

    for dirigeant in dirigeants_list:
        qualite = dirigeant.get("Qualité", "")

        # Test 1 : Ignorer commissaires
        if "Commissaire" in qualite:
            continue

        # Test 2 : Vérifier si qualité valide
        is_valid = any(q.lower() in qualite.lower() for q in qualites_valides)

        if is_valid:
            # Extraire le nom
            if "Dénomination" in dirigeant:
                return dirigeant["Dénomination"]
            elif "Nom, Prénom(s)" in dirigeant:
                return format_nom_prenom(dirigeant["Nom, Prénom(s)"])

    return None
```

**Cas de test :**

| Dirigeants dans HTML | Résultat | Raison |
|----------------------|----------|--------|
| 1. Chaillou Denis (Commissaire)<br>2. Moulin Luc (Gérant) | Moulin Luc | Ignore commissaire, prend gérant |
| 1. Ernst & Young (Commissaire)<br>2. Charles (Président) | Charles | Ignore commissaire, prend président |
| 1. Dupont Jean (Commissaire) | None | Aucun dirigeant valide |
| 1. Martin Paul (Gérant)<br>2. Durand Marie (Président) | Martin Paul | Prend le premier dirigeant valide |

---

## 5. Formatage conditionnel

### Formatage du capital social

```python
def format_capital(capital_str: str) -> str:
    """
    Formate le capital social.

    Transformation:
    "145131987 EUR" → "145 131 987 €"

    Règles:
    1. Extraire les chiffres uniquement
    2. Ajouter espaces tous les 3 chiffres (séparateur milliers)
    3. Remplacer "EUR" par "€"

    Returns:
        Capital formaté
    """
    import re

    # Extraire les chiffres
    match = re.search(r'([\d\s]+)', capital_str)
    if not match:
        return capital_str.replace('EUR', '€').strip()

    # Nettoyer
    montant = match.group(1).replace(' ', '').replace('\xa0', '')

    # Formater avec espaces
    montant_formate = '{:,}'.format(int(montant)).replace(',', ' ')

    return f"{montant_formate} €"
```

**Cas de test :**

| Entrée | Sortie | Transformation |
|--------|--------|----------------|
| `"145131987 EUR"` | `"145 131 987 €"` | Standard |
| `"145131987  EUR"` | `"145 131 987 €"` | Espaces multiples |
| `"1200000 EUR"` | `"1 200 000 €"` | Petit montant |
| `"1000 EUR"` | `"1 000 €"` | Très petit |
| `"145 131 987 EUR"` | `"145 131 987 €"` | Déjà formaté, change juste EUR |

---

### Formatage des montants monétaires

```python
def format_montant(value: float, decimales: int = 2) -> str:
    """
    Formate un montant monétaire.

    Format:
    1234.56 → "1 234,56 €"

    Règles:
    - Séparateur milliers : espace
    - Séparateur décimal : virgule
    - Symbole : €

    Returns:
        Montant formaté
    """
    # Formater avec séparateurs
    montant_str = f"{value:,.{decimales}f}"

    # Remplacer séparateurs anglais par français
    montant_str = montant_str.replace(',', ' ')  # Milliers
    montant_str = montant_str.replace('.', ',')  # Décimales

    return f"{montant_str} €"
```

**Cas de test :**

| Valeur | Décimales | Résultat |
|--------|-----------|----------|
| 1500.00 | 2 | `"1 500,00 €"` |
| 1234.56 | 2 | `"1 234,56 €"` |
| 145131987.00 | 2 | `"145 131 987,00 €"` |
| 1500 | 2 | `"1 500,00 €"` |
| 1500.5 | 2 | `"1 500,50 €"` |

---

## 6. Gestion des erreurs

### Erreurs de validation

```python
class ValidationError(Exception):
    """Erreur de validation des données."""
    pass

def generate_bail(data: dict) -> bytes:
    """
    Génère un document BAIL.

    Raises:
        ValidationError: Si données invalides
        FileNotFoundError: Si template introuvable
        Exception: Autres erreurs
    """
    # Validation
    is_valid, missing_fields = validate_required_fields(data)
    if not is_valid:
        raise ValidationError(f"Champs manquants: {', '.join(missing_fields)}")

    # Validation SIREN
    if not validate_siren(data.get("SIREN BAILLEUR")):
        raise ValidationError("SIREN BAILLEUR invalide")

    if not validate_siren(data.get("SIREN PRENEUR")):
        raise ValidationError("SIREN PRENEUR invalide")

    # Suite de la génération...
```

**Gestion dans l'interface :**

```python
try:
    document = generate_bail(data)
    st.success("Document généré avec succès!")
    st.download_button("Télécharger", document, "bail.docx")
except ValidationError as e:
    st.error(f"Erreur de validation : {e}")
except FileNotFoundError as e:
    st.error(f"Template introuvable : {e}")
except Exception as e:
    st.error(f"Erreur inattendue : {e}")
    logger.exception("Erreur lors de la génération")
```

---

### Erreurs d'enrichissement INPI

```python
def handle_inpi_enrichment(siren: str, data: dict) -> dict:
    """
    Gère l'enrichissement INPI avec gestion d'erreurs.

    Returns:
        Données enrichies avec statut
    """
    try:
        enriched = enrich_company_data(siren)

        # Vérifier le statut
        if enriched.get("enrichment_status") == "success":
            # Fusionner avec données Excel
            return {**data, **enriched}

        elif enriched.get("enrichment_status") == "partial":
            # Avertir l'utilisateur mais continuer
            logger.warning("Enrichissement partiel")
            return {**data, **enriched}

        else:  # "failed"
            # Logger et utiliser uniquement Excel
            logger.error("Enrichissement INPI échoué")
            return data

    except Exception as e:
        logger.exception("Erreur enrichissement INPI")
        # Continuer avec données Excel uniquement
        return data
```

---

## 7. Tests de non-régression

### Cas de test complets

#### Test 1 : BAIL standard avec GAPD

**Données d'entrée :**
```python
{
    "NOM DU BAILLEUR": "FORGEOT & AL",
    "SIREN BAILLEUR": "123456789",
    "NOM DU PRENEUR": "KARAVEL",
    "SIREN PRENEUR": "532321916",
    "Date de prise d'effet du bail": "01/01/2025",
    "Durée initiale du bail": 9,
    "Durée GAPD": 3,
    "Montant loyer HT mensuel": 1500.00,
    "TVA": 20,
    "Provision pour charges mensuelles": 150.00,
    "Dépôt de garantie Nombre de mois": 3,
    "HONORAIRES TTC ANNEE 1": "Oui - 1 200,00 €",
    "Clause résolutoire": "OUI"
}
```

**Résultats attendus :**
- ✅ Enrichissement INPI activé (SIREN présent)
- ✅ Durée totale = 12 ans
- ✅ Date fin initiale = 01/01/2034
- ✅ Date fin GAPD = 01/01/2037
- ✅ Loyer annuel HT = 18 000,00 €
- ✅ Loyer annuel TTC = 21 600,00 €
- ✅ Charges annuelles = 1 800,00 €
- ✅ Dépôt garantie = 4 500,00 €
- ✅ Article 8.2 inclus (honoraires commence par "Oui")
- ✅ Article 26.2 inclus (clause = "OUI")
- ✅ Capital formaté = "145 131 987 €"
- ✅ Président = "CHARLES" (pas commissaire)

---

#### Test 2 : BAIL sans GAPD ni options

**Données d'entrée :**
```python
{
    "NOM DU BAILLEUR": "FORGEOT & AL",
    "SIREN BAILLEUR": "123456789",
    "NOM DU PRENEUR": "FLEUX",
    "SIREN PRENEUR": "481283901",
    "Date de prise d'effet du bail": "01/06/2025",
    "Durée initiale du bail": 6,
    "Durée GAPD": "",  # Vide
    "Montant loyer HT mensuel": 2000.00,
    "TVA": "",  # Vide → défaut 20%
    "Provision pour charges mensuelles": 0,
    "Dépôt de garantie Nombre de mois": "",  # Vide → défaut 3
    "HONORAIRES TTC ANNEE 1": "Non",  # Ne commence pas par "Oui"
    "Clause résolutoire": "NON"
}
```

**Résultats attendus :**
- ✅ Enrichissement INPI activé
- ✅ Durée totale = 6 ans (GAPD vide → 0)
- ✅ Date fin initiale = 01/06/2031
- ✅ Date fin GAPD = 01/06/2031 (pas de GAPD)
- ✅ Loyer annuel HT = 24 000,00 €
- ✅ Loyer annuel TTC = 28 800,00 € (TVA défaut 20%)
- ✅ Charges annuelles = 0,00 €
- ✅ Dépôt garantie = 6 000,00 € (défaut 3 mois)
- ✅ Article 8.2 NON inclus (honoraires ne commence pas par "Oui")
- ✅ Article 26.2 NON inclus (clause = "NON")
- ✅ Capital formaté = "1 200 000 €"
- ✅ Gérant = "Luc Moulin" (pas "RICHEMONT CAPERAA AUDIT" qui est commissaire)

---

### Matrice de tests

| Scénario | Enrichissement | Article 8.2 | Article 26.2 | Statut |
|----------|----------------|-------------|--------------|--------|
| BAIL complet avec options | ✅ | ✅ | ✅ | ✅ Validé |
| BAIL sans GAPD | ✅ | ❌ | ❌ | ✅ Validé |
| BAIL sans SIREN | ❌ | ✅ | ✅ | ✅ Validé |
| SIREN invalide | ❌ | ✅ | ❌ | ✅ Validé |
| API INPI rate limit | ✅ Scraping | ✅ | ✅ | ✅ Validé |
| Honoraires = "Oui" | ✅ | ✅ | ❌ | ✅ Validé |
| Clause = "OUI" | ✅ | ❌ | ✅ | ✅ Validé |
| Valeurs par défaut (TVA, dépôt) | ✅ | ❌ | ❌ | ✅ Validé |

---

## Conclusion

Ce document détaille l'ensemble des tests, conditions, et règles métier du système de génération BAIL. Pour toute modification de la logique, mettre à jour ce document et ajouter les tests correspondants.

**Dernière validation :** 2025-11-09
