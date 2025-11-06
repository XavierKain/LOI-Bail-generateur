"""
Générateur de documents BAIL à partir des données et règles Excel.

Ce module gère la logique complexe de génération des baux commerciaux :
- Calcul des variables dérivées
- Évaluation des conditions
- Sélection des variantes d'articles
- Remplacement des placeholders
"""

import pandas as pd
import re
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
import logging

logger = logging.getLogger(__name__)


class BailGenerator:
    """Générateur de documents BAIL avec logique conditionnelle."""

    def __init__(self, excel_path: str = "Redaction BAIL.xlsx"):
        """
        Initialise le générateur avec les règles depuis Excel.

        Args:
            excel_path: Chemin vers le fichier Excel contenant les règles
        """
        self.excel_path = excel_path
        self.regles_df = None
        self.donnees_df = None
        self._load_rules()

    def _load_rules(self):
        """Charge les règles depuis le fichier Excel."""
        try:
            # Charger l'onglet Rédaction BAIL
            self.regles_df = pd.read_excel(
                self.excel_path,
                sheet_name="Rédaction BAIL"
            )

            # Charger l'onglet Liste données BAIL
            self.donnees_df = pd.read_excel(
                self.excel_path,
                sheet_name="Liste données BAIL"
            )

            logger.info(f"Règles BAIL chargées: {len(self.regles_df)} lignes")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des règles BAIL: {e}")
            raise

    def _normaliser_nom_variable(self, nom: str) -> str:
        """
        Normalise les noms de variables pour gérer les variations.

        Args:
            nom: Nom de variable brut

        Returns:
            Nom normalisé
        """
        # Mapping des variations de noms
        mappings = {
            "Durée du Bail": "Durée Bail",
            "Durée du DG": "Durée DG",
            "Montant Palier 1": "Montant du palier 1",
            "Montant Palier 2": "Montant du palier 2",
            "Montant Palier 3": "Montant du palier 3",
            "Montant du Palier 1": "Montant du palier 1",
            "Montant du Palier 2": "Montant du palier 2",
            "Montant du Palier 3": "Montant du palier 3",
        }

        return mappings.get(nom, nom)

    def calculer_variables_derivees(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule les variables dérivées à partir des données primaires.

        Variables calculées :
        - Adresse Locaux Loués
        - Montants des paliers (1 à 6)
        - Surface R-1
        - Type Bail
        - Date de signature
        - Montant du DG
        - Période DG

        Args:
            donnees: Dictionnaire avec les données primaires

        Returns:
            Dictionnaire avec données primaires + dérivées
        """
        derivees = donnees.copy()

        # Adresse Locaux Loués
        ville = donnees.get("Ville ou arrondissement", "")
        rue = donnees.get("Numéro et rue", "")
        if ville and rue:
            derivees["Adresse Locaux Loués"] = f"{ville}, {rue}"

        # Montants des paliers
        montant_loyer = donnees.get("Montant du loyer")
        if montant_loyer:
            for i in range(1, 7):
                key_annee = f"Loyer année {i}"
                loyer_annee = donnees.get(key_annee)
                if loyer_annee:
                    derivees[f"Montant du palier {i}"] = montant_loyer - loyer_annee

        # Surface R-1
        surface_totale = donnees.get("Surface totale")
        surface_rdc = donnees.get("Surface RDC")
        if surface_totale and surface_rdc:
            derivees["Surface R-1"] = surface_totale - surface_rdc

        # Type Bail
        duree_bail = donnees.get("Durée Bail")
        if duree_bail == 9:
            derivees["Type Bail"] = "3/6/9"
        elif duree_bail == 10:
            derivees["Type Bail"] = "6/9/10"

        # Date de signature (aujourd'hui + 15 jours)
        date_signature = datetime.now() + timedelta(days=15)
        derivees["Date de signature"] = date_signature.strftime("%d/%m/%Y")

        # Montant du DG
        duree_dg = donnees.get("Durée DG")
        if montant_loyer and duree_dg:
            derivees["Montant du DG"] = (montant_loyer / 12) * duree_dg

        # Période DG
        if duree_dg:
            periode_map = {3: "quart", 4: "tiers", 6: "moitier"}
            derivees["Période DG"] = periode_map.get(duree_dg, "")

        logger.debug(f"Variables dérivées calculées: {list(derivees.keys())}")
        return derivees

    def evaluer_condition(self, condition_str: str, donnees: Dict[str, Any]) -> bool:
        """
        Évalue une condition textuelle.

        Exemples de conditions:
        - "Si [Durée Bail] > 9"
        - "Si [Actualisation] = 'Oui'"
        - "Si [Loyer année 1] non vide"
        - "Si plusieurs conditions suspensives"
        - None ou vide → True (pas de condition)

        Args:
            condition_str: Condition en format texte
            donnees: Données pour évaluer la condition

        Returns:
            True si la condition est satisfaite, False sinon
        """
        # Pas de condition = toujours vrai
        if pd.isna(condition_str) or not condition_str:
            return True

        condition = str(condition_str).strip()

        # Cas spécial: "Si plusieurs conditions suspensives"
        if "plusieurs conditions suspensives" in condition.lower():
            count = sum(1 for i in range(1, 5)
                       if donnees.get(f"Condition suspensive {i}"))
            return count > 1

        # Nettoyer les guillemets typographiques
        condition = condition.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")

        # Parser les conditions avec pattern "Si [Variable] opérateur valeur"
        # Pattern: Si [Variable] (=|>|<|>=|<=|!=|supérieur à) valeur
        match_comparison = re.search(
            r'Si\s+"?([^"\[\]]+|[\[][^\]]+[\]])"?\s*(=|>|<|>=|<=|!=|supérieur à|supérieure à)\s*["\']?([^"\']+)["\']?',
            condition,
            re.IGNORECASE
        )

        if match_comparison:
            var_name = match_comparison.group(1).strip().replace('[', '').replace(']', '')
            var_name = self._normaliser_nom_variable(var_name)
            operator = match_comparison.group(2).strip().lower()
            expected_value = match_comparison.group(3).strip()

            actual_value = donnees.get(var_name)

            # Gérer les comparaisons
            try:
                if operator == "=":
                    return str(actual_value).strip() == expected_value
                elif operator == "!=":
                    return str(actual_value).strip() != expected_value
                elif operator in [">", "supérieur à", "supérieure à"]:
                    return float(actual_value) > float(expected_value)
                elif operator == ">=":
                    return float(actual_value) >= float(expected_value)
                elif operator == "<":
                    return float(actual_value) < float(expected_value)
                elif operator == "<=":
                    return float(actual_value) <= float(expected_value)
            except (ValueError, TypeError):
                logger.warning(f"Impossible de comparer {actual_value} avec {expected_value}")
                return False

        # Pattern: Si [Variable] non vide / non nul
        match_nonempty = re.search(
            r'Si\s+\[([^\]]+)\]\s+non\s+(vide|nul)',
            condition,
            re.IGNORECASE
        )

        if match_nonempty:
            var_name = match_nonempty.group(1).strip()
            value = donnees.get(var_name)
            # Considérer comme non vide si value existe et n'est pas None, "", 0, False
            return bool(value) and value != 0

        # Si on ne peut pas parser, logger un warning
        logger.warning(f"Condition non reconnue: {condition}")
        return False

    def obtenir_texte_article(
        self,
        article_name: str,
        designation: Optional[str],
        donnees: Dict[str, Any]
    ) -> Optional[str]:
        """
        Obtient le texte d'un article en évaluant les conditions.

        Args:
            article_name: Nom de l'article (ex: "Comparution")
            designation: Désignation spécifique (ex: "Comparution Bailleur")
            donnees: Données pour évaluer les conditions

        Returns:
            Texte de l'article ou None si non trouvé
        """
        # Filtrer les lignes correspondantes
        mask = self.regles_df['Article'] == article_name
        if designation:
            mask = mask | (self.regles_df['Désignation'] == designation)

        lignes = self.regles_df[mask]

        if lignes.empty:
            logger.warning(f"Aucune règle trouvée pour l'article '{article_name}'")
            return None

        # Parcourir les lignes et évaluer les conditions
        for _, ligne in lignes.iterrows():
            # Vérifier si la donnée source correspond (pour les lookup tables)
            donnee_source = ligne.get('Donnée source')
            nom_source = ligne.get('Nom Source')

            if pd.notna(donnee_source) and pd.notna(nom_source):
                # C'est un lookup: vérifier si la valeur correspond
                valeur_actuelle = donnees.get(nom_source)
                if str(valeur_actuelle) != str(donnee_source):
                    continue  # Passer à la ligne suivante

            # Évaluer Condition Option 1
            condition1 = ligne.get('Condition')
            if self.evaluer_condition(condition1, donnees):
                texte = ligne.get('Entrée correspondante - Option 1')
                if pd.notna(texte):
                    return str(texte)

            # Évaluer Condition Option 2
            condition2 = ligne.get('Condition Option 2')
            if self.evaluer_condition(condition2, donnees):
                texte = ligne.get('Entrée correspondante - Option 2')
                if pd.notna(texte):
                    return str(texte)

        logger.warning(f"Aucune condition satisfaite pour l'article '{article_name}'")
        return None

    def remplacer_placeholders(self, texte: str, donnees: Dict[str, Any]) -> str:
        """
        Remplace les placeholders [Variable] dans le texte.

        Args:
            texte: Texte avec placeholders
            donnees: Données pour remplacer les placeholders

        Returns:
            Texte avec placeholders remplacés
        """
        if not texte:
            return ""

        # Trouver tous les placeholders [Variable]
        placeholders = re.findall(r'\[([^\]]+)\]', texte)

        for placeholder in placeholders:
            # Normaliser le nom de la variable
            placeholder_norm = self._normaliser_nom_variable(placeholder)
            valeur = donnees.get(placeholder_norm) or donnees.get(placeholder)
            if valeur is not None:
                # Formater les nombres avec séparateurs si nécessaire
                if isinstance(valeur, (int, float)):
                    valeur_str = f"{valeur:,.2f}".replace(",", " ").replace(".", ",")
                    # Retirer les décimales si .00
                    valeur_str = valeur_str.replace(",00", "")
                else:
                    valeur_str = str(valeur)

                texte = texte.replace(f"[{placeholder}]", valeur_str)
            else:
                logger.warning(f"Placeholder non trouvé dans les données: [{placeholder}]")
                texte = texte.replace(f"[{placeholder}]", f"[{placeholder}]")  # Garder le placeholder

        return texte

    def generer_bail(self, donnees: Dict[str, Any]) -> Dict[str, str]:
        """
        Génère le contenu complet du BAIL.

        Args:
            donnees: Dictionnaire avec toutes les données primaires

        Returns:
            Dictionnaire avec les articles générés
            {
                "Comparution": "texte...",
                "Article préliminaire": "texte...",
                ...
            }
        """
        logger.info("Début de la génération du BAIL")

        # 1. Calculer les variables dérivées
        donnees_complete = self.calculer_variables_derivees(donnees)

        # 2. Générer chaque article
        articles_generes = {}

        # Liste des articles à générer (dans l'ordre)
        articles_order = [
            "Comparution",
            "Article préliminaire",
            "Article 1",
            "Article 2",
            "Article 3",
            "Article 5.3",
            "Article 7.1",
            "Article 7.2",
            "Article 7.3",
            "Article 7.6",
            "Article 8",
            "Article 19",
            "Article 22.2",
            "Article 26",
            "Article 26.1",
            "Article 26.2"
        ]

        for article_name in articles_order:
            texte = self.obtenir_texte_article(article_name, None, donnees_complete)

            if texte:
                # Remplacer les placeholders
                texte_final = self.remplacer_placeholders(texte, donnees_complete)
                articles_generes[article_name] = texte_final
                logger.debug(f"Article généré: {article_name}")
            else:
                logger.warning(f"Article non généré: {article_name}")

        logger.info(f"Génération terminée: {len(articles_generes)} articles générés")
        return articles_generes
