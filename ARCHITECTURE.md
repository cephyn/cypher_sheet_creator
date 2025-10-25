# Project Documentation

## Overview

**Cypher Sheet Creator** is a Python application that converts formatted character sheet text files into professional, stylish PDFs. It's designed for the Cypher System (a tabletop RPG system), but can be adapted for other systems.

The application automatically processes multiple character sheets in batch mode, parsing structured text and generating beautiful, easy-to-read PDF documents.

## System Architecture

```
Input (Text Files)
        ↓
   Parser Module
        ↓
Structured Data (Dict)
        ↓
  PDF Generator
        ↓
Output (PDF Files)
```

### Module Breakdown

#### `parser.py` - CharacterSheetParser
Responsible for parsing formatted text files and extracting structured data.

**Key Methods:**
- `parse()`: Main parsing orchestrator
- `_parse_header()`: Extracts character name and descriptors
- `_parse_attributes()`: Extracts pools, edges, defenses
- `_parse_special_abilities()`: Extracts special abilities and descriptions
- `_parse_skills()`: Extracts skills with levels and descriptions
- `_parse_attacks()`: Extracts attack details
- `_parse_cyphers()`: Extracts cypher information
- `_parse_equipment()`: Extracts equipment list
- `_parse_advancements()`: Extracts advancement tier and choices
- `_parse_background()`: Extracts background information
- `_parse_notes()`: Extracts miscellaneous notes

**Output Format:**
```python
{
    'header': {'name', 'type', 'focus', 'flavor', 'world'},
    'attributes': {'might', 'speed', 'intellect', 'effort', 'armor', 'initiative'},
    'special_abilities': [{'name', 'description'}, ...],
    'skills': [{'name', 'level', 'description'}, ...],
    'attacks': [{'name', 'description'}, ...],
    'cyphers': [{'name', 'level', 'type', 'description'}, ...],
    'equipment': ['item1', 'item2', ...],
    'advancements': {'tier', 'choices'},
    'background': {'section': ['content']},
    'notes': {'section': ['content']}
}
```

#### `pdf_generator.py` - CypherCharacterSheetPDF
Responsible for generating professional PDFs with styling and layout.

**Key Methods:**
- `generate()`: Main PDF generation orchestrator
- `_create_custom_styles()`: Sets up reportlab styles
- `_add_header()`: Renders character header
- `_add_attributes_section()`: Renders attribute table
- `_add_special_abilities()`: Renders special abilities section
- `_add_skills()`: Renders skills section
- `_add_attacks()`: Renders attacks section
- `_add_cyphers()`: Renders cyphers section
- `_add_equipment()`: Renders equipment section
- `_add_background()`: Renders background section (page 2)
- `_add_notes()`: Renders notes section (page 2)

**Design Features:**
- Modern color palette with professional styling
- Two-page layout (character stats → background/notes)
- Responsive tables with alternating row colors
- Hierarchical text sizing and weights
- Clean spacing and visual hierarchy

#### `main.py` - Application Entry Point
Orchestrates the batch processing of character sheets.

**Process:**
1. Scans `examples/` directory for `.txt` files
2. For each file:
   - Reads the file content
   - Parses using `CharacterSheetParser`
   - Generates PDF using `CypherCharacterSheetPDF`
   - Outputs to `output/` directory
3. Reports success/failure for each file

## Data Flow Example

**Input Text:**
```
Herbalist is a Perceptive Explorer who Lives In The Wilderness with a Skills And
Knowledge Flavor in a Historical world

Might:     ______ Pool: 13 Edge: 1 Defense: Practiced
...
```

**Parsed Data:**
```python
{
    'header': {
        'name': 'Herbalist',
        'type': 'Perceptive Explorer',
        'focus': 'Lives In The Wilderness',
        'flavor': 'Skills And Knowledge',
        'world': 'Historical'
    },
    'attributes': {
        'might': {'pool': 13, 'edge': 1, 'defense': 'Practiced'},
        ...
    }
}
```

**PDF Output:**
- Page 1: Header, attributes table, special abilities, skills, attacks, cyphers, equipment
- Page 2: Background sections, notes and intrusions

## File Structure

