# Quick Start Guide

## Setup (First Time Only)

1. Open PowerShell in the project directory
2. Create and activate the virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Running the Application

```powershell
.\.venv\Scripts\python.exe main.py
```

Or simply:
```powershell
python main.py
```

All character sheets in the `examples/` directory will be processed and PDFs will be generated in the `output/` directory.

### Process a different folder or a single file

You can point the tool at any folder of `.txt` files (or a single `.txt` file):

```powershell
# Folder of .txt files
python main.py --input "C:\path\to\my_sheets"

# Single file
python main.py --input "C:\path\to\my_sheets\my_character.txt"

# Custom output directory
python main.py --input "C:\path\to\my_sheets" --output "C:\path\to\exports"

# Use a custom file pattern (when input is a directory)
python main.py --input "C:\path\to\my_sheets" --pattern "*_final.txt"

# Enable debug previews (PNG) and whitespace metrics
python main.py --input "C:\path\to\my_sheets" --debug
```

Notes:
- Defaults remain `--input examples` and `--output output`.
- Debug is OFF by default. Use `--debug` to generate PNG previews and whitespace metrics.
- With `--debug`, PNGs go to `<output>/png_debug/` and intermediate PDFs to `<output>/_debug_pdf/`.

## Adding New Character Sheets

1. Place your formatted text file in the `examples/` directory
2. Run `python main.py`
3. Your PDF will be generated in the `output/` directory

## Project Features

### Architecture
- **`parser.py`**: Intelligent text file parsing that extracts structured data from formatted character sheets
- **`pdf_generator.py`**: Professional PDF generation with modern styling and layout
- **`main.py`**: Command-line entry point for batch processing

### Styling
- **Modern Color Palette**: Professional blues and grays with accent colors
- **Clean Typography**: Hierarchical headings and readable body text
- **Efficient Layout**: Two-page format with attributes on page 1, background/notes on page 2
- **Professional Tables**: Attribute tables with alternating row colors
- **Organized Sections**: Clear visual separation of character information

### Supported Sections
✓ Character Header (Name, Type, Focus, Flavor, World)
✓ Attributes (Pools, Edges, Defenses, Initiative)
✓ Special Abilities
✓ Skills
✓ Attacks
✓ Cyphers
✓ Equipment
✓ Background
✓ Notes

## Extending the Application

### Adding Custom Styling
Edit the color palette in `pdf_generator.py`:
```python
self.colors = {
    'primary': HexColor('#2C3E50'),
    'secondary': HexColor('#3498DB'),
    # ... add more colors
}
```

### Adding New Sections
1. Add parsing logic in `parser.py` (e.g., `_parse_new_section()`)
2. Add PDF generation in `pdf_generator.py` (e.g., `_add_new_section()`)
3. Call the new method in the `generate()` function

### Customizing PDF Layout
Modify page margins and styling in `CypherCharacterSheetPDF.__init__()`:
```python
self.doc = SimpleDocTemplate(
    output_path,
    pagesize=letter,  # or A4
    rightMargin=0.5 * inch,
    # ... adjust margins as needed
)
```

## Troubleshooting

### Command not found: python
- Make sure Python is in your PATH
- Or use the full path: `.\.venv\Scripts\python.exe main.py`

### No PDFs generated
- Check that text files exist in the `examples/` directory
- Check console output for parsing errors
- Ensure file format matches the expected structure

### Incorrect PDF formatting
- Review the input text file format
- Check parser output for parsing issues
- Verify section headers match expected names (e.g., "Special Abilities", "Skills")

## Future Enhancements

- [ ] Command-line arguments for custom input/output directories
- [ ] Interactive GUI for character creation
- [ ] Template selection for different game systems
- [ ] Custom color scheme configuration
- [ ] Image/portrait support
- [ ] Multi-language support
- [ ] Export to other formats (HTML, JSON, XML)
