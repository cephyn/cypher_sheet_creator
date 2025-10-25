"""
PDF Generator module for creating stylish character sheets.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, grey, black, white
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
)
from reportlab.platypus import KeepTogether
from typing import Dict, List, Any
from datetime import datetime


class CypherCharacterSheetPDF:
    """Generates a professional PDF from parsed character sheet data."""

    def __init__(self, data: Dict[str, Any], output_path: str):
        self.data = data
        self.output_path = output_path
        self.colors = {
            "primary": HexColor("#2C3E50"),
            "secondary": HexColor("#3498DB"),
            "accent": HexColor("#E74C3C"),
            "light_bg": HexColor("#ECF0F1"),
            "text": HexColor("#2C3E50"),
        }
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
        )
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        self.story = []

    def _create_custom_styles(self):
        """Create custom paragraph styles."""
        self.styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=self.styles["Normal"],
                fontSize=18,
                textColor=self.colors["primary"],
                spaceAfter=6,
                leading=20,
                fontName="Helvetica-Bold",
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Normal"],
                fontSize=12,
                textColor=white,
                spaceAfter=8,
                leading=14,
                fontName="Helvetica-Bold",
                backColor=self.colors["secondary"],
                leftIndent=6,
                rightIndent=6,
                topPadding=4,
                bottomPadding=4,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="SubsectionHeader",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=self.colors["secondary"],
                spaceAfter=6,
                leading=12,
                fontName="Helvetica-Bold",
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="Normal2",
                parent=self.styles["Normal"],
                fontSize=9,
                leading=11,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="AbilityName",
                parent=self.styles["Normal"],
                fontSize=9,
                textColor=self.colors["primary"],
                spaceAfter=2,
                leading=10,
                fontName="Helvetica-Bold",
            )
        )

    def generate(self):
        """Generate the complete PDF."""
        self._add_header()
        self._add_attributes_section()
        self._add_special_abilities()
        self._add_skills()
        self._add_attacks()
        self._add_cyphers()
        self._add_equipment()
        self.story.append(PageBreak())
        self._add_background()
        self._add_notes()

        self.doc.build(self.story)

    def _add_header(self):
        """Add character header with name and descriptors."""
        header_data = self.data["header"]
        name = header_data.get("name", "Unknown")
        char_type = header_data.get("type", "")
        focus = header_data.get("focus", "")
        flavor = header_data.get("flavor", "")
        world = header_data.get("world", "")

        title_text = f"<b>{name}</b>"
        self.story.append(Paragraph(title_text, self.styles["CustomTitle"]))

        subtitle = f"{char_type}"
        if focus:
            subtitle += f" &mdash; {focus}"
        if flavor:
            subtitle += f" &mdash; {flavor}"
        if world:
            subtitle += f" ({world})"

        self.story.append(Paragraph(subtitle, self.styles["Normal2"]))
        self.story.append(Spacer(1, 0.15 * inch))

    def _add_attributes_section(self):
        """Add pools, edges, defenses, and other attributes."""
        attrs = self.data["attributes"]

        self.story.append(Paragraph("ATTRIBUTES", self.styles["SectionHeader"]))

        # Create attribute table
        attr_data = [["Attribute", "Pool", "Edge", "Defense"]]

        for attr_name in ["might", "speed", "intellect"]:
            if attr_name in attrs:
                attr_info = attrs[attr_name]
                attr_data.append(
                    [
                        attr_name.capitalize(),
                        str(attr_info["pool"]),
                        str(attr_info["edge"]),
                        attr_info["defense"],
                    ]
                )

        attr_table = Table(
            attr_data, colWidths=[1.5 * inch, 0.8 * inch, 0.6 * inch, 1.2 * inch]
        )
        attr_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), self.colors["light_bg"]),
                    ("TEXTCOLOR", (0, 0), (-1, 0), self.colors["primary"]),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, grey),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, HexColor("#F8F9FA")]),
                ]
            )
        )
        self.story.append(attr_table)
        self.story.append(Spacer(1, 0.1 * inch))

        # Other attributes
        other_attrs = []
        if "effort" in attrs:
            other_attrs.append(f"<b>Effort:</b> {attrs['effort']}")
        if "armor" in attrs:
            other_attrs.append(f"<b>Armor:</b> {attrs['armor']}")
        if "initiative" in attrs:
            other_attrs.append(f"<b>Initiative:</b> {attrs['initiative']}")
        if "xp" in attrs:
            other_attrs.append(f"<b>XP:</b> {attrs['xp']}")

        if other_attrs:
            self.story.append(
                Paragraph(" | ".join(other_attrs), self.styles["Normal2"])
            )
            self.story.append(Spacer(1, 0.15 * inch))

    def _add_special_abilities(self):
        """Add special abilities section."""
        if not self.data["special_abilities"]:
            return

        self.story.append(Paragraph("SPECIAL ABILITIES", self.styles["SectionHeader"]))

        for ability in self.data["special_abilities"]:
            self.story.append(
                Paragraph(ability["name"], self.styles["SubsectionHeader"])
            )
            desc = " ".join(ability["description"])
            self.story.append(Paragraph(desc, self.styles["Normal2"]))
            self.story.append(Spacer(1, 0.08 * inch))

    def _add_skills(self):
        """Add skills section."""
        if not self.data["skills"]:
            return

        self.story.append(Paragraph("SKILLS", self.styles["SectionHeader"]))

        skill_data = []
        for skill in self.data["skills"]:
            skill_level = skill["level"]
            desc = " ".join(skill["description"]) if skill["description"] else ""

            if desc:
                skill_text = f"<b>{skill['name']}</b> ({skill_level}): {desc}"
            else:
                skill_text = f"<b>{skill['name']}</b> ({skill_level})"

            skill_data.append(skill_text)

        for skill_text in skill_data:
            self.story.append(Paragraph(skill_text, self.styles["Normal2"]))

        self.story.append(Spacer(1, 0.15 * inch))

    def _add_attacks(self):
        """Add attacks section."""
        if not self.data["attacks"]:
            return

        self.story.append(Paragraph("ATTACKS", self.styles["SectionHeader"]))

        for attack in self.data["attacks"]:
            self.story.append(
                Paragraph(attack["name"], self.styles["SubsectionHeader"])
            )
            desc = " ".join(attack["description"])
            self.story.append(Paragraph(desc, self.styles["Normal2"]))
            self.story.append(Spacer(1, 0.08 * inch))

    def _add_cyphers(self):
        """Add cyphers section."""
        if not self.data["cyphers"]:
            return

        self.story.append(Paragraph("CYPHERS", self.styles["SectionHeader"]))

        for cypher in self.data["cyphers"]:
            cypher_header = (
                f"{cypher['name']} (Level {cypher['level']}, {cypher['type']})"
            )
            self.story.append(Paragraph(cypher_header, self.styles["SubsectionHeader"]))
            desc = " ".join(cypher["description"])
            self.story.append(Paragraph(desc, self.styles["Normal2"]))
            self.story.append(Spacer(1, 0.08 * inch))

    def _add_equipment(self):
        """Add equipment section."""
        if not self.data["equipment"]:
            return

        self.story.append(Paragraph("EQUIPMENT", self.styles["SectionHeader"]))

        for item in self.data["equipment"]:
            item_text = f"• {item}"
            self.story.append(Paragraph(item_text, self.styles["Normal2"]))

        self.story.append(Spacer(1, 0.15 * inch))

    def _add_background(self):
        """Add background section on second page."""
        if not self.data["background"]:
            return

        self.story.append(Paragraph("BACKGROUND", self.styles["SectionHeader"]))

        for subsection, content in self.data["background"].items():
            self.story.append(Paragraph(subsection, self.styles["SubsectionHeader"]))
            text = " ".join(content)
            self.story.append(Paragraph(text, self.styles["Normal2"]))
            self.story.append(Spacer(1, 0.1 * inch))

    def _add_notes(self):
        """Add notes section."""
        if not self.data["notes"]:
            return

        self.story.append(Paragraph("NOTES", self.styles["SectionHeader"]))

        for subsection, content in self.data["notes"].items():
            self.story.append(Paragraph(subsection, self.styles["SubsectionHeader"]))
            for note in content:
                self.story.append(Paragraph(f"• {note}", self.styles["Normal2"]))
            self.story.append(Spacer(1, 0.08 * inch))