```
cypher_sheet_creator/
├── main.py                           # Entry point
├── requirements.txt                  # Dependencies
├── README.md                         # Main documentation
├── QUICK_START.md                    # Getting started guide
├── ARCHITECTURE.md                   # This file
├── .gitignore                        # Git ignore rules
│
├── src/
│   ├── __init__.py                   # Package marker
│   ├── parser.py                     # Text parsing module
│   └── pdf_generator.py              # PDF generation module
│
├── examples/                         # Input character sheets (text files)
│   ├── herbalist_*.txt
│   ├── warrior_*.txt
│   ├── shaman_*.txt
│   ├── tracker_*.txt
│   ├── lore_keeper_*.txt
│   └── scavenger_*.txt
│
├── output/                           # Generated PDFs (created on first run)
│   ├── herbalist_*.pdf
│   ├── warrior_*.pdf
│   ├── shaman_*.pdf
│   ├── tracker_*.pdf
│   ├── lore_keeper_*.pdf
│   └── scavenger_*.pdf
│
└── .venv/                            # Virtual environment (created on setup)
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| reportlab | 4.4.4 | PDF generation and styling |
| pillow | 12.0.0 | Image handling (optional for future features) |

## Text File Format Specification

Character sheets must follow this format:

### Header Line
```
[Name] is a [Type] who/with [Focus] with a [Flavor] Flavor in a [World] world
```

### Sections
Each section must have a clear header followed by content:

```
Might:     ______ Pool: [N] Edge: [N] Defense: [Level]
Speed:     ______ Pool: [N] Edge: [N] Defense: [Level]
Intellect: ______ Pool: [N] Edge: [N] Defense: [Level]
Effort: [N]
Armor: [N]

Special Abilities
-----------------
[Ability Name]
    [Description text...]

Skills
------
[Skill Name] ([Level])
    [Optional description...]

Attacks
-------
[Attack Name]
    [Description...]

Cyphers
-------
[Cypher Name] (Level [N], [Type])
    [Description...]

Equipment
---------
- [Item]

Advancements
------------
Tier: [N]
[ ] [Choice]

Background
----------
[Section Name]
    [Content...]

Notes
-----
[Section Name]
    [Content...]
```

## Color Scheme

```
Primary:   #2C3E50  - Dark blue-gray (headings, text)
Secondary: #3498DB  - Bright blue (section headers)
Accent:    #E74C3C  - Red (highlights, important)
Light BG:  #ECF0F1  - Light gray (table backgrounds)
Text:      #2C3E50  - Dark (body text)
```

## Development Guidelines

### Adding New Sections
1. Create parsing method in `CharacterSheetParser`:
   ```python
   def _parse_section(self):
       # Extract data and update self.data['section_key']
   ```

2. Create rendering method in `CypherCharacterSheetPDF`:
   ```python
   def _add_section(self):
       # Use self.story.append() to add elements
   ```

3. Call in `generate()` method

### Improving Parsing
- Use regex for pattern matching
- Handle variable whitespace
- Support multiple content formats
- Validate extracted data

### Enhancing Styling
- Adjust colors through self.colors dict
- Modify font sizes in _create_custom_styles()
- Change margins in __init__()
- Add new TableStyle rules for tables

## Performance Considerations

- **Parsing**: O(n) where n = number of lines in input file
- **PDF Generation**: ~1-2 seconds per character sheet
- **Memory**: Minimal - processes one file at a time
- **Scalability**: Can process 100+ character sheets in reasonable time

## Known Limitations & Future Work

### Current Limitations
- No support for special characters in filenames
- Limited to English text
- Fixed page size (letter)
- No image/portrait support
- No hyperlinks or bookmarks

### Future Enhancements
- [ ] CLI arguments for custom I/O paths
- [ ] Configuration file for styling
- [ ] Multiple template options
- [ ] Support for multiple game systems
- [ ] Image handling and portraits
- [ ] HTML/JSON export options
- [ ] GUI application
- [ ] Watch mode for auto-regeneration

## Testing Considerations

To test modifications:
1. Create test files in `examples/`
2. Run `python main.py`
3. Check generated PDFs in `output/`
4. Verify parsing accuracy and PDF appearance

## Troubleshooting Guide

| Issue | Cause | Solution |
|-------|-------|----------|
| No PDFs generated | No .txt files in examples/ | Add character sheet files |
| Parse errors | Wrong file format | Check against specification |
| Malformed PDF | Missing sections | Ensure all headers present |
| Styling issues | Color/font not applied | Check custom styles setup |
| Import errors | Missing dependencies | Run `pip install -r requirements.txt` |

## Contact & Support

For issues, enhancements, or questions about the architecture, refer to the README.md and QUICK_START.md files.
