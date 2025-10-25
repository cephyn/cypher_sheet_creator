#!/usr/bin/env python3
"""
Cypher Sheet Creator - Convert character sheet text files to professional PDFs.
"""

import sys
import os
from pathlib import Path
from src.parser import CharacterSheetParser
from src.pdf_generator import CypherCharacterSheetPDF


def main():
    """Main entry point."""
    examples_dir = Path("examples")
    output_dir = Path("output")

    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)

    # Process all text files in examples directory
    text_files = list(examples_dir.glob("*.txt"))

    if not text_files:
        print("No text files found in examples directory.")
        return

    print(f"Found {len(text_files)} character sheet(s) to convert.\n")

    for text_file in text_files:
        print(f"Processing: {text_file.name}")

        try:
            # Read the file
            with open(text_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse the character sheet
            parser = CharacterSheetParser(content)
            data = parser.parse()

            # Generate PDF
            output_filename = text_file.stem + ".pdf"
            output_path = output_dir / output_filename

            pdf_generator = CypherCharacterSheetPDF(data, str(output_path))
            pdf_generator.generate()

            print(f"  ✓ Generated: {output_path}")

        except Exception as e:
            print(f"  ✗ Error processing {text_file.name}: {str(e)}")
            import traceback

            traceback.print_exc()

    print("\nConversion complete!")


if __name__ == "__main__":
    main()
