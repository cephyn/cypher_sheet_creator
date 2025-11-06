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
import argparse


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Cypher System character sheet text files into PDFs.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default="examples",
        help="Input directory containing .txt files, or a single .txt file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="output",
        help="Output directory for generated PDFs and debug assets",
    )
    parser.add_argument(
        "-p",
        "--pattern",
        type=str,
        default="*.txt",
        help="Glob pattern to match input files when --input is a directory",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Generate debug PNG previews and whitespace metrics (slower)",
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = _parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)
    png_debug_root = output_dir / "png_debug"
    tmp_pdf_root = output_dir / "_debug_pdf"

    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    # Only create debug dirs when requested
    if args.debug:
        png_debug_root.mkdir(parents=True, exist_ok=True)
        tmp_pdf_root.mkdir(parents=True, exist_ok=True)

    # Resolve input files (directory glob or single file)
    if input_path.is_dir():
        text_files = list(input_path.glob(args.pattern))
    elif input_path.is_file() and input_path.suffix.lower() == ".txt":
        text_files = [input_path]
    else:
        print(f"Input not found or unsupported: {input_path}")
        print("Provide a directory of .txt files or a single .txt file path.")
        sys.exit(1)

    if not text_files:
        print(f"No files matched in {input_path} with pattern '{args.pattern}'.")
        return

    print(
        f"Found {len(text_files)} character sheet(s) to convert from '{input_path}'.\n"
    )

    for text_file in text_files:
        print(f"Processing: {text_file.name}")

        try:
            # Read the file
            with open(text_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse the character sheet
            parser = CharacterSheetParser(content)
            data = parser.parse()

            # Paths and generation
            final_pdf_name = text_file.stem + ".pdf"
            final_pdf_path = output_dir / final_pdf_name

            if args.debug:
                tmp_pdf_path = tmp_pdf_root / final_pdf_name
                # Keep PNG previews organized mirroring the input directory structure when possible
                try:
                    rel = text_file.relative_to(
                        input_path if input_path.is_dir() else text_file.parent
                    )
                    png_out_dir = png_debug_root / rel.parent / text_file.stem
                except Exception:
                    png_out_dir = png_debug_root / text_file.stem

                # Generate to a temporary PDF first (so we can preview to PNG)
                pdf_generator = CypherCharacterSheetPDF(data, str(tmp_pdf_path))
                pdf_generator.generate()

                # Create PNG previews and whitespace metrics
                pngs = pdf_to_pngs(tmp_pdf_path, png_out_dir, scale=2.0)
                print(f"  PNG previews: {len(pngs)} page(s) -> {png_out_dir}")
                analyze_pdf_whitespace(tmp_pdf_path, scale=1.5)

                # Move/copy the temporary PDF to the final output location
                try:
                    tmp_pdf_path.replace(final_pdf_path)
                except Exception:
                    with open(tmp_pdf_path, "rb") as src, open(
                        final_pdf_path, "wb"
                    ) as dst:
                        dst.write(src.read())

            else:
                # Generate directly to final output (no debug assets)
                pdf_generator = CypherCharacterSheetPDF(data, str(final_pdf_path))
                pdf_generator.generate()

            print(f"  Generated: {final_pdf_path}")

        except Exception as e:
            print(f"  Error processing {text_file.name}: {str(e)}")
            import traceback

            traceback.print_exc()

    print("\nConversion complete!")


if __name__ == "__main__":
    main()
