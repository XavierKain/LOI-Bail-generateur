# Documentation du Système de Génération de BAIL

## Date de création
2025-11-09

## Vue d'ensemble

Ce système génère automatiquement des documents de bail commercial (BAIL) à partir de données Excel enrichies avec les informations INPI (Institut National de la Propriété Industrielle).

## Architecture du système

### 1. Fichiers principaux

#### Application Streamlit
- **[app.py](app.py)** : Interface utilisateur principale
  - Navigation entre LOI et BAIL
  - Upload de fichiers Excel
  - Génération et téléchargement des documents

#### Modules core
- **[modules/excel_parser.py](modules/excel_parser.py)** : Lecture et parsing des données Excel
- **[modules/inpi_client.py](modules/inpi_client.py)** : Enrichissement des données entreprise via INPI
- **[modules/document_generator_bail.py](modules/document_generator_bail.py)** : Génération du document BAIL Word

#### Templates
- **[Template BAIL avec placeholder.docx](Template BAIL avec placeholder.docx)** : Template Word avec placeholders

#### Fichiers de données
- **[Redaction BAIL.xlsx](Redaction BAIL.xlsx)** : Fichier Excel source avec onglet "Liste données BAIL"

### 2. Flux de traitement

```
1. Upload Excel
   ↓
2. Parse onglet "Liste données BAIL"
   ↓
3. Enrichissement INPI (si SIREN fourni)
   ↓
4. Calculs et conditions logiques
   ↓
5. Remplacement des placeholders
   ↓
6. Génération document Word final
```

## Fonctionnalités principales

### 1. Enrichissement INPI

#### Architecture en 3 niveaux

1. **API INPI** (prioritaire)
   - Authentification OAuth2
   - Endpoint : `https://registre-national-entreprises.inpi.fr/api/`
   - Rate limit : 5 requêtes/minute (configuré localement)
   - Récupère tous les champs si disponible

2. **Scraping BeautifulSoup** (fallback automatique)
   - Compatible Streamlit Cloud
   - Utilisé si API rate limit (429) ou indisponible
   - HTML parsing sans JavaScript
   - Récupère tous les 6 champs requis

3. **Playwright** (non utilisé sur Streamlit Cloud)
   - Headless browser avec JavaScript
   - Nécessite Chromium (incompatible Streamlit Cloud)
   - Code conservé pour usage local

#### Champs enrichis

| Champ | Source | Format |
|-------|--------|--------|
| NOM DE LA SOCIETE | H1 de la page | Texte brut |
| TYPE DE SOCIETE | Label "Forme juridique" + sibling | Ex: "SASU, Société par actions..." |
| CAPITAL SOCIAL | Label "Capital social" + sibling | Format: "145 131 987 €" |
| ADRESSE DE DOMICILIATION | Label "Adresse du siège" + sibling | Adresse complète |
| LOCALITE RCS | Extraite de l'adresse | Ex: "PARIS" |
| PRESIDENT DE LA SOCIETE | Section "Gestion et Direction" | Nom complet du dirigeant |

#### Filtrage des dirigeants

Le système filtre automatiquement pour ne retourner que les vrais dirigeants :

**Qualités acceptées :**
- Gérant
- Président
- Directeur général
- Président du conseil d'administration
- Président du conseil de surveillance

**Qualités ignorées :**
- Commissaire aux comptes titulaire
- Commissaire aux comptes suppléant

#### Formatage spécial

**Capital social :**
```python
# Entrée : "145131987 EUR" ou "145131987  EUR"
# Sortie : "145 131 987 €"

# Logique :
1. Extraire les chiffres avec regex
2. Supprimer tous les espaces/caractères spéciaux
3. Formater avec {:,} puis remplacer , par espace
4. Ajouter symbole €
```

### 2. Parsing Excel

#### Structure attendue

**Onglet : "Liste données BAIL"**

Format à 2 colonnes :
```
| Nom du champ           | Valeur       |
|------------------------|--------------|
| NOM DU BAILLEUR        | FORGEOT & AL |
| SIREN BAILLEUR         | 123456789    |
| ...                    | ...          |
```

#### Extraction

```python
# Colonne A = Noms des champs
# Colonne B = Valeurs correspondantes
# Retourne un dictionnaire {champ: valeur}
```

### 3. Conditions logiques et calculs

#### Articles conditionnels

