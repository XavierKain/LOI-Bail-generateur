"""
Module de génération de documents BAIL au format Word.

Ce module prend les articles générés par BailGenerator et les insère
dans le template Word avec placeholders, puis remplace tous les placeholders
[Variable] par les valeurs extraites.
"""

from docx import Document
from docx.shared import RGBColor, Pt
from pathlib import Path
from typing import Dict, Optional, Union
import logging
import re
import openpyxl
from openpyxl.cell.rich_text import CellRichText
from .number_to_french import number_to_french_words
from .text_style import TextStyle, RichTextStyle
from .word_text_loader import WordTextLoader
from .placeholder_formatter import replace_placeholder_with_format

logger = logging.getLogger(__name__)


class BailWordGenerator:
    """Générateur de documents BAIL au format Word."""

    def _normalize_variable_name(self, var_name: str, donnees: Dict[str, any]) -> str:
        """
        Normalise le nom de variable pour gérer les variations.

        Args:
            var_name: Nom de variable brut
            donnees: Données disponibles

        Returns:
            Nom de variable normalisé ou original si trouvé directement
        """
        # Si la variable existe telle quelle, la retourner
        if var_name in donnees:
            return var_name

        # Mappings courants
        mappings = {
            # Montant Palier X → Montant du palier X
            **{f"Montant Palier {i}": f"Montant du palier {i}" for i in range(1, 7)},
            **{f"Montant palier {i}": f"Montant du palier {i}" for i in range(1, 7)},
        }

        normalized = mappings.get(var_name, var_name)

        # Si toujours pas trouvé, chercher avec des variations de casse
        if normalized not in donnees:
            for key in donnees.keys():
                if key.lower() == normalized.lower():
                    return key

        return normalized

    def __init__(self, template_path: str = "Template BAIL avec placeholder.docx",
                 excel_config_path: str = "Redaction BAIL.xlsx",
                 word_styles_path: str = "Textes BAIL avec styles.docx"):
        """
        Initialise le générateur Word pour BAIL.

        Args:
            template_path: Chemin vers le template Word avec placeholders
            excel_config_path: Chemin vers le fichier Excel de configuration (pour les styles - deprecated)
            word_styles_path: Chemin vers le document Word contenant les textes formatés
        """
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template non trouvé: {template_path}")

        self.excel_config_path = Path(excel_config_path)
        self.text_styles = {}  # {row_idx: {col_name: TextStyle}} - deprecated

        # Charger les styles depuis le document Word
        self.word_text_loader = WordTextLoader(word_styles_path)

        logger.info(f"Template BAIL chargé: {template_path}")
        logger.info(f"Styles chargés: {self.word_text_loader}")

    def _load_styles_from_excel(self):
        """Charge les styles de texte depuis le fichier Excel de configuration."""
        try:
            # Charger avec data_only=False pour détecter le rich text
            wb = openpyxl.load_workbook(self.excel_config_path, data_only=False, rich_text=True)
            ws_bail = wb["Rédaction BAIL"]

            headers = [cell.value for cell in ws_bail[1]]

            for row_idx in range(2, ws_bail.max_row + 1):
                row_styles = {}

                for col_idx, header in enumerate(headers, start=1):
                    if header:
                        cell = ws_bail.cell(row_idx, col_idx)
                        if cell.value is not None:
                            # Vérifier si c'est du rich text
                            if isinstance(cell.value, CellRichText):
                                # Rich text avec formatage partiel
                                rich_style = RichTextStyle.from_excel_rich_text(cell.value)
                                row_styles[header] = rich_style
                            else:
                                # Texte simple avec formatage uniforme
                                style = TextStyle.from_excel_cell(cell)
                                if isinstance(cell.value, str):
                                    style.text = cell.value.strip()
                                else:
                                    style.text = str(cell.value)
                                row_styles[header] = style

                if row_styles:
                    self.text_styles[row_idx] = row_styles

            wb.close()
            logger.info(f"Styles chargés depuis {self.excel_config_path}: {len(self.text_styles)} lignes")

        except Exception as e:
            logger.warning(f"Impossible de charger les styles depuis Excel: {e}")
            self.text_styles = {}

    def generer_document(
        self,
        articles_generes: Dict[str, str],
        donnees: Dict[str, any],
        output_path: str
    ) -> None:
        """
        Génère le document BAIL Word final.

        Args:
            articles_generes: Dict avec les articles générés par BailGenerator
            donnees: Données complètes (variables extraites + dérivées)
            output_path: Chemin de sortie pour le document généré

        Raises:
            FileNotFoundError: Si le template n'existe pas
        """
        logger.info("Début de la génération du document BAIL Word")

        # Charger le template
        doc = Document(self.template_path)

        # ÉTAPE 1: Remplacer les placeholders {{ARTICLE}}
        placeholder_mapping = {
            "{{COMPARUTION_BAILLEUR}}": articles_generes.get("Comparution Bailleur", ""),
            "{{COMPARUTION_PRENEUR}}": articles_generes.get("Comparution Preneur", ""),
            "{{ARTICLE_PRELIMINAIRE}}": articles_generes.get("Article préliminaire", ""),
            "{{ARTICLE_1}}": articles_generes.get("Article 1", ""),
            "{{ARTICLE_2}}": articles_generes.get("Article 2", ""),
            "{{ARTICLE_3}}": articles_generes.get("Article 3", ""),
            "{{ARTICLE_5_3}}": articles_generes.get("Article 5.3", ""),
            "{{ARTICLE_7_1}}": articles_generes.get("Article 7.1", ""),
            "{{ARTICLE_7_2}}": articles_generes.get("Article 7.2", ""),
            "{{ARTICLE_7_3}}": articles_generes.get("Article  7.3", ""),  # Note: 2 espaces
            "{{ARTICLE_7_6}}": articles_generes.get("Article 7.6", ""),
            "{{ARTICLE_8}}": articles_generes.get("Article 8", ""),
            "{{ARTICLE_19}}": articles_generes.get("Article 19", ""),
            "{{ARTICLE_22_2}}": articles_generes.get("Article 22.2", ""),
            "{{ARTICLE_26}}": articles_generes.get("Article 26", ""),
            "{{ARTICLE_26_1}}": articles_generes.get("Article 26.1", ""),
            "{{ARTICLE_26_2}}": articles_generes.get("Article 26.2", ""),
            "{{VILLE}}": donnees.get("Ville ou arrondissement", "Paris").split("(")[0].strip(),
            "{{DATE_SIGNATURE}}": donnees.get("Date de signature", ""),
        }

        # Remplacer les placeholders {{ARTICLE}} dans tous les paragraphes
        for paragraph in doc.paragraphs:
            self._replace_article_placeholders(paragraph, placeholder_mapping)

        # Remplacer les placeholders dans les tableaux
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        self._replace_article_placeholders(paragraph, placeholder_mapping)

        # ÉTAPE 2: Remplacer les placeholders [Variable] dans TOUT le document
        # (comme dans LOIGenerator)
        for paragraph in doc.paragraphs:
            self._replace_variable_placeholders(paragraph, donnees)

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        self._replace_variable_placeholders(paragraph, donnees)

        # Nettoyer les paragraphes vides
        self._clean_empty_paragraphs(doc)

        # Sauvegarder le document
        doc.save(output_path)
        logger.info(f"Document BAIL généré: {output_path}")

    def _get_comparution_bailleur(self, articles: Dict[str, str]) -> str:
        """
        Extrait le texte de comparution du Bailleur.

        Args:
            articles: Articles générés

        Returns:
            Texte de comparution du Bailleur
        """
        comparution = articles.get("Comparution", "")
        if not comparution:
            return ""

        # Le texte complet contient bailleur et preneur
        # On cherche la partie bailleur (avant "D'UNE PART")
        parts = comparution.split("D'UNE PART")
        if len(parts) >= 1:
            return parts[0].strip()
        return comparution

    def _get_comparution_preneur(self, articles: Dict[str, str]) -> str:
        """
        Extrait le texte de comparution du Preneur.

        Args:
            articles: Articles générés

        Returns:
            Texte de comparution du Preneur
        """
        comparution = articles.get("Comparution", "")
        if not comparution:
            return ""

        # Le texte complet contient bailleur et preneur
        # On cherche la partie preneur (après "ET :" et avant "D'AUTRE PART")
        if "ET :" in comparution:
            parts = comparution.split("ET :")
            if len(parts) >= 2:
                preneur_part = parts[1].split("D'AUTRE PART")[0] if "D'AUTRE PART" in parts[1] else parts[1]
                return preneur_part.strip()

        return ""

    def _get_section_id_for_text(self, text: str) -> Optional[str]:
        """
        Tente de trouver l'ID de section correspondant dans le document Word.

        Args:
            text: Le texte à chercher

        Returns:
            L'ID de section si trouvé, sinon None
        """
        if not text or not self.word_text_loader:
            return None

        # Chercher dans toutes les sections
        for section_id in self.word_text_loader.get_section_ids():
            section_para = self.word_text_loader.get_formatted_paragraph(section_id)
            if section_para and section_para.text.strip() == text.strip():
                return section_id

        return None

    def _replace_article_placeholders(
        self,
        paragraph,
        mapping: Dict[str, str]
    ) -> None:
        """
        Remplace les placeholders {{ARTICLE}} dans un paragraphe.
        Applique le formatage depuis le document Word si disponible.

        Args:
            paragraph: Paragraphe docx
            mapping: Mapping {placeholder: texte_final}
        """
        full_text = paragraph.text

        # Vérifier s'il y a des placeholders {{}}
        if "{{" not in full_text:
            return

        # Pour chaque placeholder trouvé
        for placeholder, replacement in mapping.items():
            if placeholder in full_text:
                # Si le remplacement est vide, on supprime le placeholder
                if not replacement:
                    full_text = full_text.replace(placeholder, "")
                else:
                    # Chercher si on a un paragraphe formaté dans le Word
                    section_id = self._get_section_id_for_text(replacement)

                    if section_id:
                        # On a trouvé le formatage ! L'appliquer
                        source_para = self.word_text_loader.get_formatted_paragraph(section_id)
                        if source_para:
                            # Remplacer le placeholder par le texte formaté
                            full_text = full_text.replace(placeholder, replacement)
                            # Appliquer le formatage
                            self.word_text_loader.copy_formatted_text_to_paragraph(source_para, paragraph)
                            logger.info(f"✨ Formatage appliqué depuis Word pour {section_id}")
                            return  # Important: sortir pour ne pas écraser le formatage

                    # Sinon, remplacement normal sans formatage
                    full_text = full_text.replace(placeholder, replacement)

        # Si le texte a changé, on met à jour le paragraphe
        if full_text != paragraph.text:
            # Préserver le formatage du premier run
            if paragraph.runs:
                # Vider tous les runs
                for run in paragraph.runs:
                    run.text = ""
                # Ajouter le nouveau texte au premier run
                paragraph.runs[0].text = full_text
            else:
                paragraph.text = full_text

    def _replace_variable_placeholders(
        self,
        paragraph,
        donnees: Dict[str, any]
    ) -> None:
        """
        Remplace les placeholders [Variable] dans un paragraphe EN PRÉSERVANT LE FORMATAGE.
        Met les placeholders manquants en ROUGE.
        Gère les placeholders "en lettres" pour conversion numérique.

        Args:
            paragraph: Paragraphe docx
            donnees: Données avec toutes les variables
        """
        full_text = paragraph.text

        # Trouver tous les placeholders [Variable]
        placeholders = re.findall(r'\[([^\]]+)\]', full_text)

        if not placeholders:
            return

        # Pour chaque placeholder, essayer de le remplacer avec formatage préservé
        for placeholder in placeholders:
            placeholder_with_brackets = f"[{placeholder}]"

            # Gestion spéciale pour les placeholders "en lettres"
            if placeholder.endswith(" en lettres"):
                base_variable = placeholder.replace(" en lettres", "")
                base_variable = self._normalize_variable_name(base_variable, donnees)
                value = donnees.get(base_variable)

                if value and str(value).strip():
                    try:
                        value_clean = str(value).replace(" ", "").replace(",", ".")
                        numeric_value = float(value_clean)
                        words = number_to_french_words(numeric_value)
                        # Remplacer avec préservation du formatage
                        replace_placeholder_with_format(paragraph, placeholder_with_brackets, words + " ")
                        logger.info(f"✨ Formatage préservé pour placeholder '{placeholder}'")
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Impossible de convertir '{value}' en lettres: {e}")
                        # Laisser le placeholder (sera mis en rouge à la fin)
                else:
                    # Placeholder manquant sera géré à la fin
                    pass
            else:
                # Placeholder normal
                normalized_placeholder = self._normalize_variable_name(placeholder, donnees)
                value = donnees.get(normalized_placeholder)

                if value and str(value).strip():
                    # Remplacer avec préservation du formatage
                    replace_placeholder_with_format(paragraph, placeholder_with_brackets, str(value))
                    logger.info(f"✨ Formatage préservé pour placeholder '{placeholder}'")
                else:
                    # Placeholder manquant sera géré à la fin
                    pass

        # Deuxième passe: mettre les placeholders restants en rouge
        full_text = paragraph.text
        remaining_placeholders = re.findall(r'\[([^\]]+)\]', full_text)

        if remaining_placeholders:
            # Il reste des placeholders non remplacés: les mettre en rouge
            # Vider les runs existants
            for run in list(paragraph.runs):
                run.text = ""

            # Parser le texte et créer des runs avec le bon formatage
            current_pos = 0
            for match in re.finditer(r'\[([^\]]+)\]', full_text):
                # Texte avant le placeholder
                if match.start() > current_pos:
                    run = paragraph.add_run(full_text[current_pos:match.start()])
                    run.font.color.rgb = RGBColor(0, 0, 0)

                # Le placeholder en rouge
                placeholder = match.group(0)  # Avec les crochets
                run = paragraph.add_run(placeholder)
                run.font.color.rgb = RGBColor(255, 0, 0)

                current_pos = match.end()

            # Texte après le dernier placeholder
            if current_pos < len(full_text):
                run = paragraph.add_run(full_text[current_pos:])
                run.font.color.rgb = RGBColor(0, 0, 0)

    def _set_paragraph_text_with_styles(self, paragraph, text: str,
                                         text_style: Optional[Union[TextStyle, RichTextStyle]] = None):
        """
        Remplace le texte d'un paragraphe en appliquant les styles si disponibles.

        Args:
            paragraph: Paragraphe Word
            text: Nouveau texte (ignoré si text_style est RichTextStyle)
            text_style: Style à appliquer (TextStyle ou RichTextStyle, optionnel)
        """
        # Vider tous les runs existants
        for run in paragraph.runs:
            run.text = ""

        if isinstance(text_style, RichTextStyle):
            # Rich text: appliquer directement au paragraphe
            text_style.apply_to_word_paragraph(paragraph)
        else:
            # Texte simple: créer un seul run
            if paragraph.runs:
                new_run = paragraph.runs[0]
            else:
                new_run = paragraph.add_run()

            new_run.text = text

            # Appliquer les styles si disponibles
            if text_style:
                text_style.apply_to_word_run(new_run)

    def _clean_empty_paragraphs(self, doc) -> None:
        """
        Nettoie les paragraphes qui ne contiennent que des placeholders vides.

        Args:
            doc: Document docx
        """
        paragraphs_to_remove = []

        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            # Si le paragraphe ne contient que des {{ }} vides ou est vide
            if not text or re.match(r'^(\{\{[^}]*\}\}\s*)+$', text):
                if text:  # Contient des {{ }} non remplacés
                    paragraphs_to_remove.append(paragraph)

        # Supprimer les paragraphes identifiés
        for paragraph in paragraphs_to_remove:
            p_element = paragraph._element
            p_element.getparent().remove(p_element)

        logger.debug(f"Nettoyé {len(paragraphs_to_remove)} paragraphes vides")
