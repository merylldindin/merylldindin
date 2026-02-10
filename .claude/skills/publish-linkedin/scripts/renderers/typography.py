"""Font loading and text utilities for slide rendering."""

from functools import lru_cache
from pathlib import Path

from PIL import ImageDraw, ImageFont

FONT_PATH: Path = Path("/System/Library/Fonts/HelveticaNeue.ttc")
FONT_INDEX_REGULAR: int = 10  # Medium weight for smoother body text
FONT_INDEX_BOLD: int = 1


@lru_cache(maxsize=16)
def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load HelveticaNeue font at given size.

    Args:
        size: Font size in points
        bold: Whether to use bold weight

    Returns:
        PIL FreeTypeFont instance
    """
    index = FONT_INDEX_BOLD if bold else FONT_INDEX_REGULAR
    return ImageFont.truetype(str(FONT_PATH), size=size, index=index)


def measure_text(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont
) -> tuple[int, int]:
    """Measure text dimensions.

    Args:
        draw: PIL ImageDraw instance
        text: Text string to measure
        font: Font to use for measurement

    Returns:
        Tuple of (width, height)
    """
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    """Word-level greedy line wrapping.

    Args:
        draw: PIL ImageDraw instance
        text: Text to wrap
        font: Font for width measurement
        max_width: Maximum line width in pixels

    Returns:
        List of wrapped lines
    """
    words = text.split()
    if not words:
        return []

    lines: list[str] = []
    current_line = words[0]

    for word in words[1:]:
        test_line = f"{current_line} {word}"
        width, _ = measure_text(draw, test_line, font)

        if width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)
    return lines
