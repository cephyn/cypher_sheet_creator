# Development Guide

## Getting Started with Development

### Prerequisites
- Python 3.10+ (project uses 3.13.2)
- Text editor or IDE (VS Code recommended)
- Git for version control

### Initial Setup

1. **Clone/Navigate to the project**
   ```powershell
   cd f:\AppDevTwo\cypher_sheet_creator
   ```

2. **Create virtual environment**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```powershell
   python main.py
   ```

## Project Workflow

### Understanding the Code Flow

```
1. main.py
   ├─ Scan examples/ directory
   ├─ For each .txt file:
   │  ├─ Read file content
   │  ├─ Pass to CharacterSheetParser
   │  ├─ Parse text → structured dict
   │  ├─ Pass to CypherCharacterSheetPDF
   │  ├─ Generate PDF
   │  └─ Save to output/
   └─ Report results

2. parser.py
   ├─ CharacterSheetParser.__init__(text)
   ├─ parse() → calls all parse_* methods
   ├─ _parse_header()
   ├─ _parse_attributes()
   ├─ _parse_special_abilities()
   ├─ _parse_skills()
   ├─ _parse_attacks()
   ├─ _parse_cyphers()
   ├─ _parse_equipment()
   ├─ _parse_advancements()
   ├─ _parse_background()
   ├─ _parse_notes()
   └─ Returns: structured dict

3. pdf_generator.py
   ├─ CypherCharacterSheetPDF.__init__(data, path)
   ├─ generate() → calls all add_* methods
   ├─ _create_custom_styles()
   ├─ _add_header()
   ├─ _add_attributes_section()
   ├─ _add_special_abilities()
   ├─ _add_skills()
   ├─ _add_attacks()
   ├─ _add_cyphers()
   ├─ _add_equipment()
   ├─ _add_background()
   ├─ _add_notes()
   └─ Builds PDF in output/
```

## Making Changes

### Adding a New Section (Example: Inventory)

**Step 1: Update parser.py**
```python
# In __init__ method, add to self.data:
'inventory': []

# Add parsing method:
def _parse_inventory(self):
    """Parse the Inventory section."""
    content = self._get_section_content('Inventory')
    for line in content:
        if line.strip().startswith('-'):
            self.data['inventory'].append(line.strip()[1:].strip())
        elif line.strip():
            self.data['inventory'].append(line.strip())

# In parse() method, call:
self._parse_inventory()
```

**Step 2: Update pdf_generator.py**
```python
# Add rendering method:
def _add_inventory(self):
    """Add inventory section."""
    if not self.data['inventory']:
        return
    
    self.story.append(Paragraph("INVENTORY", self.styles['SectionHeader']))
    for item in self.data['inventory']:
        item_text = f"• {item}"
        self.story.append(Paragraph(item_text, self.styles['Normal2']))
    self.story.append(Spacer(1, 0.15 * inch))

# In generate() method, call:
self._add_inventory()
```

### Modifying Styling

**Edit colors:**
```python
# In pdf_generator.py __init__:
self.colors = {
    'primary': HexColor('#YOUR_HEX'),  # Changed
    'secondary': HexColor('#3498DB'),
    'accent': HexColor('#E74C3C'),
    'light_bg': HexColor('#ECF0F1'),
    'text': HexColor('#2C3E50'),
}
```

**Edit fonts and sizes:**
```python
# In _create_custom_styles():
self.styles.add(ParagraphStyle(
    name='CustomTitle',
    fontSize=20,  # Changed from 18
    fontName='Helvetica-Bold',
))
```

**Adjust page layout:**
```python
# In __init__:
self.doc = SimpleDocTemplate(
    output_path,
    pagesize=A4,  # Changed from letter
    rightMargin=1 * inch,  # Changed from 0.5
    # ... etc
)
```

### Improving the Parser

**Handling edge cases:**
```python
def _parse_section(self, section_name: str):
    """More robust section finding."""
    for i, line in enumerate(self.lines):
        # Case-insensitive matching
        if line.strip().upper() == section_name.upper():
            return i
        # Support with/without separators
        if section_name in line and (i + 1 < len(self.lines) 
                                      and '---' in self.lines[i + 1]):
            return i
    return None
```

**Better regex patterns:**
```python
# Use raw strings for clarity
pattern = r'^(\w+)\s+is\s+a\s+(.+?)(?:\s+in\s+a\s+(.+?))?$'

# Use named groups for readability
match = re.match(
    r'(?P<name>\w+)\s+is\s+a\s+(?P<type>.+)',
    first_line
)
if match:
    name = match.group('name')
    char_type = match.group('type')
```

