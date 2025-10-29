"""
Module pour générer les documents LOI depuis le template Word.
Gère le remplacement des placeholders, les sections optionnelles, et les headers/footers.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from docx import Document
from docx.shared import RGBColor
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

logger = logging.getLogger(__name__)


class LOIGenerator:
    """Générateur de documents LOI depuis un template DOCX."""

    def __init__(
        self,
        variables: Dict[str, str],
        societes_info: Dict[str, Dict[str, str]],
        template_path: str = "Template LOI avec placeholder.docx"
    ):
        """
        Initialise le générateur.

        Args:
            variables: Dictionnaire des variables extraites
            societes_info: Informations des sociétés bailleures
            template_path: Chemin vers le template Word
        """
        self.variables = variables.copy()
        self.societes_info = societes_info
        self.template_path = Path(template_path)

        if not self.template_path.exists():
            raise FileNotFoundError(f"Template introuvable: {template_path}")

        # Normaliser les noms de variables (mapping)
        self._normalize_variable_names()

        # Pré-calculer les valeurs dérivées
        self._calculate_derived_values()

        logger.info("Générateur LOI initialisé")

    def _normalize_variable_names(self):
        """
        Normalise les noms de variables pour gérer les variations.
        Crée des alias pour les variables avec des noms légèrement différents.
        """
        # Mapping: Nom dans Excel → Nom dans Template
        mappings = {
            "Statut Locaux loués": "Statut Locaux Loués",
            "Durée ferme bail": "Durée ferme Bail",
            "Duré GAPD": "Durée GAPD",  # Typo dans l'ancien Excel
        }

        for excel_name, template_name in mappings.items():
            if excel_name in self.variables and template_name not in self.variables:
                self.variables[template_name] = self.variables[excel_name]
                logger.debug(f"Mapping: '{excel_name}' → '{template_name}'")

    def _calculate_derived_values(self):
        """Calcule les valeurs dérivées (paliers, adresse, type bail, etc.)."""

        # 1. Calculer les paliers (remises)
        self._calculate_paliers()

        # 2. Construire l'adresse complète
        self._build_address()

        # 3. Calculer le type de bail
        self._calculate_type_bail()

        # 4. Calculer la date de signature (Date d'aujourd'hui + 15 jours)
        self._calculate_date_signature()

        # 5. Calculer les surfaces
        self._calculate_surfaces()

    def _calculate_paliers(self):
        """Calcule les montants des paliers (remises) pour chaque année."""
        try:
            loyer_base_str = self.variables.get("Montant du loyer", "0").strip()
            # Nettoyer la valeur (retirer espaces, virgules)
            loyer_base_str = loyer_base_str.replace(" ", "").replace(",", "")

            try:
                loyer_base = float(loyer_base_str)
            except ValueError:
                logger.warning(f"Montant du loyer invalide: {loyer_base_str}")
                loyer_base = 0

            for annee in range(1, 7):
                loyer_annee_key = f"Loyer année {annee}"
                loyer_annee_str = self.variables.get(loyer_annee_key, "").strip()

                if loyer_annee_str:
                    # Nettoyer la valeur
                    loyer_annee_str = loyer_annee_str.replace(" ", "").replace(",", "")
                    try:
                        loyer_annee = float(loyer_annee_str)
                        remise = loyer_base - loyer_annee

                        if remise > 0:
                            # Formater avec espaces pour les milliers
                            self.variables[f"Montant du palier {annee}"] = f"{int(remise):,}".replace(",", " ")
                            logger.debug(f"Palier année {annee}: {int(remise):,} €")
                    except ValueError:
                        logger.warning(f"Loyer année {annee} invalide: {loyer_annee_str}")

        except Exception as e:
            logger.error(f"Erreur calcul des paliers: {e}")

    def _build_address(self):
        """Construit l'adresse complète des locaux loués."""
        ville = self.variables.get("Ville ou arrondissement", "")
        rue = self.variables.get("Numéro et rue", "")

        if ville and rue:
            self.variables["Adresse Locaux Loués"] = f"{rue}, {ville}"
        elif ville:
            self.variables["Adresse Locaux Loués"] = ville
        elif rue:
            self.variables["Adresse Locaux Loués"] = rue

    def _calculate_type_bail(self):
        """Calcule le type de bail selon la durée."""
        duree_bail = self.variables.get("Durée Bail", "").strip()

        if duree_bail:
            try:
                duree = int(float(duree_bail))
                if duree == 9:
                    self.variables["Type Bail"] = "3/6/9"
                elif duree == 10:
                    self.variables["Type Bail"] = "6/9/10"
                else:
                    self.variables["Type Bail"] = f"{duree} ans"
            except ValueError:
                pass

    def _calculate_date_signature(self):
        """Calcule la date de signature (Date d'aujourd'hui + 15 jours)."""
        date_aujourdhui_str = self.variables.get("Date d'aujourd'hui", "")

        if date_aujourdhui_str:
            try:
                # Parser DD/MM/YYYY
                date_aujourdhui = datetime.strptime(date_aujourdhui_str, "%d/%m/%Y")
                date_signature = date_aujourdhui + timedelta(days=15)
                self.variables["Date de signature"] = date_signature.strftime("%d/%m/%Y")
            except ValueError:
                pass

    def _calculate_surfaces(self):
        """Calcule la surface R-1 (total - RDC)."""
        try:
            surface_totale = self.variables.get("Surface totale", "").strip()
            surface_rdc = self.variables.get("Surface RDC", "").strip()

            if surface_totale and surface_rdc:
                surface_totale = float(surface_totale.replace(" ", "").replace(",", "."))
                surface_rdc = float(surface_rdc.replace(" ", "").replace(",", "."))
                surface_r1 = surface_totale - surface_rdc

                if surface_r1 > 0:
                    self.variables["Surface R-1"] = str(int(surface_r1))
        except ValueError:
            pass

    def _is_paragraph_optional(self, paragraph) -> bool:
        """
        Détecte si un paragraphe est optionnel (texte en bleu).

        Args:
            paragraph: Paragraphe docx

        Returns:
            True si le paragraphe est optionnel (bleu)
        """
        for run in paragraph.runs:
            if run.font.color and run.font.color.type == 1:  # RGB color
                rgb = run.font.color.rgb
                # Bleu: B > R et B > G
                # RGBColor est un tuple (R, G, B) indexable
                if rgb and len(rgb) >= 3:
                    r, g, b = rgb[0], rgb[1], rgb[2]
                    if b > r and b > g:
                        return True
        return False

    def _find_placeholders(self, text: str) -> List[str]:
        """
        Trouve tous les placeholders dans un texte.

        Args:
            text: Texte à analyser

        Returns:
            Liste des placeholders trouvés
        """
        return re.findall(r'\[([^\]]+)\]', text)

    def _has_data_for_placeholders(self, placeholders: List[str]) -> bool:
        """
        Vérifie si toutes les données sont disponibles pour les placeholders.

        Args:
            placeholders: Liste des placeholders

        Returns:
            True si toutes les données sont disponibles
        """
        for placeholder in placeholders:
            if placeholder not in self.variables or not self.variables[placeholder]:
                return False
        return True

    def _replace_placeholders_in_text(self, text: str) -> Tuple[str, bool]:
        """
        Remplace les placeholders dans un texte.

        Args:
            text: Texte contenant des placeholders

        Returns:
            Tuple (texte_modifié, données_manquantes)
        """
        placeholders = self._find_placeholders(text)
        missing_data = False

        for placeholder in placeholders:
            value = self.variables.get(placeholder, "")
            if value:
                text = text.replace(f"[{placeholder}]", value)
            else:
                missing_data = True

        return text, missing_data

    def _process_paragraph(self, paragraph) -> Optional[str]:
        """
        Traite un paragraphe: remplace les placeholders ou le supprime.

        Args:
            paragraph: Paragraphe docx

        Returns:
            "delete" si le paragraphe doit être supprimé, None sinon
        """
        text = paragraph.text
        placeholders = self._find_placeholders(text)

        if not placeholders:
            return None

        is_optional = self._is_paragraph_optional(paragraph)
        has_data = self._has_data_for_placeholders(placeholders)

        # Section optionnelle sans données → Supprimer
        if is_optional and not has_data:
            logger.debug(f"Suppression paragraphe optionnel: {text[:50]}...")
            return "delete"

        # Remplacer les placeholders dans les runs
        for run in paragraph.runs:
            original_text = run.text

            # Section optionnelle avec données → Mettre TOUT en noir
            if is_optional and has_data:
                run.font.color.rgb = RGBColor(0, 0, 0)

            # Remplacer les placeholders
            new_text = original_text
            run_missing_data = False

            # Trouver les placeholders dans ce run spécifique
            run_placeholders = self._find_placeholders(original_text)

            for placeholder in run_placeholders:
                value = self.variables.get(placeholder, "")
                if value:
                    new_text = new_text.replace(f"[{placeholder}]", value)
                else:
                    run_missing_data = True

            run.text = new_text

            # Section obligatoire avec placeholder manquant → Mettre SEULEMENT les placeholders en rouge
            if not is_optional and run_missing_data:
                # Recréer le run avec des parties en rouge pour les placeholders
                run.text = ""
                parts = []
                current_pos = 0

                # Parser le texte pour identifier les placeholders
                import re
                for match in re.finditer(r'\[([^\]]+)\]', original_text):
                    placeholder = match.group(1)
                    start, end = match.span()

                    # Ajouter le texte avant le placeholder (en noir)
                    if start > current_pos:
                        parts.append(('black', original_text[current_pos:start]))

                    # Ajouter le placeholder
                    value = self.variables.get(placeholder, "")
                    if value:
                        parts.append(('black', value))
                    else:
                        parts.append(('red', f"[{placeholder}]"))

                    current_pos = end

                # Ajouter le reste du texte (en noir)
                if current_pos < len(original_text):
                    parts.append(('black', original_text[current_pos:]))

                # Reconstruire le run avec les bonnes couleurs
                if parts:
                    # Utiliser le premier élément pour le run actuel
                    first_color, first_text = parts[0]
                    run.text = first_text
                    if first_color == 'red':
                        run.font.color.rgb = RGBColor(255, 0, 0)
                    else:
                        run.font.color.rgb = RGBColor(0, 0, 0)

                    # Ajouter les autres parties comme de nouveaux runs
                    for color, text in parts[1:]:
                        new_run = paragraph.add_run(text)
                        if color == 'red':
                            new_run.font.color.rgb = RGBColor(255, 0, 0)
                        else:
                            new_run.font.color.rgb = RGBColor(0, 0, 0)
                        # Copier le formatage du run original
                        new_run.font.name = run.font.name
                        new_run.font.size = run.font.size
                        new_run.font.bold = run.font.bold
                        new_run.font.italic = run.font.italic

                if run_missing_data:
                    logger.warning(f"Placeholder manquant (rouge): {text[:50]}...")

        return None

    def _update_headers_footers(self, doc: Document):
        """
        Met à jour les headers et footers selon la société bailleur.
        Ne touche PAS à la structure existante, remplace juste le contenu texte.

        Args:
            doc: Document docx
        """
        societe_bailleur = self.variables.get("Société Bailleur", "")

        if not societe_bailleur or societe_bailleur not in self.societes_info:
            logger.warning(f"Société bailleur '{societe_bailleur}' non trouvée dans la config")
            return

        societe_info = self.societes_info[societe_bailleur]
        header_text = societe_info.get("header", "")
        footer_text = societe_info.get("footer", "")

        from docx.shared import Pt
        from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

        # Mettre à jour tous les headers et footers
        for section in doc.sections:
            # Header
            if header_text:
                header = section.header

                # Supprimer tous les paragraphes existants
                for para in list(header.paragraphs):
                    p = para._element
                    p.getparent().remove(p)

                # Créer un nouveau paragraphe avec le bon formatage
                para = header.add_paragraph()
                para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                run = para.add_run(header_text)
                run.font.bold = True
                run.font.size = Pt(12)

            # Footer
            if footer_text:
                footer = section.footer

                # Supprimer tous les paragraphes existants
                for para in list(footer.paragraphs):
                    p = para._element
                    p.getparent().remove(p)

                # Le footer peut avoir plusieurs lignes
                lines = footer_text.split("\n")
                for i, line in enumerate(lines):
                    para = footer.add_paragraph()
                    para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    run = para.add_run(line)
                    run.font.size = Pt(9)

        logger.info(f"Headers/Footers mis à jour pour: {societe_bailleur}")

    def generate(self, output_path: str) -> str:
        """
        Génère le document LOI final.

        Args:
            output_path: Chemin du fichier de sortie

        Returns:
            Chemin du fichier généré
        """
        logger.info(f"Génération du document LOI: {output_path}")

        # Charger le template
        doc = Document(str(self.template_path))

        # Première passe: identifier les sections à garder
        # Pour les paragraphes comme "Remises..." qui n'ont pas de placeholder mais contrôlent une section
        paragraphs_with_data = set()
        all_paragraphs = doc.paragraphs

        # Détecter si les paliers ont des données
        has_palier_data = any(
            self.variables.get(f"Montant du palier {i}", "")
            for i in range(1, 7)
        )

        # Détecter si les conditions suspensives ont des données
        has_conditions_data = any(
            self.variables.get(f"Condition suspensive {i}", "")
            for i in range(1, 5)
        )

        # Traiter tous les paragraphes
        paragraphs_to_delete = []
        for i, paragraph in enumerate(all_paragraphs):
            text = paragraph.text
            is_optional = self._is_paragraph_optional(paragraph)

            # Cas spéciaux: paragraphes de titre sans placeholder
            if is_optional and not self._find_placeholders(text):
                # "Remises (sur loyer annuel indexé) :"
                if "Remises" in text and "loyer" in text:
                    if has_palier_data:
                        # Garder ce paragraphe et le mettre en noir
                        for run in paragraph.runs:
                            run.font.color.rgb = RGBColor(0, 0, 0)
                    else:
                        paragraphs_to_delete.append(paragraph)
                    continue

                # "Condition(s) suspensive(s)"
                if "Condition" in text and "suspensive" in text:
                    if has_conditions_data:
                        # Garder ce paragraphe et le mettre en noir
                        for run in paragraph.runs:
                            run.font.color.rgb = RGBColor(0, 0, 0)
                    else:
                        paragraphs_to_delete.append(paragraph)
                    continue

            # Traitement normal
            result = self._process_paragraph(paragraph)
            if result == "delete":
                paragraphs_to_delete.append(paragraph)

        # Supprimer les paragraphes marqués
        for paragraph in paragraphs_to_delete:
            p = paragraph._element
            p.getparent().remove(p)

        # Traiter les tableaux
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    cells_to_delete = []
                    for paragraph in cell.paragraphs:
                        result = self._process_paragraph(paragraph)
                        if result == "delete":
                            cells_to_delete.append(paragraph)

                    # Supprimer les paragraphes dans les cellules
                    for paragraph in cells_to_delete:
                        p = paragraph._element
                        p.getparent().remove(p)

        # Mettre à jour les headers/footers
        self._update_headers_footers(doc)

        # Sauvegarder
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(output_path))

        logger.info(f"Document généré: {output_path}")
        return str(output_path)
