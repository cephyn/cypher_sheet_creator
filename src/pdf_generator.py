"""
PDF Generator module for creating attractive, compact, landscape character sheets.
"""

from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, grey, black, white
from reportlab.platypus import (
    BaseDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
    Frame,
    PageTemplate,
    KeepTogether,
)
from typing import Dict, List, Any, Sequence
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
        # Page/layout measurements
        self.pagesize = landscape(letter)
        self.page_width, self.page_height = self.pagesize
        # Compact margins and panel sizes to reduce wasted space
        self.margin = 0.3 * inch
        self.header_height = 0.0 * inch  # no banner header in compact mode
        self.top_panel_height = 0.9 * inch  # compact top panel for name + attributes

        # Build document with custom frames and a page template
        self.doc = BaseDocTemplate(
            output_path,
            pagesize=self.pagesize,
            leftMargin=self.margin,
            rightMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=0.45 * inch,  # a bit more room for footer
        )
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        self.story = []

        self._init_page_template()

    def _create_custom_styles(self):
        """Create custom paragraph styles."""
        # Compact title/subtitle styles
        self.styles.add(
            ParagraphStyle(
                name="CompactTitle",
                parent=self.styles["Normal"],
                fontSize=16,
                textColor=self.colors["primary"],
                spaceAfter=0,
                leading=17,
                fontName="Helvetica-Bold",
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="CompactSubtitle",
                parent=self.styles["Normal"],
                fontSize=9.5,
                textColor=grey,
                spaceAfter=2,
                leading=11,
                fontName="Helvetica",
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Normal"],
                fontSize=9.5,
                textColor=white,
                spaceAfter=4,
                leading=11,
                fontName="Helvetica-Bold",
                backColor=self.colors["secondary"],
                leftIndent=3,
                rightIndent=3,
                topPadding=2,
                bottomPadding=2,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="SubsectionHeader",
                parent=self.styles["Normal"],
                fontSize=9,
                textColor=self.colors["secondary"],
                spaceAfter=2,
                leading=10,
                fontName="Helvetica-Bold",
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="Normal2",
                parent=self.styles["Normal"],
                fontSize=8.4,
                leading=10.0,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="AbilityName",
                parent=self.styles["Normal"],
                fontSize=9,
                textColor=self.colors["primary"],
                spaceAfter=1,
                leading=10,
                fontName="Helvetica-Bold",
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="Footer",
                parent=self.styles["Normal"],
                fontSize=7.8,
                leading=9,
                textColor=grey,
            )
        )

        # Muted, compact subsection header for background/notes (black, not blue)
        self.styles.add(
            ParagraphStyle(
                name="MinorHeader",
                parent=self.styles["Normal"],
                fontSize=8.8,
                leading=10.2,
                textColor=black,
                fontName="Helvetica-Bold",
                spaceBefore=0,
                spaceAfter=2,
            )
        )
        # Notes header even lighter (non-bold) for compact look
        self.styles.add(
            ParagraphStyle(
                name="NotesHeader",
                parent=self.styles["Normal2"],
                fontSize=8.4,
                leading=10.0,
                textColor=black,
                fontName="Helvetica",
                spaceBefore=0,
                spaceAfter=1,
            )
        )

    def _init_page_template(self):
        """Define frames and page templates for landscape, 2-column layout with header/footer."""
        avail_width = self.page_width - (2 * self.margin)
        gutter = 0.18 * inch
        # 60/40 split columns for better fit (abilities/attacks vs skills/cyphers/equipment)
        col1_width = avail_width * 0.6
        col2_width = avail_width - gutter - col1_width

        # Top panel for attributes, directly under the header banner
        top_y = (
            self.page_height - self.margin - self.header_height - self.top_panel_height
        )
        frame_top = Frame(
            self.margin,
            top_y,
            avail_width,
            self.top_panel_height,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
            id="top",
        )

        # Two columns area for the rest of the content
        cols_height = top_y - self.margin
        frame_col1 = Frame(
            self.margin,
            self.margin,
            col1_width,
            cols_height,
            leftPadding=0,
            rightPadding=6,
            topPadding=0,
            bottomPadding=0,
            id="col1",
        )
        frame_col2 = Frame(
            self.margin + col1_width + gutter,
            self.margin,
            col2_width,
            cols_height,
            leftPadding=6,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
            id="col2",
        )

        template = PageTemplate(
            id="landscape_two_col",
            frames=[frame_top, frame_col1, frame_col2],
            # no banner/footer in compact mode to save space
        )
        self.doc.addPageTemplates([template])

    def _draw_header_footer(self, canvas, doc):
        """Draw a colored header banner with name/subtitle and a light footer with page info."""
        canvas.saveState()

        # Header banner background
        header_y = self.page_height - self.margin - self.header_height
        canvas.setFillColor(self.colors["secondary"])
        canvas.rect(
            self.margin,
            header_y,
            self.page_width - 2 * self.margin,
            self.header_height,
            fill=1,
            stroke=0,
        )

        header_data = self.data.get("header", {})
        name = header_data.get("name", "Unknown")
        char_type = header_data.get("type", "")
        focus = header_data.get("focus", "")
        flavor = header_data.get("flavor", "")
        world = header_data.get("world", "")

        subtitle = char_type
        if focus:
            subtitle += f" — {focus}"
        if flavor:
            subtitle += f" — {flavor}"
        if world:
            subtitle += f" ({world})"

        # Header text
        canvas.setFillColor(white)
        canvas.setFont("Helvetica-Bold", 20)
        canvas.drawString(self.margin + 8, header_y + self.header_height - 24, name)
        canvas.setFont("Helvetica", 10.5)
        canvas.drawString(self.margin + 8, header_y + 10, subtitle)

        # Footer
        canvas.setFillColor(grey)
        canvas.setFont("Helvetica", 8)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        footer_left = f"Generated: {ts}"
        footer_right = f"Page {doc.page}"
        canvas.drawString(self.margin, self.margin - 0.3 * inch + 10, footer_left)
        canvas.drawRightString(
            self.page_width - self.margin, self.margin - 0.3 * inch + 10, footer_right
        )

        canvas.restoreState()

    def generate(self):
        """Generate the complete PDF in a compact, landscape two-column layout."""
        # Top panel content: compact name/subtitle line + attributes
        self._add_compact_header_line()
        self._add_attributes_section()

        # Columnar content
        # Left column preferred: abilities, attacks
        self._add_special_abilities()
        self._add_attacks()

        # Right column preferred: skills, cyphers, equipment
        self._add_skills()
        self._add_cyphers()
        self._add_equipment()

        # Continue on subsequent pages as needed
        self._add_background()
        self._add_notes()

        self.doc.build(self.story)

    # Compact header is added as flowables in the top frame

    def _add_compact_header_line(self):
        header_data = self.data.get("header", {})
        name = header_data.get("name", "Unknown")
        char_type = header_data.get("type", "")
        focus = header_data.get("focus", "")
        flavor = header_data.get("flavor", "")
        world = header_data.get("world", "")

        parts = [p for p in [char_type, focus, flavor] if p]
        subtitle = " — ".join(parts)
        if world:
            subtitle += f" ({world})"

        self.story.append(
            Paragraph(name, self.styles.get("CompactTitle", self.styles["Title"]))
        )
        if subtitle.strip():
            self.story.append(
                Paragraph(
                    subtitle, self.styles.get("CompactSubtitle", self.styles["Normal"])
                )
            )
        # thin rule
        rule = Table([[""]], colWidths=[self.page_width - 2 * self.margin])
        rule.setStyle(
            TableStyle(
                [
                    ("LINEBELOW", (0, 0), (-1, -1), 0.5, grey),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )
        self.story.append(rule)

    def _add_attributes_section(self):
        """Add a compact top panel with attributes and secondary stats as a card row."""
        attrs = self.data.get("attributes", {})

        # Section header (subtle since header banner already present)
        self.story.append(Paragraph("ATTRIBUTES", self.styles["SectionHeader"]))

        # Build three attribute "cards"
        cards: List[Any] = []
        for attr_key, display in [
            ("might", "Might"),
            ("speed", "Speed"),
            ("intellect", "Intellect"),
        ]:
            if attr_key in attrs:
                a = attrs[attr_key]
                card_tbl = Table(
                    [
                        [
                            Paragraph(
                                f"<b>{display}</b>", self.styles["SubsectionHeader"]
                            )
                        ],
                        [
                            Table(
                                [
                                    ["Pool", str(a.get("pool", ""))],
                                    ["Edge", str(a.get("edge", ""))],
                                    ["Defense", a.get("defense", "")],
                                ],
                                colWidths=[0.8 * inch, 0.8 * inch],
                                style=TableStyle(
                                    [
                                        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                                        ("FONTSIZE", (0, 0), (-1, -1), 8.2),
                                        ("TEXTCOLOR", (0, 0), (0, -1), grey),
                                        ("TEXTCOLOR", (1, 0), (1, -1), black),
                                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                                        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                                    ]
                                ),
                            )
                        ],
                    ],
                    colWidths=[1.85 * inch],
                )
                card_tbl.setStyle(
                    TableStyle(
                        [
                            ("BOX", (0, 0), (-1, -1), 0.5, grey),
                            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#F2F7FB")),
                            ("LEFTPADDING", (0, 0), (-1, -1), 5),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                            ("TOPPADDING", (0, 0), (-1, -1), 3),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                        ]
                    )
                )
                cards.append(card_tbl)

        # Place the three cards in a single row
        if cards:
            # If fewer than 3, still render nicely
            while len(cards) < 3:
                cards.append(Spacer(1, 0))
            cards_row = Table(
                [cards], colWidths=[1.95 * inch, 1.95 * inch, 1.95 * inch]
            )
            cards_row.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 2),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                    ]
                )
            )
            self.story.append(cards_row)

        # Secondary stats inline line to save vertical space
        chips = []
        if "effort" in attrs:
            chips.append(f"<b>Effort:</b> {attrs['effort']}")
        if "armor" in attrs:
            chips.append(f"<b>Armor:</b> {attrs['armor']}")
        if "initiative" in attrs:
            chips.append(f"<b>Initiative:</b> {attrs['initiative']}")
        if "xp" in attrs:
            chips.append(f"<b>XP:</b> {attrs['xp']}")
        if "recovery_roll" in attrs:
            chips.append(f"<b>Recovery:</b> {attrs['recovery_roll']}")
        if chips:
            self.story.append(Spacer(1, 0.03 * inch))
            self.story.append(Paragraph(" | ".join(chips), self.styles["Normal2"]))
            self.story.append(Spacer(1, 0.04 * inch))

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
            self.story.append(Spacer(1, 0.06 * inch))

    def _add_skills(self):
        """Add skills section."""
        if not self.data["skills"]:
            return

        self.story.append(Paragraph("SKILLS", self.styles["SectionHeader"]))

        for skill in self.data["skills"]:
            skill_level = skill.get("level", "")
            desc = " ".join(skill.get("description", []))
            label = (
                f"<b>{skill['name']}</b> ({skill_level}): {desc}"
                if desc
                else f"<b>{skill['name']}</b> ({skill_level})"
            )
            self.story.append(Paragraph("• " + label, self.styles["Normal2"]))
        self.story.append(Spacer(1, 0.06 * inch))

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
            self.story.append(Spacer(1, 0.06 * inch))

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

        for it in self.data["equipment"]:
            self.story.append(Paragraph("• " + str(it), self.styles["Normal2"]))
        self.story.append(Spacer(1, 0.06 * inch))

    def _add_background(self):
        """Add background section on second page."""
        if not self.data["background"]:
            return
        self.story.append(Paragraph("BACKGROUND", self.styles["SectionHeader"]))

        # Render each background subsection like a special ability: bold
        # subsection header then a compact paragraph body (no bullets).
        for subsection, content in self.data["background"].items():
            if subsection.strip():
                self.story.append(
                    Paragraph(subsection, self.styles["SubsectionHeader"])
                )
            # content is a list of paragraph strings
            for para in content:
                if para and para.strip():
                    self.story.append(Paragraph(para, self.styles["Normal2"]))
            # small spacer to separate subsections
            self.story.append(Spacer(1, 0.04 * inch))

    def _add_notes(self):
        """Add notes section."""
        if not self.data["notes"]:
            return

        self.story.append(Paragraph("NOTES", self.styles["SectionHeader"]))

        # Render notes similar to abilities/cyphers: subsection title in bold
        # style then a compact paragraph block. Avoid per-line bullets.
        for subsection, content in self.data["notes"].items():
            if subsection.strip():
                self.story.append(
                    Paragraph(subsection, self.styles["SubsectionHeader"])
                )
            for para in content:
                if para and para.strip():
                    self.story.append(Paragraph(para, self.styles["Normal2"]))
            self.story.append(Spacer(1, 0.04 * inch))

    def _flowables_to_columns(self, items: Sequence[Any], ncols: int = 2):
        """Arrange a list of flowables into a compact table with n columns.
        Returns a Flowable (Table or Spacer)."""
        if not items:
            return Spacer(1, 0)
        rows = (len(items) + ncols - 1) // ncols
        cols: List[List[Any]] = [[] for _ in range(ncols)]
        for i, item in enumerate(items):
            cols[i % ncols].append(item)
        # Pad columns to equal rows
        for c in cols:
            while len(c) < rows:
                c.append(Spacer(1, 0))
        # Transpose to rows
        table_rows = list(zip(*cols))
        col_width = (self.page_width - 2 * self.margin - 0.25 * inch) / ncols
        tbl = Table(table_rows, colWidths=[col_width] * ncols)
        tbl.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 1),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ]
            )
        )
        return tbl
