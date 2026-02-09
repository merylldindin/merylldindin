"""PDF assembly utilities for LinkedIn carousel."""

import shutil
import subprocess
from pathlib import Path

from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from models.carousel import SLIDE_HEIGHT, SLIDE_WIDTH

# PDF page size matching LinkedIn slide dimensions
# Using points (1 inch = 72 points)
PAGE_WIDTH = SLIDE_WIDTH * 72 / 96  # Convert pixels to points (assuming 96 DPI)
PAGE_HEIGHT = SLIDE_HEIGHT * 72 / 96


def assemble_carousel_pdf(
    slide_paths: list[Path],
    output_path: Path,
    title: str = "LinkedIn Carousel",
) -> Path:
    """Assemble slide images into a PDF carousel.

    Args:
        slide_paths: Ordered list of slide image paths
        output_path: Path for output PDF file
        title: PDF document title

    Returns:
        Path to created PDF
    """
    # Create PDF with custom page size matching slide dimensions
    c = canvas.Canvas(
        str(output_path),
        pagesize=(PAGE_WIDTH, PAGE_HEIGHT),
    )
    c.setTitle(title)
    c.setAuthor("Meryll Dindin")

    for i, slide_path in enumerate(slide_paths):
        if not slide_path.exists():
            print(f"  Warning: Slide not found: {slide_path}")
            continue

        # Draw image to fill the entire page
        c.drawImage(
            str(slide_path),
            0,
            0,
            width=PAGE_WIDTH,
            height=PAGE_HEIGHT,
            preserveAspectRatio=True,
            anchor="c",
        )

        # Add page break if not the last slide
        if i < len(slide_paths) - 1:
            c.showPage()

    c.save()

    compress_pdf(output_path)

    print(f"  PDF saved: {output_path.name}")
    return output_path


def compress_pdf(pdf_path: Path) -> None:
    """Compress PDF using Ghostscript if available.

    Uses the /ebook preset (150dpi) which is sufficient for LinkedIn uploads.

    Args:
        pdf_path: Path to PDF file to compress in-place
    """
    gs_path = shutil.which("gs")
    if not gs_path:
        print("  Ghostscript not found, skipping PDF compression")
        return

    compressed_path = pdf_path.with_suffix(".compressed.pdf")

    result = subprocess.run(
        [
            gs_path,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/ebook",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={compressed_path}",
            str(pdf_path),
        ],
        capture_output=True,
    )

    if result.returncode == 0 and compressed_path.exists():
        original_size = pdf_path.stat().st_size
        compressed_size = compressed_path.stat().st_size
        compressed_path.replace(pdf_path)
        reduction = (1 - compressed_size / original_size) * 100
        print(f"  PDF compressed: {original_size // 1024}KB → {compressed_size // 1024}KB ({reduction:.0f}% reduction)")
    else:
        compressed_path.unlink(missing_ok=True)
        print("  PDF compression failed, keeping original")