## Testing & Debugging

### Manual Testing

1. **Create test file** in `examples/test_character.txt`
2. **Run the application**
   ```powershell
   python main.py
   ```
3. **Check output** in `output/test_character.pdf`

### Debugging Parsing

```python
# In main.py or directly in parser.py:
parser = CharacterSheetParser(content)
data = parser.parse()

# Print parsed data to inspect:
import json
print(json.dumps(data, indent=2))
```

### Debugging PDF Generation

```python
# Check what's being added:
print(f"Adding header: {self.data['header']}")
print(f"Number of skills: {len(self.data['skills'])}")

# Inspect generated story elements:
for i, element in enumerate(self.story):
    print(f"{i}: {type(element).__name__}")
```

## Common Tasks

### Add Support for a New Game System

1. Create `src/parsers/cypher_parser.py` and `src/parsers/dnd_parser.py`
2. Create abstract base class in `src/parser_base.py`
3. Update `main.py` to detect system and use appropriate parser
4. Create system-specific PDF generator in `src/pdf_generators/`

### Add Configuration File Support

```python
# Create config.py
import json

class Config:
    def __init__(self, config_file='config.json'):
        with open(config_file) as f:
            self.data = json.load(f)
    
    def get_color(self, key):
        return self.data['colors'][key]
    
    def get_font_size(self, key):
        return self.data['fonts'][key]

# Use in pdf_generator.py:
config = Config()
self.colors['primary'] = HexColor(config.get_color('primary'))
```

### Set Up Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# In main.py:
logger.info(f"Processing: {text_file.name}")
logger.error(f"Error: {str(e)}")
```

### Add Unit Tests

```python
# tests/test_parser.py
import unittest
from src.parser import CharacterSheetParser

class TestParser(unittest.TestCase):
    def test_parse_header(self):
        text = "Warrior is a Vicious Warrior who Never Says Die"
        parser = CharacterSheetParser(text)
        data = parser.parse()
        self.assertEqual(data['header']['name'], 'Warrior')
    
    def test_parse_attributes(self):
        text = "Might:     ______ Pool: 16 Edge: 1 Defense: Practiced"
        # ... test logic

if __name__ == '__main__':
    unittest.main()
```

## Performance Optimization

### Batch Processing
- Current: Sequential processing
- Future: Use multiprocessing for parallel PDF generation

```python
from multiprocessing import Pool

def process_file(file_path):
    # Parse and generate PDF
    pass

with Pool() as p:
    p.map(process_file, text_files)
```

### Caching
- Cache parsed data for unchanged files
- Use file hashing to detect changes

### Memory Optimization
- Process large files in chunks
- Clean up temporary objects

## Code Standards

### Style Guide
- Follow PEP 8
- Use type hints for functions
- Write docstrings for all modules/classes/functions
- Keep functions under 50 lines when possible
- Use meaningful variable names

### Example:
```python
def extract_pool_value(line: str) -> Optional[int]:
    """
    Extract pool value from attribute line.
    
    Args:
        line: A string containing pool information
        
    Returns:
        The pool value as an integer, or None if not found
        
    Example:
        >>> extract_pool_value("Might:     ______ Pool: 13 Edge: 1")
        13
    """
    match = re.search(r'Pool:\s+(\d+)', line)
    return int(match.group(1)) if match else None
```

## Deploying/Distributing

### Create Executable (PyInstaller)
```powershell
pip install pyinstaller
pyinstaller --onefile main.py
```

### Create Installer (NSIS or MSI)
- Package the executable and documentation
- Create installer wizard
- Handle registry entries if needed

### Publish to PyPI
```powershell
pip install setuptools wheel twine
python setup.py sdist bdist_wheel
twine upload dist/*
```

## Troubleshooting Development

| Issue | Solution |
|-------|----------|
| Import errors | Ensure virtual env is activated |
| Module not found | Run `pip install -r requirements.txt` |
| Changes not reflecting | Restart Python interpreter |
| PDF not generating | Check file permissions in output/ |
| Memory issues | Close unnecessary applications |
| Slow performance | Check for large files in examples/ |

## Resources

- **ReportLab**: https://www.reportlab.com/docs/reportlab-userguide.pdf
- **Python Regex**: https://docs.python.org/3/library/re.html
- **Type Hints**: https://docs.python.org/3/library/typing.html
- **PEP 8**: https://www.python.org/dev/peps/pep-0008/

## Getting Help

1. Check documentation (README.md, ARCHITECTURE.md)
2. Review code comments and docstrings
3. Test with debug prints and logging
4. Consult Python official documentation
5. Search Stack Overflow for similar issues
