"""
Module de génération de documents BAIL au format Word.

Ce module prend les articles générés par BailGenerator et les insère
dans le template Word avec placeholders.
"""

from docx import Document
from pathlib import Path
from typing import Dict
import logging
import re

logger = logging.getLogger(__name__)


class BailWordGenerator:
    """Générateur de documents BAIL au format Word."""

    def __init__(self, template_path: str = "Template BAIL avec placeholder.docx"):
        """
        Initialise le générateur Word pour BAIL.

        Args:
            template_path: Chemin vers le template Word avec placeholders
        """
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template non trouvé: {template_path}")

        logger.info(f"Template BAIL chargé: {template_path}")

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
            donnees: Données complètes (pour VILLE et DATE_SIGNATURE)
            output_path: Chemin de sortie pour le document généré

        Raises:
            FileNotFoundError: Si le template n'existe pas
        """
        logger.info("Début de la génération du document BAIL Word")

        # Charger le template
        doc = Document(self.template_path)

        # Mapping des placeholders vers les articles générés
        placeholder_mapping = {
            "{{COMPARUTION_BAILLEUR}}": self._get_comparution_bailleur(articles_generes),
            "{{COMPARUTION_PRENEUR}}": self._get_comparution_preneur(articles_generes),
            "{{ARTICLE_PRELIMINAIRE}}": articles_generes.get("Article préliminaire", ""),
            "{{ARTICLE_1}}": articles_generes.get("Article 1", ""),
            "{{ARTICLE_2}}": articles_generes.get("Article 2", ""),
            "{{ARTICLE_3}}": articles_generes.get("Article 3", ""),
            "{{ARTICLE_5_3}}": articles_generes.get("Article 5.3", ""),
            "{{ARTICLE_7_1}}": articles_generes.get("Article 7.1", ""),
            "{{ARTICLE_7_2}}": articles_generes.get("Article 7.2", ""),
            "{{ARTICLE_7_3}}": articles_generes.get("Article 7.3", ""),
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

        # Remplacer les placeholders dans tous les paragraphes
        for paragraph in doc.paragraphs:
            self._replace_placeholders_in_paragraph(paragraph, placeholder_mapping)

        # Remplacer les placeholders dans les tableaux (signature)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        self._replace_placeholders_in_paragraph(paragraph, placeholder_mapping)

        # Nettoyer les paragraphes vides avec placeholders vides
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

    def _replace_placeholders_in_paragraph(
        self,
        paragraph,
        mapping: Dict[str, str]
    ) -> None:
        """
        Remplace les placeholders dans un paragraphe en préservant le formatage.

        Args:
            paragraph: Paragraphe docx
            mapping: Mapping {placeholder: texte_final}
        """
        # Reconstituer le texte complet du paragraphe
        full_text = paragraph.text

        # Vérifier s'il y a des placeholders
        if "{{" not in full_text:
            return

        # Pour chaque placeholder trouvé
        for placeholder, replacement in mapping.items():
            if placeholder in full_text:
                # Si le remplacement est vide, on supprime le placeholder
                if not replacement:
                    full_text = full_text.replace(placeholder, "")
                else:
                    full_text = full_text.replace(placeholder, replacement)

        # Si le texte a changé, on met à jour le paragraphe
        if full_text != paragraph.text:
            # Préserver le formatage du premier run
            if paragraph.runs:
                first_run_format = paragraph.runs[0]
                # Vider tous les runs
                for run in paragraph.runs:
                    run.text = ""
                # Ajouter le nouveau texte au premier run
                paragraph.runs[0].text = full_text
            else:
                # Pas de runs, créer un nouveau
                paragraph.text = full_text

    def _clean_empty_paragraphs(self, doc) -> None:
        """
        Nettoie les paragraphes qui ne contiennent que des placeholders vides.

        Args:
            doc: Document docx
        """
        # Identifier les paragraphes vides à supprimer
        paragraphs_to_remove = []

        for i, paragraph in enumerate(doc.paragraphs):
            text = paragraph.text.strip()
            # Si le paragraphe ne contient que des {{ }} vides ou est vide
            if not text or re.match(r'^(\{\{[^}]*\}\}\s*)+$', text):
                # Ne pas supprimer les paragraphes de structure (vides intentionnels)
                # On vérifie s'il y a du contenu avant/après
                if text:  # Contient des {{ }} non remplacés
                    paragraphs_to_remove.append(paragraph)

        # Supprimer les paragraphes identifiés
        for paragraph in paragraphs_to_remove:
            p_element = paragraph._element
            p_element.getparent().remove(p_element)

        logger.debug(f"Nettoyé {len(paragraphs_to_remove)} paragraphes vides")
