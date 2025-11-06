"""
Module pour parser les fichiers Excel BAIL.

Format attendu: onglet "Liste données BAIL" avec mapping des variables
"""

import pandas as pd
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class BailExcelParser:
    """Parser pour extraire les données BAIL depuis Excel."""

    def __init__(self, excel_path: str, config_path: str = "Redaction BAIL.xlsx"):
        """
        Initialise le parser BAIL.

        Args:
            excel_path: Chemin vers le fichier Excel avec les données
            config_path: Chemin vers le fichier de configuration BAIL
        """
        self.excel_path = excel_path
        self.config_path = config_path

    def extract_variables(self) -> Dict[str, Any]:
        """
        Extrait les variables depuis le fichier Excel BAIL.

        Utilise l'onglet "Liste données BAIL" du fichier de configuration
        pour savoir où trouver chaque variable dans le fichier Excel source.

        Returns:
            Dictionnaire {nom_variable: valeur}
        """
        try:
            # Charger la configuration (mapping des variables)
            config_df = pd.read_excel(
                self.config_path,
                sheet_name="Liste données BAIL"
            )

            # Charger le fichier Excel source
            # On va essayer différents onglets
            xl_file = pd.ExcelFile(self.excel_path)

            # Priorité: "Validation", "Last Forecast", premier onglet
            sheet_name = None
            for preferred in ["Validation", "Last Forecast"]:
                if preferred in xl_file.sheet_names:
                    sheet_name = preferred
                    break
            if not sheet_name:
                sheet_name = xl_file.sheet_names[0]

            logger.info(f"Lecture de l'onglet '{sheet_name}' depuis {self.excel_path}")
            data_df = pd.read_excel(self.excel_path, sheet_name=sheet_name)

            # Extraire les variables selon le mapping
            variables = {}

            for _, row in config_df.iterrows():
                var_name = row.get("Variable")
                source_sheet = row.get("Source")
                cell_or_desc = row.get("Cellule / Description")

                if pd.isna(var_name):
                    continue

                # Si la source correspond à l'onglet qu'on lit
                if pd.notna(source_sheet) and source_sheet == sheet_name:
                    # Essayer de trouver la variable
                    # Méthode 1: Chercher var_name dans la première colonne
                    for idx, data_row in data_df.iterrows():
                        if str(data_row.iloc[0]).strip() == str(var_name).strip():
                            # Prendre la valeur dans la 2e colonne
                            if len(data_row) > 1:
                                value = data_row.iloc[1]
                                if pd.notna(value):
                                    variables[var_name] = value
                                    logger.debug(f"Variable trouvée: {var_name} = {value}")
                            break

            logger.info(f"Variables BAIL extraites: {len(variables)}")
            return variables

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des variables BAIL: {e}")
            raise

    def get_output_filename(self, variables: Dict[str, Any]) -> str:
        """
        Génère le nom du fichier de sortie.

        Args:
            variables: Variables extraites

        Returns:
            Nom de fichier pour le BAIL généré
        """
        nom_preneur = variables.get("Nom Preneur", "Client")
        date_loi = variables.get("Date LOI", "")

        filename = f"BAIL - {nom_preneur} - {date_loi}.docx"
        # Nettoyer les caractères invalides
        filename = filename.replace("/", "-").replace("\\", "-")

        return filename
