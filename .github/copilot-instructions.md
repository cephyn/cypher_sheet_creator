# Copilot Instructions for cypher_sheet_creator

These instructions help AI coding agents work effectively in this repository. Keep changes grounded in the current code, patterns, and workflows below.

## Big picture
- Purpose: Convert structured Cypher System character sheet text files (examples/*.txt) into compact, professional PDFs (output/*.pdf).
- Flow:
  1) main.py scans examples/, reads text
  2) src/parser.py parses to a structured dict
  3) src/pdf_generator.py renders a 2‑column landscape PDF with ReportLab
  4) src/renderer.py (utility) renders debug PNGs and whitespace metrics
- Output: PDFs to output/, PNG previews to output/png_debug/, temp PDFs to output/_debug_pdf/.

## Key modules and data shapes
- parser.py → CharacterSheetParser.parse() returns a dict with keys:
  - header: {name, type, focus, flavor, world}
  - attributes: {might, speed, intellect, effort, armor, initiative, recovery_roll}
  - special_abilities: [{name, description: [str, ...]}]
  - skills: [{name, level, description: [str, ...]}]
  - attacks: [{name, description: [str, ...]}]
  - cyphers: [{name, level, type, description: [str, ...]}]
  - equipment: [str]
  - advancements: {tier, choices: [str]}
  - background: {subsection: [paragraph, ...]}
  - notes: {subsection: [paragraph, ...]}
- pdf_generator.py consumes exactly that schema. Adding/removing fields requires updating both parser and generator.

## Parsing conventions (project-specific)
- Sections are delimited by exact headers (case-insensitive) like "Special Abilities", "Skills", ... See parser._get_section_content().
- Subheaders within sections are non-indented, short lines detected heuristically.
  - Attacks: non‑indented short titles; punctuation like &, -, ', /, +, digits are allowed (see looks_like_attack_header).
  - Cyphers: header format is "<Name (optional tags)> (Level N, Type)" — the parser captures any name prefix before the (Level...).
  - Background: subsection headers use _looks_like_subsection_header(); body lines are merged into paragraphs.
  - Notes: blocks split on blank lines; first line is header, following lines merged.
- Wrapped lines and hyphenation are merged by _merge_lines_into_paragraphs().

## PDF layout conventions (project-specific)
- Landscape letter, margins ~0.3", two columns (60/40 split). First page has a compact header + advancement panel, then columns.
- Section and subsection flows:
  - Headers use keepWithNext where possible; subheader + first paragraph are wrapped in KeepTogether.
  - Section header + first content are also wrapped in KeepTogether for Cyphers and Background to avoid stranded headers at column bottoms.
- Styles: defined in _create_custom_styles(); key styles include SectionHeader, SubsectionHeader, Normal2. Colors: primary #2C3E50, secondary #3498DB.

## Developer workflows
- Run locally (Windows PowerShell shown):
  - Create/activate venv and install deps: see QUICK_START.md.
  - Generate all PDFs: `python main.py` (writes to output/ and debug PNGs).
- Debug rendering:
  - main.py writes PNG previews to output/png_debug/<stem> and prints whitespace metrics via src/renderer.analyze_pdf_whitespace().
  - When changing pagination/flow, prefer KeepTogether and keepWithNext tweaks around headers + first content blocks.
- Add a new section:
  1) Extend parser: add data shape to self.data and a _parse_* method, wire into parse().
  2) Extend pdf_generator: add _add_* method that appends Flowables to self.story; call it from generate() in the correct column/page location.
  3) Keep header with first block (KeepTogether) to avoid stranded headers.

## Patterns to follow
- Keep text parsing resilient to minor whitespace and punctuation variations; prefer named groups in regex and small helpers for heuristics.
- In ReportLab, group minimal logical units with KeepTogether (e.g., header + first paragraph). Avoid huge KeepTogether blocks that might not fit a column.
- After editing pagination/styling, run main.py to validate no exceptions and skim whitespace metrics for regressions.

## External deps
- reportlab (PDF), pypdfium2 (PNG rendering for debug), pillow (image IO). See requirements.txt.

## Examples
- Attack header parsing accepts punctuation: "Bow & Arrow" becomes a SubsectionHeader with its description.
- Cypher header parsing accepts tagged names: "Effort Enhancer (Combat) (Level 4, Subtle)" parses as its own cypher.
- Background/Notes: headers kept with first paragraph; remaining paragraphs flow across columns/pages.

## Gotchas
- Section headers can strand at column bottoms if not grouped; ensure header + first block are KeepTogether for long sections.
- Updating data schema without updating pdf_generator will raise KeyError or render empty sections.
- Make changes in small increments; use debug PNGs and console whitespace output to spot layout regressions early.
