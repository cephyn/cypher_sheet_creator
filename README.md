# Cypher Sheet Creator

A Python application that converts formatted character sheet text files into stylish, clean, and professional PDFs with an efficient modern layout.

## Features

- **Smart Parsing**: Extracts all character information from structured text files
- **Professional Layout**: Creates beautiful, multi-section character sheets
- **Modern Design**: Clean typography, thoughtful color scheme, and efficient space usage
- **Batch Processing**: Convert multiple character sheets at once
- **Customizable**: Easy to extend with additional styling or sections

## Project Structure

```
cypher_sheet_creator/
├── main.py              # Main entry point
├── requirements.txt     # Python dependencies
├── examples/            # Sample character sheet files
└── src/
    ├── __init__.py
    ├── parser.py        # Text file parsing logic
    └── pdf_generator.py # PDF generation and styling
```

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

This will process all `.txt` files in the `examples/` directory and generate corresponding PDFs in the `output/` directory.

## Character Sheet Format

The application expects text files with the following structure:

```
[Name] is a [Descriptor] [Type] who/with [Focus] with a [Flavor] Flavor in a [World] world

[Attributes Section]
Might:     ______ Pool: 13 Edge: 1 Defense: Practiced
...

[Special Abilities]
[Name]
    [Description]

[Skills]
[Name] ([Level])
    [Description]

[Attacks]
[Name]
    [Description]

[Cyphers]
[Name] (Level [X], [Type])
    [Description]

[Equipment]
- [Item]

[Background]
[Section]
    [Content]

[Notes]
[Section]
    [Content]
```

## Dependencies

- **reportlab**: PDF generation
- **pillow**: Image handling

## License

MIT