##### Article 8.2 - Charges et Impôts
```python
if "Oui" in data.get("HONORAIRES TTC ANNEE 1", ""):
    inclure_article_8_2 = True
```

##### Article 26.2 - Clause résolutoire
```python
if data.get("Clause résolutoire", "").strip().upper() == "OUI":
    inclure_article_26_2 = True
```

#### Calculs automatiques

##### Durée totale du bail
```python
duree_initiale = int(data.get("Durée initiale du bail", 0))
duree_gapd = int(data.get("Durée GAPD", 0))
duree_totale = duree_initiale + duree_gapd
```

##### Calculs de loyers

**Loyer annuel HT :**
```python
loyer_mensuel_ht = float(data.get("Montant loyer HT mensuel"))
loyer_annuel_ht = loyer_mensuel_ht * 12
```

**Loyer annuel TTC :**
```python
loyer_annuel_ht = float(...)
tva = float(data.get("TVA", "20"))
loyer_annuel_ttc = loyer_annuel_ht * (1 + tva / 100)
```

**Loyer trimestriel :**
```python
loyer_mensuel = float(...)
loyer_trimestriel = loyer_mensuel * 3
```

##### Charges

**Provision charges annuelle :**
```python
charges_mensuelles = float(data.get("Provision pour charges mensuelles"))
charges_annuelles = charges_mensuelles * 12
```

**Total loyer + charges :**
```python
total_mensuel = loyer_mensuel + charges_mensuelles
total_trimestriel = loyer_trimestriel + (charges_mensuelles * 3)
```

##### Dépôt de garantie

```python
# Nombre de mois configuré dans Excel
nb_mois = int(data.get("Dépôt de garantie Nombre de mois", 3))
loyer_mensuel_ht = float(...)
depot_garantie = loyer_mensuel_ht * nb_mois
```

#### Dates

**Date de prise d'effet :**
```python
date_effet = data.get("Date de prise d'effet du bail")
# Format attendu : "01/01/2025" ou datetime
```

**Date de fin initiale :**
```python
from dateutil.relativedelta import relativedelta

date_debut = datetime.strptime(date_effet, "%d/%m/%Y")
duree_initiale = int(data.get("Durée initiale du bail"))
date_fin = date_debut + relativedelta(years=duree_initiale)
date_fin_str = date_fin.strftime("%d/%m/%Y")
```

**Date de fin avec GAPD :**
```python
duree_totale = duree_initiale + duree_gapd
date_fin_gapd = date_debut + relativedelta(years=duree_totale)
```

### 4. Section Signatures

Le template contient une table de signatures avec les présidents :

```
┌─────────────────────────┬─────────────────────────┐
│      Le Bailleur        │       Le Preneur        │
├─────────────────────────┼─────────────────────────┤
│ Monsieur Maxime FORGEOT │ [PRESIDENT DE LA SOCIETE]│
└─────────────────────────┴─────────────────────────┘
```

**Le Bailleur :** Toujours "Monsieur Maxime FORGEOT" (hardcodé)
**Le Preneur :** Récupéré via enrichissement INPI

## Gestion des erreurs

### Enrichissement INPI

#### Statuts d'enrichissement

| Statut | Description | Action |
|--------|-------------|--------|
| `success` | Tous les champs récupérés | Utiliser les données INPI |
| `partial` | Certains champs manquants | Combiner INPI + Excel |
| `failed` | Enrichissement échoué | Utiliser uniquement Excel |

#### Rate limit

```python
# Si API retourne 429
→ Fallback automatique sur scraping BeautifulSoup
→ Log : "Rate limit INPI atteint"
→ Log : "Données récupérées via scraping (API indisponible)"
```

#### Logs types

**Succès API :**
```
INFO: Recherche INPI pour SIREN: 123456789
INFO: Authentification INPI réussie
INFO: Enrichissement INPI réussi pour SOCIETE XYZ
```

**Fallback scraping :**
```
WARNING: Rate limit INPI atteint
INFO: API INPI non disponible, tentative de scraping BeautifulSoup...
INFO: Scraping BeautifulSoup complet pour SIREN 123456789
INFO: Scraping BeautifulSoup réussi: 6 champs récupérés
```

### Validation des données

#### Champs requis

Avant génération, vérifier :
- Date de prise d'effet
- Durée initiale du bail
- Montant loyer HT mensuel
- SIREN du preneur (si enrichissement souhaité)

