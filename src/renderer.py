"""
Renderer utilities for generating PNG previews from PDFs and analyzing whitespace.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from pypdfium2 import PdfDocument
from PIL import Image


def pdf_to_pngs(
    pdf_path: Path | str, out_dir: Path | str, scale: float = 2.0
) -> List[Path]:
    """Render each page of a PDF to a PNG file.

    Args:
        pdf_path: Path to the input PDF file.
        out_dir: Directory to write PNG files into (created if needed).
        scale: Render scale factor. 2.0 ~ 144 DPI on typical PDF units; increase for sharper images.

    Returns:
        List of written PNG file paths in page order.
    """
    pdf_path = Path(pdf_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = PdfDocument(str(pdf_path))
    outputs: List[Path] = []

    stem = pdf_path.stem
    for index, page in enumerate(doc):
        # Render page
        bitmap = page.render(scale=scale)
        pil_image: Image.Image = bitmap.to_pil()

        out_file = out_dir / f"{stem}_page{index + 1}.png"
        pil_image.save(out_file, format="PNG")
        outputs.append(out_file)

    return outputs


def analyze_whitespace(
    img: Image.Image, threshold: int = 245
) -> Tuple[float, Tuple[int, int, int, int]]:
    """Estimate whitespace ratio and content bounding box for a page PNG.

    Args:
        img: PIL Image of the page.
        threshold: Grayscale threshold (0-255): pixels >= threshold considered whitespace.

    Returns:
        (whitespace_ratio, bbox) where bbox = (left, top, right, bottom) of non-white content.
    """
    gray = img.convert("L")
    w, h = gray.size
    pixels = gray.load()

    # Find content bounds by scanning for any pixel below threshold
    top = None
    bottom = None
    left = None
    right = None

    # Compute whitespace ratio
    total = w * h
    white_count = 0

    for y in range(h):
        row_has_content = False
        for x in range(w):
            val = pixels[x, y]
            if val >= threshold:
                white_count += 1
            else:
                row_has_content = True
                if left is None or x < left:
                    left = x
                if right is None or x > right:
                    right = x
        if row_has_content:
            if top is None:
                top = y
            bottom = y

    whitespace_ratio = white_count / float(total) if total else 0.0

    # Normalize bbox
    if top is None or left is None or right is None or bottom is None:
        bbox = (0, 0, w, h)  # fallback: treat as full-page whitespace
    else:
        bbox = (left, top, right, bottom)

    return whitespace_ratio, bbox


def analyze_pdf_whitespace(pdf_path: Path | str, scale: float = 2.0) -> None:
    """Render pages to memory and print whitespace metrics for debugging."""
    doc = PdfDocument(str(pdf_path))
    for idx, page in enumerate(doc):
        bitmap = page.render(scale=scale)
        img = bitmap.to_pil()
        ratio, bbox = analyze_whitespace(img)
        print(f"  Page {idx+1}: whitespace ~ {ratio:.2%}, content bbox={bbox}")
