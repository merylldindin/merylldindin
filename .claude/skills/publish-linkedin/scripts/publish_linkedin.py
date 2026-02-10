"""LinkedIn carousel generator.

Generate professional LinkedIn carousels with AI-powered slide creation.

Usage:
    uv run python scripts/publish_linkedin.py --topic "How to build a product roadmap"
    uv run python scripts/publish_linkedin.py --topic "MTSS Framework Guide" --slides 8
    uv run python scripts/publish_linkedin.py --outline "Topic"
    uv run python scripts/publish_linkedin.py --review "draft text here"
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(Path(__file__).parent.parent / ".env")

from generators.content import generate_outline, review_draft
from generators.illustrations import generate_slide_background
from models.carousel import Carousel, CarouselMetadata, CarouselSlide
from renderers import render_slide
from utils.pdf import assemble_carousel_pdf

SCRIPTS_DIR: Path = Path(__file__).parent
OUTPUT_DIR: Path = SCRIPTS_DIR / "output"


def create_output_directory() -> tuple[Path, str]:
    """Create timestamped output directory with slides subfolder.

    Returns:
        Tuple of (output_path, timestamp)
    """
    timestamp: str = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path: Path = OUTPUT_DIR / timestamp
    slides_path: Path = output_path / "slides"
    output_path.mkdir(parents=True, exist_ok=True)
    slides_path.mkdir(parents=True, exist_ok=True)
    return output_path, timestamp


def save_caption(caption_text: str, output_dir: Path) -> Path:
    """Save caption to markdown file.

    Args:
        caption_text: Formatted caption text
        output_dir: Output directory

    Returns:
        Path to caption file
    """
    caption_path: Path = output_dir / "caption.md"
    caption_path.write_text(caption_text, encoding="utf-8")
    print(f"  Caption saved: {caption_path.name}")
    return caption_path


def save_metadata(
    carousel: Carousel,
    slide_paths: list[Path],
    pdf_path: Path | None,
    caption_path: Path | None,
    output_dir: Path,
    timestamp: str,
) -> Path:
    """Save generation metadata to JSON file.

    Args:
        carousel: Carousel object with content
        slide_paths: Paths to generated slide images
        pdf_path: Path to assembled PDF
        caption_path: Path to caption file
        output_dir: Output directory
        timestamp: Generation timestamp

    Returns:
        Path to metadata file
    """
    metadata = CarouselMetadata(
        topic=carousel.topic,
        title=carousel.title,
        slide_count=carousel.get_slide_count(),
        slide_paths=[str(p) for p in slide_paths],
        pdf_path=str(pdf_path) if pdf_path else None,
        caption_path=str(caption_path) if caption_path else None,
        output_dir=str(output_dir),
        timestamp=timestamp,
    )

    metadata_path: Path = output_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata.model_dump(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"  Metadata saved: {metadata_path.name}")
    return metadata_path


def run_outline(topic: str, slide_count: int = 6) -> None:
    """Preview carousel outline without generating images.

    Args:
        topic: Topic for the carousel
        slide_count: Target number of slides
    """
    print("\n" + "=" * 60)
    print("CAROUSEL OUTLINE PREVIEW")
    print("=" * 60 + "\n")

    print(f"Topic: {topic}")
    print(f"Target slides: {slide_count}\n")

    print("Generating outline...")
    carousel = generate_outline(topic, slide_count)

    print(f"\nTitle: {carousel.title}")
    print(f"Slides: {carousel.get_slide_count()}\n")

    print("-" * 40)
    print("SLIDES")
    print("-" * 40)

    for slide in carousel.slides:
        print(f"\n[{slide.number}] {slide.slide_type.value.upper()}: {slide.title}")
        if slide.content:
            for item in slide.content:
                print(f"    • {item}")

    print("\n" + "-" * 40)
    print("CAPTION")
    print("-" * 40)

    print(f"\nHook:\n{carousel.caption.hook}")
    print(f"\nTeaser:\n{carousel.caption.teaser}")
    print(f"\nCTA:\n{carousel.caption.cta}")
    print(f"\nHashtags: {' '.join(f'#{tag}' for tag in carousel.caption.hashtags)}")

    print("\n" + "=" * 60)
    print("To generate full carousel, run with --topic instead of --outline")
    print("=" * 60 + "\n")


def run_generate(topic: str, slide_count: int = 6) -> None:
    """Generate full carousel with images and PDF.

    Args:
        topic: Topic for the carousel
        slide_count: Target number of slides
    """
    print("\n" + "=" * 60)
    print("GENERATING LINKEDIN CAROUSEL")
    print("=" * 60 + "\n")

    print(f"Topic: {topic}")
    print(f"Target slides: {slide_count}\n")

    # Create output directory
    output_dir, timestamp = create_output_directory()
    slides_dir = output_dir / "slides"
    print(f"Output: {output_dir}\n")

    # Step 1: Generate outline
    print("Step 1: Generating carousel outline...")
    carousel = generate_outline(topic, slide_count)
    print(f"  Title: {carousel.title}")
    print(f"  Slides: {carousel.get_slide_count()}")

    # Step 2: Generate backgrounds and render slides
    print("\nStep 2: Rendering slide images...")
    slide_paths: list[Path] = []

    for slide in carousel.slides:
        slide_filename = f"slide-{slide.number:02d}-{slide.slide_type.value}.png"
        slide_path = slides_dir / slide_filename

        # Generate background with embedded illustration
        bg_path = slides_dir / f"bg-{slide.number:02d}.png"
        generate_slide_background(slide, bg_path)

        # Render text on top (2x + downscale for crisp typography)
        render_slide(slide, slide_path, background_path=bg_path)

        slide_paths.append(slide_path)
        slide.local_path = str(slide_path)
        print(f"  Rendered: {slide_filename}")

    # Step 3: Assemble PDF
    print("\nStep 3: Assembling PDF carousel...")
    pdf_path = output_dir / "carousel.pdf"
    assemble_carousel_pdf(slide_paths, pdf_path, title=carousel.title)

    # Step 4: Save caption
    print("\nStep 4: Saving caption...")
    caption_text = carousel.caption.format()
    caption_path = save_caption(caption_text, output_dir)

    # Step 5: Save metadata
    print("\nStep 5: Saving metadata...")
    save_metadata(carousel, slide_paths, pdf_path, caption_path, output_dir, timestamp)

    # Summary
    print("\n" + "=" * 60)
    print("CAROUSEL GENERATION COMPLETE")
    print("=" * 60)
    print(f"\nOutput directory: {output_dir}")
    print(f"Slides: {len(slide_paths)} images")
    print(f"PDF: {pdf_path.name}")
    print(f"Caption: {caption_path.name}")

    print("\n" + "-" * 40)
    print("CAPTION PREVIEW")
    print("-" * 40)
    print(caption_text)
    print("-" * 40)

    print("\n" + "=" * 60 + "\n")


def run_review(draft: str) -> None:
    """Review and improve a carousel draft.

    Args:
        draft: Draft text to review
    """
    print("\n" + "=" * 60)
    print("REVIEWING CAROUSEL DRAFT")
    print("=" * 60 + "\n")

    print("Analyzing draft...")
    feedback = review_draft(draft)

    print("\n" + "-" * 40)
    print("FEEDBACK & IMPROVEMENTS")
    print("-" * 40)
    print(feedback)
    print("\n" + "=" * 60 + "\n")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate LinkedIn carousels with AI-powered slide creation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --topic "How to build a product roadmap"
  %(prog)s --topic "MTSS Framework Guide" --slides 8
  %(prog)s --outline "5 AI Tools for Productivity"
  %(prog)s --review "My draft carousel text..."
        """,
    )

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--topic",
        metavar="TOPIC",
        help="Generate full carousel from topic",
    )
    mode_group.add_argument(
        "--outline",
        metavar="TOPIC",
        help="Preview outline without generating images",
    )
    mode_group.add_argument(
        "--review",
        metavar="DRAFT",
        help="Review and improve existing draft",
    )

    parser.add_argument(
        "--slides",
        type=int,
        default=6,
        metavar="N",
        help="Target number of slides (default: 6, minimum: 5)",
    )

    args = parser.parse_args()

    try:
        if args.topic:
            run_generate(args.topic, args.slides)
        elif args.outline:
            run_outline(args.outline, args.slides)
        elif args.review:
            run_review(args.review)

    except KeyboardInterrupt:
        print("\n\nAborted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