#### Valeurs par défaut

```python
# Si champ manquant, utiliser valeur par défaut
tva = data.get("TVA", "20")  # 20% par défaut
depot_garantie_mois = data.get("Dépôt de garantie Nombre de mois", "3")
```

## Performance

### Temps de traitement

| Étape | Temps moyen |
|-------|-------------|
| Parsing Excel | < 1s |
| Enrichissement INPI (API) | 1-2s |
| Enrichissement INPI (scraping) | 8-12s |
| Génération document | < 1s |
| **Total (API)** | **2-4s** |
| **Total (scraping)** | **9-14s** |

### Cache

- **API INPI** : Cache LRU avec `@lru_cache(maxsize=100)`
- **Durée** : Session Streamlit (jusqu'au restart)

## Déploiement

### Streamlit Cloud

**Configuration requise :**
```toml
[server]
maxUploadSize = 10

[theme]
primaryColor = "#0066CC"
```

**Dépendances :**
```
streamlit
python-docx
openpyxl
pandas
requests
beautifulsoup4
python-dateutil
```

**Dépendances optionnelles (non requises sur Streamlit Cloud) :**
```
playwright  # Pour tests locaux uniquement
```

### Variables d'environnement

Aucune configuration requise - le système fonctionne sans authentification INPI (fallback automatique sur scraping).

## Tests

### Tests disponibles

- **[test_beautifulsoup_fallback.py](test_beautifulsoup_fallback.py)** : Test complet du fallback
- **[test_beautifulsoup_all_fields.py](test_beautifulsoup_all_fields.py)** : Test extraction de tous les champs
- **[test_signature_complete.py](test_signature_complete.py)** : Test signatures avec présidents

### Exécution

```bash
# Test du scraping BeautifulSoup
python3 test_beautifulsoup_fallback.py

# Test avec SIREN spécifique
python3 -c "
from modules.inpi_client import INPIClient
inpi = INPIClient()
data = inpi.get_company_info('532321916')
print(data)
"
```

### Cas de test validés

| SIREN | Société | Dirigeant attendu | Statut |
|-------|---------|-------------------|--------|
| 532321916 | KARAVEL | CHARLES | ✅ |
| 481283901 | FLEUX | Luc Moulin (Gérant) | ✅ |

## Maintenance

### Logs

Les logs sont disponibles dans la console Streamlit :
```python
import logging
logger = logging.getLogger(__name__)

# Niveaux utilisés
logger.info(...)    # Informations générales
logger.warning(...) # Avertissements (rate limit, etc.)
logger.error(...)   # Erreurs
logger.debug(...)   # Debug (désactivé par défaut)
```

### Mise à jour du template

Pour modifier le template Word :
1. Ouvrir **Template BAIL avec placeholder.docx**
2. Utiliser les placeholders entre crochets : `[NOM_DU_CHAMP]`
3. Sauvegarder
4. Tester avec l'application

### Ajout de nouveaux champs

1. Ajouter le champ dans l'onglet Excel "Liste données BAIL"
2. Ajouter le placeholder dans le template Word
3. Ajouter la logique de calcul dans [modules/document_generator_bail.py](modules/document_generator_bail.py)
4. Tester

## Historique des modifications

### 2025-11-09 : Implémentation complète

#### Enrichissement INPI
- ✅ Fallback BeautifulSoup complet (6 champs)
- ✅ Filtrage des commissaires aux comptes
- ✅ Formatage du capital social : "145 131 987 €"
- ✅ Compatible Streamlit Cloud

#### Template BAIL
- ✅ Ajout section signatures avec présidents
- ✅ Support Article 8.2 conditionnel (charges)
- ✅ Support Article 26.2 conditionnel (clause résolutoire)

#### Calculs
- ✅ Durée totale (initiale + GAPD)
- ✅ Loyers annuels HT/TTC
- ✅ Loyers trimestriels
- ✅ Provisions charges
- ✅ Dépôt de garantie
- ✅ Dates de fin de bail

## Support

Pour toute question ou problème :
1. Consulter les logs dans la console Streamlit
2. Vérifier le format du fichier Excel
3. Tester avec les SIREN de test (532321916, 481283901)
4. Vérifier que le template Word contient les bons placeholders

## Références

- [API INPI Documentation](https://data.inpi.fr/api/documentation)
- [python-docx Documentation](https://python-docx.readthedocs.io/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
