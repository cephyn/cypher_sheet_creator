#!/usr/bin/env python3
"""
Cypher Sheet Creator - Convert character sheet text files to professional PDFs.
"""

import sys
import os
from pathlib import Path
from src.parser import CharacterSheetParser
from src.pdf_generator import CypherCharacterSheetPDF
from src.renderer import pdf_to_pngs, analyze_pdf_whitespace


def main():
    """Main entry point."""
    examples_dir = Path("examples")
    output_dir = Path("output")
    png_debug_root = output_dir / "png_debug"
    tmp_pdf_root = output_dir / "_debug_pdf"

    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    png_debug_root.mkdir(exist_ok=True)
    tmp_pdf_root.mkdir(exist_ok=True)

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

            # Paths for debug-first generation
            final_pdf_name = text_file.stem + ".pdf"
            final_pdf_path = output_dir / final_pdf_name
            tmp_pdf_path = tmp_pdf_root / final_pdf_name
            png_out_dir = png_debug_root / text_file.stem

            # Generate to a temporary PDF first (so we can preview to PNG)
            pdf_generator = CypherCharacterSheetPDF(data, str(tmp_pdf_path))
            pdf_generator.generate()

            # Create PNG previews
            pngs = pdf_to_pngs(tmp_pdf_path, png_out_dir, scale=2.0)
            # Print whitespace metrics for quick debugging
            print(f"  PNG previews: {len(pngs)} page(s) -> {png_out_dir}")
            analyze_pdf_whitespace(tmp_pdf_path, scale=1.5)

            # Move/copy the temporary PDF to the final output location
            # Use replace to overwrite if exists
            try:
                # Python 3.8+: Path.replace is available
                tmp_pdf_path.replace(final_pdf_path)
            except Exception:
                # Fallback to write bytes copy
                with open(tmp_pdf_path, "rb") as src, open(final_pdf_path, "wb") as dst:
                    dst.write(src.read())

            print(f"  Generated: {final_pdf_path}")

        except Exception as e:
            print(f"  Error processing {text_file.name}: {str(e)}")
            import traceback

            traceback.print_exc()

    print("\nConversion complete!")


if __name__ == "__main__":
    main()
