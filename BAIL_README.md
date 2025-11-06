# Générateur de BAIL Commercial

## Statut
**Production Ready** ✅

Le générateur de BAIL est maintenant fonctionnel et prêt à être testé avec des données réelles.

## Fichiers créés

### Modules Python
- **[modules/bail_generator.py](modules/bail_generator.py)** - Générateur de contenu avec logique conditionnelle
- **[modules/bail_word_generator.py](modules/bail_word_generator.py)** - Générateur de documents Word
- **[modules/__init__.py](modules/__init__.py)** - Export des modules BAIL

### Templates et Configuration
- **[Template BAIL avec placeholder.docx](Template%20BAIL%20avec%20placeholder.docx)** - Template Word avec 19 placeholders
- **[Redaction BAIL.xlsx](Redaction%20BAIL.xlsx)** - Règles conditionnelles et textes (fourni par l'utilisateur)

### Interface Streamlit
- **[app_bail.py](app_bail.py)** - Application Streamlit dédiée au BAIL

### Tests
- **[test_bail_generator.py](test_bail_generator.py)** - Tests unitaires du générateur
- **[create_test_bail_excel.py](create_test_bail_excel.py)** - Génère un fichier Excel de test
- **[Test_Donnees_BAIL.xlsx](Test_Donnees_BAIL.xlsx)** - Fichier Excel de test

### Documentation
- **[BAIL_ALGORITHM.md](BAIL_ALGORITHM.md)** - Documentation complète de l'algorithme
- **BAIL_README.md** (ce fichier) - Guide d'utilisation

## Comment utiliser

### Option 1: Via Streamlit (Recommandé)

1. Lancer l'application BAIL:
```bash
python3 -m streamlit run app_bail.py --server.port 8503
```

2. Ouvrir dans le navigateur: http://localhost:8503

3. Uploader un fichier Excel avec les données BAIL (voir format ci-dessous)

4. Vérifier les données extraites

5. Cliquer sur "Générer le document BAIL"

6. Télécharger le fichier DOCX généré

### Option 2: Via Python (Programmation)

```python
from modules import BailGenerator, BailWordGenerator

# 1. Préparer les données
donnees = {
    "Nom Preneur": "Jean DUPONT",
    "Type Preneur": "SAS",
    "Société Bailleur": "SCI FORGEOT PROPERTY",
    "Durée Bail": 9,
    "Montant du loyer": 120000,
    # ... autres variables
}

# 2. Générer les articles
generator = BailGenerator("Redaction BAIL.xlsx")
articles = generator.generer_bail(donnees)

# 3. Créer le document Word
donnees_complete = generator.calculer_variables_derivees(donnees)
word_gen = BailWordGenerator("Template BAIL avec placeholder.docx")
word_gen.generer_document(articles, donnees_complete, "output/BAIL.docx")
```

## Format du fichier Excel d'entrée

Le fichier Excel doit contenir un onglet nommé **"Liste"** avec 2 colonnes:

| Variable | Valeur |
|----------|--------|
| Nom Preneur | Jean DUPONT |
| Type Preneur | SAS |
| Société Bailleur | SCI FORGEOT PROPERTY |
| Durée Bail | 9 |
| Montant du loyer | 120000 |
| ... | ... |

**Exemple**: [Test_Donnees_BAIL.xlsx](Test_Donnees_BAIL.xlsx)

## Variables requises

### Informations de base (15 variables)
- Nom Preneur
- Type Preneur (Personne physique, SAS, SARL, EURL, Société en formation)
- Siret Preneur
- Société Bailleur
- Ville ou arrondissement
- Numéro et rue
- Date LOI
- Enseigne
- Statut Locaux loués
- Destination
- Durée Bail
- Durée ferme Bail
- Date prise d'effet
- Surface totale
- Surface RDC

### Conditions suspensives (0-4 variables)
- Condition suspensive 1
- Condition suspensive 2
- Condition suspensive 3
- Condition suspensive 4

### Loyer et finances (13+ variables)
- Montant du loyer
- Loyer année 1 (optionnel, pour paliers)
- Loyer année 2 (optionnel)
- Loyer année 3-6 (optionnels)
- Droit d'entrée (optionnel)
- Accession (Immédiate / Fin de Bail)
- Actualisation (Oui / Non)
- Durée Franchise (optionnel, en mois)
- Participation Travaux
- Remboursement
- Paiement (Prélèvement / Virement)

### Garanties (1-2 variables)
- Durée DG (en mois: 3, 4, ou 6)
- Durée GAPD (optionnel)

### Honoraires (3 variables)
- Broker
- Honoraires Preneur
- Honoraires Bailleur

### Divers (2 variables)
- DPE (A, B, C, D, E, F, G)
- Restauration sans extraction (Oui / Non)

## Articles générés

Le générateur produit **16 articles** avec logique conditionnelle:

| Article | Description | Conditions |
|---------|-------------|-----------|
| **Comparution** | Bailleur et Preneur | Lookup selon Société Bailleur et Type Preneur |
| **Article préliminaire** | Conditions suspensives | Si au moins 1 condition suspensive |
| **Article 1** | Désignation | Toujours |
| **Article 2** | Durée | Toujours (variant si Durée > 9) |
| **Article 3** | Destination | Toujours (+ clause si Restauration) |
| **Article 5.3** | Accession | Selon option Accession |
| **Article 7.1** | Montant du loyer | Toujours |
| **Article 7.2** | Actualisation | Selon Actualisation Oui/Non |
| **Article 7.3** | Paiement | Selon Paiement Prélèvement/Virement |
| **Article 7.6** | Droit d'entrée | Si Droit d'entrée non vide |
| **Article 8** | Garanties | Si DG ou GAPD |
| **Article 19** | Frais et honoraires | Si Honoraires Preneur non vide |
| **Article 22.2** | DPE | Si DPE non vide |
| **Article 26** | Dispositions particulières | Toujours |
| **Article 26.1** | Paliers de loyer | Si Loyer année 1 non vide |
| **Article 26.2** | Franchise de loyer | Si Durée Franchise non vide |

## Variables dérivées (7 calculées automatiquement)

1. **Adresse Locaux Loués** = [Ville] + [Numéro et rue]
2. **Montant du palier X** = [Montant du loyer] - [Loyer année X]
3. **Surface R-1** = [Surface totale] - [Surface RDC]
4. **Type Bail** = "3/6/9" si Durée=9, "6/9/10" si Durée=10
5. **Date de signature** = Date du jour + 15 jours
6. **Montant du DG** = [Montant du loyer] / 12 * [Durée DG]
7. **Période DG** = "quart" si 3 mois, "tiers" si 4, "moitier" si 6

## Architecture technique

### BailGenerator ([modules/bail_generator.py](modules/bail_generator.py))

**Responsabilité**: Logique métier et génération de contenu

**Méthodes clés**:
- `calculer_variables_derivees()` - Calcule 7 variables dérivées
- `evaluer_condition()` - Évalue conditions textuelles (>, =, non vide, etc.)
- `obtenir_texte_article()` - Sélectionne le bon texte selon conditions
- `remplacer_placeholders()` - Remplace [Variable] par valeurs
- `generer_bail()` - Méthode principale, retourne Dict[article_name: texte]

**Formats de conditions supportés**:
```python
"Si [Durée Bail] > 9"
"Si [Actualisation] = 'Oui'"
"Si [Droit d'entrée] non vide"
"Si plusieurs conditions suspensives"
```

### BailWordGenerator ([modules/bail_word_generator.py](modules/bail_word_generator.py))

**Responsabilité**: Génération du document Word final

**Méthodes clés**:
- `generer_document()` - Crée le DOCX final
- `_replace_placeholders_in_paragraph()` - Remplace {{PLACEHOLDER}}
- `_clean_empty_paragraphs()` - Nettoie les paragraphes vides

**Placeholders utilisés**:
```
{{COMPARUTION_BAILLEUR}}
{{COMPARUTION_PRENEUR}}
{{ARTICLE_PRELIMINAIRE}}
{{ARTICLE_1}} à {{ARTICLE_26_2}}
{{VILLE}}
{{DATE_SIGNATURE}}
```

## Tests

### Test unitaire
```bash
python3 test_bail_generator.py
```

**Résultats attendus**: 13-16 articles générés (selon données de test)

### Test via Streamlit
1. Lancer `python3 -m streamlit run app_bail.py --server.port 8503`
2. Uploader `Test_Donnees_BAIL.xlsx`
3. Vérifier les données extraites (33 variables)
4. Générer le document
5. Télécharger et ouvrir le DOCX

## Prochaines étapes

### Améliorations possibles
- [ ] Intégrer dans app.py principal (tabs LOI + BAIL)
- [ ] Ajouter validation des données en amont
- [ ] Enrichissement INPI automatique pour le Preneur
- [ ] Conversion montants en lettres
- [ ] Export PDF automatique
- [ ] Historique des générations

### Intégration avec LOI
L'application principale [app.py](app.py) pourrait être mise à jour pour inclure les deux générateurs dans des tabs séparés:
```python
tab_loi, tab_bail = st.tabs(["📄 LOI", "📜 BAIL"])
```

## Troubleshooting

### Erreur: Template non trouvé
Vérifier que `Template BAIL avec placeholder.docx` existe dans le dossier racine.

### Erreur: Redaction BAIL.xlsx non trouvé
Vérifier que le fichier Excel de configuration est présent.

### Articles manquants
Certains articles sont conditionnels. Vérifier les données:
- Article préliminaire: Nécessite au moins 1 condition suspensive
- Article 7.6: Nécessite un Droit d'entrée
- Article 26.1: Nécessite des paliers de loyer (Loyer année 1)
- Article 26.2: Nécessite une Durée Franchise

### Placeholders non remplacés
Vérifier que les noms de variables correspondent exactement (case-sensitive).
Le système normalise certaines variations automatiquement.

## Contact

Développé par Xavier Kain
Branche: `redaction-bail`
Version: 1.0

---

**Statut**: ✅ Production Ready - Prêt pour tests utilisateur
