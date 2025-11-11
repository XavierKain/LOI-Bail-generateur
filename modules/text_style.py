"""
Module pour gérer les styles de texte depuis Excel vers Word.
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class TextStyle:
    """
    Représente le style d'un texte (police, gras, italique, etc.).
    Compatible avec openpyxl (Excel) et python-docx (Word).
    """

    text: str
    bold: bool = False
    italic: bool = False
    underline: bool = False
    font_name: Optional[str] = None
    font_size: Optional[float] = None  # En points
    color_rgb: Optional[str] = None  # Format: 'RRGGBB'

    @classmethod
    def from_excel_cell(cls, cell) -> 'TextStyle':
        """
        Crée un TextStyle depuis une cellule Excel (openpyxl).

        Args:
            cell: Cellule openpyxl

        Returns:
            TextStyle avec les propriétés de la cellule
        """
        # Extraire le texte
        text = ""
        if cell.value is not None:
            text = str(cell.value)

        # Extraire le style
        bold = False
        italic = False
        underline = False
        font_name = None
        font_size = None
        color_rgb = None

        if cell.font:
            bold = cell.font.bold or False
            italic = cell.font.italic or False
            underline = cell.font.underline is not None and cell.font.underline != 'none'
            font_name = cell.font.name
            font_size = cell.font.size

            # Extraire la couleur
            if cell.font.color:
                if cell.font.color.rgb:
                    # Format: '00RRGGBB' -> 'RRGGBB'
                    color_rgb = str(cell.font.color.rgb)
                    if len(color_rgb) == 8 and color_rgb.startswith('00'):
                        color_rgb = color_rgb[2:]

        return cls(
            text=text,
            bold=bold,
            italic=italic,
            underline=underline,
            font_name=font_name,
            font_size=font_size,
            color_rgb=color_rgb
        )

    def apply_to_word_run(self, run):
        """
        Applique ce style à un run Word (python-docx).

        Args:
            run: Run python-docx
        """
        from docx.shared import Pt, RGBColor

        if self.bold:
            run.bold = True

        if self.italic:
            run.italic = True

        if self.underline:
            run.underline = True

        if self.font_name:
            run.font.name = self.font_name

        if self.font_size:
            run.font.size = Pt(self.font_size)

        if self.color_rgb and len(self.color_rgb) == 6:
            try:
                r = int(self.color_rgb[0:2], 16)
                g = int(self.color_rgb[2:4], 16)
                b = int(self.color_rgb[4:6], 16)
                run.font.color.rgb = RGBColor(r, g, b)
            except ValueError:
                pass  # Couleur invalide, ignorer

    def __str__(self):
        """Représentation string pour debug."""
        styles = []
        if self.bold:
            styles.append("bold")
        if self.italic:
            styles.append("italic")
        if self.underline:
            styles.append("underline")
        if self.font_name:
            styles.append(f"font:{self.font_name}")
        if self.font_size:
            styles.append(f"size:{self.font_size}")

        style_str = ", ".join(styles) if styles else "no style"
        return f"TextStyle({self.text[:30]}... [{style_str}])"


class RichTextStyle:
    """
    Représente du texte avec plusieurs styles (rich text depuis Excel).
    Contient une liste de TextStyle, un par segment de texte.
    """

    def __init__(self, text_parts: List[TextStyle]):
        """
        Initialise un RichTextStyle.

        Args:
            text_parts: Liste de TextStyle représentant les différents segments
        """
        self.text_parts = text_parts

    @property
    def full_text(self) -> str:
        """Retourne le texte complet en concaténant tous les segments."""
        return "".join(part.text for part in self.text_parts)

    @classmethod
    def from_excel_rich_text(cls, rich_text) -> 'RichTextStyle':
        """
        Crée un RichTextStyle depuis un CellRichText d'openpyxl.

        Args:
            rich_text: objet CellRichText d'openpyxl

        Returns:
            RichTextStyle avec tous les segments
        """
        from openpyxl.cell.rich_text import TextBlock

        text_parts = []

        for item in rich_text:
            if isinstance(item, str):
                # Segment de texte simple sans formatage
                text_parts.append(TextStyle(
                    text=item,
                    bold=False,
                    italic=False,
                    underline=False
                ))
            elif isinstance(item, TextBlock):
                # Segment avec formatage
                bold = item.font.b if item.font and item.font.b else False
                italic = item.font.i if item.font and item.font.i else False
                underline = item.font.u is not None if item.font else False
                font_name = item.font.name if item.font else None
                font_size = item.font.sz if item.font else None

                # Couleur
                color_rgb = None
                if item.font and item.font.color and item.font.color.rgb:
                    color_rgb = str(item.font.color.rgb)
                    if len(color_rgb) == 8 and color_rgb.startswith('00'):
                        color_rgb = color_rgb[2:]

                text_parts.append(TextStyle(
                    text=item.text,
                    bold=bold,
                    italic=italic,
                    underline=underline,
                    font_name=font_name,
                    font_size=font_size,
                    color_rgb=color_rgb
                ))

        return cls(text_parts)

    def apply_to_word_paragraph(self, paragraph):
        """
        Applique ce rich text à un paragraphe Word en créant plusieurs runs.

        Args:
            paragraph: Paragraphe python-docx
        """
        # Vider le paragraphe existant
        for run in paragraph.runs:
            run.text = ""

        # Créer un run pour chaque segment
        for part in self.text_parts:
            run = paragraph.add_run(part.text)
            part.apply_to_word_run(run)

    def __str__(self):
        """Représentation string pour debug."""
        return f"RichTextStyle({len(self.text_parts)} parts: {self.full_text[:50]}...)"
