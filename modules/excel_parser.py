"""
Module pour extraire les données des fichiers Excel (Fiche de décision).
Lit les données depuis les différents onglets et les map vers les variables LOI.
"""

import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
import openpyxl
from openpyxl.utils.exceptions import InvalidFileException
from .inpi_client import get_inpi_client

logger = logging.getLogger(__name__)


class ExcelParser:
    """Parse les fichiers Excel de décision pour extraire les variables LOI."""

    def __init__(self, excel_path: str, config_path: str = "Rédaction LOI.xlsx"):
        """
        Initialise le parser avec le fichier Excel source.

        Args:
            excel_path: Chemin vers le fichier Excel source (Fiche de décision)
            config_path: Chemin vers le fichier de configuration (Rédaction LOI.xlsx)
        """
        self.excel_path = Path(excel_path)
        self.config_path = Path(config_path)

        if not self.excel_path.exists():
            raise FileNotFoundError(f"Fichier Excel source introuvable: {excel_path}")
        if not self.config_path.exists():
            raise FileNotFoundError(f"Fichier de configuration introuvable: {config_path}")

        try:
            self.workbook = openpyxl.load_workbook(self.excel_path, data_only=True)
            self.config_workbook = openpyxl.load_workbook(self.config_path, data_only=True)
            # Also load config with formulas to handle cases where cached values are missing
            self.config_workbook_formulas = openpyxl.load_workbook(self.config_path, data_only=False)
            logger.info(f"Fichier Excel chargé: {self.excel_path.name}")
            logger.info(f"Configuration chargée: {self.config_path.name}")
        except InvalidFileException as e:
            raise ValueError(f"Fichier Excel invalide: {e}")

    def _get_cell_value(self, sheet_name: str, cell_ref: str) -> Optional[str]:
        """
        Récupère la valeur d'une cellule depuis un onglet.

        Args:
            sheet_name: Nom de l'onglet
            cell_ref: Référence de la cellule (ex: "B23")

        Returns:
            Valeur de la cellule ou None
        """
        try:
            if sheet_name not in self.workbook.sheetnames:
                logger.warning(f"Onglet '{sheet_name}' introuvable")
                return None

            sheet = self.workbook[sheet_name]
            value = sheet[cell_ref].value

            # Convertir les valeurs en string, gérer les dates
            if value is None:
                return None
            elif isinstance(value, datetime):
                return value.strftime("%d/%m/%Y")
            elif isinstance(value, (int, float)):
                return str(value)
            else:
                return str(value).strip()

        except Exception as e:
            logger.warning(f"Erreur lecture cellule {sheet_name}!{cell_ref}: {e}")
            return None

    def _parse_vlookup(self, formula: str) -> Optional[str]:
        """
        Parse une formule RECHERCHEV (VLOOKUP) et retourne la valeur.

        Format: RECHERCHEV(valeur_cherchée; plage; numéro_colonne; 0)

        Args:
            formula: Formule RECHERCHEV

        Returns:
            Valeur trouvée ou None
        """
        import re

        # Pattern: RECHERCHEV(arg1;arg2;arg3;arg4)
        match = re.match(r'RECHERCHEV\((.*)\)', formula, re.IGNORECASE)
        if not match:
            return None

        args_str = match.group(1)
        # Split par ; mais en ignorant les ; dans les noms de feuilles entre quotes
        args = []
        current_arg = ""
        in_quotes = False
        for char in args_str:
            if char == "'":
                in_quotes = not in_quotes
                current_arg += char
            elif char == ';' and not in_quotes:
                args.append(current_arg.strip())
                current_arg = ""
            else:
                current_arg += char
        if current_arg:
            args.append(current_arg.strip())

        if len(args) < 3:
            logger.warning(f"RECHERCHEV mal formée: pas assez d'arguments ({len(args)})")
            return None

        lookup_value_ref = args[0]
        table_range = args[1]
        col_index = int(args[2])

        # Extraire la valeur à chercher
        lookup_value = self._parse_formula(f"={lookup_value_ref}")
        if not lookup_value:
            logger.warning(f"Impossible de lire la valeur de recherche: {lookup_value_ref}")
            return None

        # Parser la plage (ex: 'EL F&A'!B9:P14)
        if "!" not in table_range:
            logger.warning(f"Plage RECHERCHEV invalide: {table_range}")
            return None

        parts = table_range.split("!")
        sheet_name = parts[0].strip("'")
        range_ref = parts[1].strip()

        # Parser la plage (ex: B9:P14)
        if ":" not in range_ref:
            logger.warning(f"Référence de plage invalide: {range_ref}")
            return None

        start_cell, end_cell = range_ref.split(":")

        # Extraire les coordonnées
        match_start = re.match(r'([A-Z]+)(\d+)', start_cell)
        match_end = re.match(r'([A-Z]+)(\d+)', end_cell)

        if not match_start or not match_end:
            logger.warning(f"Impossible de parser la plage: {range_ref}")
            return None

        start_col = match_start.group(1)
        start_row = int(match_start.group(2))
        end_row = int(match_end.group(2))

        # Convertir colonne lettre en nombre (A=1, B=2, etc.)
        def col_to_num(col):
            num = 0
            for char in col:
                num = num * 26 + (ord(char) - ord('A') + 1)
            return num

        start_col_num = col_to_num(start_col)

        # Accéder à la feuille
        if sheet_name not in self.workbook.sheetnames:
            logger.warning(f"Feuille '{sheet_name}' introuvable pour RECHERCHEV")
            return None

        ws = self.workbook[sheet_name]

        # Chercher la valeur dans la première colonne de la plage
        try:
            lookup_value_num = float(lookup_value)
        except:
            lookup_value_num = None

        for row in range(start_row, end_row + 1):
            cell_value = ws.cell(row, start_col_num).value

            # Comparaison (gérer nombres et textes)
            match_found = False
            if lookup_value_num is not None and isinstance(cell_value, (int, float)):
                match_found = (float(cell_value) == lookup_value_num)
            else:
                match_found = (str(cell_value).strip() == str(lookup_value).strip())

            if match_found:
                # Retourner la valeur de la colonne demandée
                result_col_num = start_col_num + col_index - 1
                result_value = ws.cell(row, result_col_num).value

                if result_value is not None:
                    return str(result_value)

        logger.warning(f"Valeur '{lookup_value}' non trouvée dans RECHERCHEV")
        return None

    def _parse_formula(self, formula: str) -> Optional[str]:
        """
        Parse une formule Excel pour extraire la valeur.

        Args:
            formula: Formule Excel (ex: "=Validation!B23" ou "=[1]Validation!B24" ou "=RECHERCHEV(...)")

        Returns:
            Valeur extraite ou None
        """
        if not formula or not isinstance(formula, str):
            return None

        # Retirer le signe =
        formula = formula.strip()
        if formula.startswith("="):
            formula = formula[1:]

        # Retirer les références à d'autres workbooks (ex: [1], [Classeur1], etc.)
        # Pattern: [xxx]SheetName!Cell → SheetName!Cell
        import re
        formula = re.sub(r'^\[.*?\]', '', formula)

        # Vérifier si c'est une formule RECHERCHEV
        if formula.upper().startswith("RECHERCHEV("):
            return self._parse_vlookup(formula)

        # Format: 'Sheet Name'!CellRef ou SheetName!CellRef
        if "!" in formula:
            parts = formula.split("!")
            sheet_name = parts[0].strip("'")
            cell_ref = parts[1].strip()
            return self._get_cell_value(sheet_name, cell_ref)

        return None

    def extract_variables(self) -> Dict[str, str]:
        """
        Extrait toutes les variables depuis le fichier Excel source.
        Utilise le fichier de configuration pour savoir quoi extraire.

        Returns:
            Dictionnaire {nom_variable: valeur}
        """
        variables = {}

        # Lire la configuration depuis Rédaction LOI
        config_sheet = self.config_workbook["Rédaction LOI"]
        config_sheet_formulas = self.config_workbook_formulas["Rédaction LOI"]

        # Parcourir les lignes de configuration (ligne 2 à 40+)
        for row in range(2, max(config_sheet.max_row, config_sheet_formulas.max_row) + 1):
            nom = config_sheet.cell(row, 1).value  # Colonne A: Nom
            source = config_sheet.cell(row, 2).value  # Colonne B: Source

            # Si source est None ou une erreur (#REF!, #N/A, etc.), essayer de lire la formule
            if not source or (isinstance(source, str) and source.startswith("#")):
                source = config_sheet_formulas.cell(row, 2).value

            if not nom:
                continue

            nom = str(nom).strip()

            # Cas spéciaux: formules de calcul dans la config
            if source and isinstance(source, str):
                if source.startswith("=") and "!" in source:
                    # C'est une référence à une cellule
                    value = self._parse_formula(source)
                    if value:
                        variables[nom] = value
                elif "[" in source and "]" in source:
                    # C'est une formule qui sera calculée plus tard (ex: adresse, paliers)
                    # On la stocke pour traitement ultérieur
                    variables[f"_formula_{nom}"] = source
                else:
                    # Texte littéral ou description
                    variables[f"_description_{nom}"] = source

        # Ajouter la date d'aujourd'hui
        variables["Date d'aujourd'hui"] = datetime.now().strftime("%d/%m/%Y")

        # Enrichissement automatique via INPI si SIRET présent
        siret = self._get_cell_value("Validation", "B25")
        if siret:
            logger.info(f"SIRET détecté: {siret} - Enrichissement INPI en cours...")
            inpi_data = self._enrich_from_inpi(siret)

            # Fusionner les données INPI avec les variables extraites
            variables.update(inpi_data)

            # Ajouter un flag pour savoir si l'enrichissement a réussi
            if inpi_data.get("enrichment_status") == "success":
                variables["_inpi_enriched"] = "true"
                logger.info("✓ Enrichissement INPI réussi")
            else:
                variables["_inpi_enriched"] = "false"
                error_msg = inpi_data.get("error_message", "Erreur inconnue")
                variables["_inpi_error"] = error_msg
                logger.warning(f"✗ Enrichissement INPI échoué: {error_msg}")

        logger.info(f"{len(variables)} variables extraites")
        return variables

    def extract_societe_info(self) -> Dict[str, Dict[str, str]]:
        """
        Extrait les informations des sociétés bailleures depuis la configuration.

        Returns:
            Dictionnaire {nom_societe: {header: str, footer: str}}
        """
        societes = {}

        config_sheet = self.config_workbook["Société Bailleur"]

        # Parcourir les lignes (ligne 2 = première société)
        for row in range(2, config_sheet.max_row + 1):
            nom_societe = config_sheet.cell(row, 1).value  # Colonne A
            header = config_sheet.cell(row, 2).value  # Colonne B
            footer = config_sheet.cell(row, 3).value  # Colonne C

            if not nom_societe:
                continue

            nom_societe = str(nom_societe).strip()

            societes[nom_societe] = {
                "header": str(header).strip() if header else nom_societe,
                "footer": str(footer).strip() if footer else ""
            }

        logger.info(f"{len(societes)} sociétés bailleures chargées")
        return societes

    def get_output_filename(self, variables: Dict[str, str]) -> str:
        """
        Génère le nom du fichier de sortie basé sur les variables extraites.
        Format: "YYYY MM DD - LOI NomPreneur.docx"

        Args:
            variables: Dictionnaire des variables

        Returns:
            Nom du fichier de sortie
        """
        date_loi = variables.get("Date LOI", "")
        nom_preneur = variables.get("Nom Preneur", "INCONNU")

        # Parser la date si elle existe
        if date_loi:
            try:
                # Format attendu: DD/MM/YYYY
                if "/" in date_loi:
                    parts = date_loi.split("/")
                    date_str = f"{parts[2]} {parts[1]} {parts[0]}"
                else:
                    # Utiliser la date d'aujourd'hui
                    date_str = datetime.now().strftime("%Y %m %d")
            except:
                date_str = datetime.now().strftime("%Y %m %d")
        else:
            date_str = datetime.now().strftime("%Y %m %d")

        filename = f"{date_str} - LOI {nom_preneur}.docx"
        return filename

    def _enrich_from_inpi(self, siret: str) -> Dict[str, str]:
        """
        Enrichit les données avec l'API INPI.

        Args:
            siret: Numéro SIRET de l'entreprise

        Returns:
            Dictionnaire avec les données enrichies INPI
        """
        # Initialiser le résultat vide
        inpi_data = {
            "N° DE SIRET": siret,
            "NOM DE LA SOCIETE": "",
            "TYPE DE SOCIETE": "",
            "CAPITAL SOCIAL": "",
            "LOCALITE RCS": "",
            "ADRESSE DE DOMICILIATION": "",
            "PRESIDENT DE LA SOCIETE": "",
            "FONCTION INPI": "",
            "enrichment_status": "failed",
            "error_message": ""
        }

        # Récupérer le client INPI
        inpi_client = get_inpi_client()

        if not inpi_client:
            inpi_data["error_message"] = "Client INPI non configuré (credentials manquants)"
            logger.warning(inpi_data["error_message"])
            return inpi_data

        try:
            # Interroger l'API INPI
            company_info = inpi_client.get_company_info(siret)

            # Mettre à jour avec les données récupérées
            inpi_data.update(company_info)

            return inpi_data

        except Exception as e:
            inpi_data["error_message"] = f"Erreur lors de l'enrichissement INPI: {str(e)}"
            logger.error(inpi_data["error_message"], exc_info=True)
            return inpi_data
