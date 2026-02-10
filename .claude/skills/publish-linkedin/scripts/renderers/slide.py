"""Core slide rendering with Pillow at 2x resolution for crisp text."""

from pathlib import Path

from PIL import Image, ImageDraw

from models.carousel import CarouselSlide, SlideType
from renderers.layout import (
    BACKGROUND_COLOR,
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    CONTENT_WIDTH,
    FONT_SIZE_NUMBER,
    LINE_SPACING_BETWEEN,
    LINE_SPACING_WITHIN,
    MARGIN_HORIZONTAL,
    NUMBER_COLOR,
    NUMBER_TITLE_GAP,
    SLIDE_LAYOUTS,
    TEXT_COLOR,
    SlideLayout,
)
from renderers.typography import load_font, measure_text, wrap_text

# Render at 2x and downscale for smoother antialiasing
RENDER_SCALE: int = 2


def render_slide(
    slide: CarouselSlide,
    output_path: Path,
    background_path: Path | None = None,
) -> Path:
    """Render a single carousel slide to PNG.

    Renders text at 2x resolution then downscales with LANCZOS
    for crisp, smooth typography.

    Args:
        slide: CarouselSlide with content
        output_path: Path to save the rendered PNG
        background_path: Optional background image to use instead of solid white

    Returns:
        Path to the rendered image
    """
    s = RENDER_SCALE
    layout = SLIDE_LAYOUTS[slide.slide_type]
    canvas_w, canvas_h = CANVAS_WIDTH * s, CANVAS_HEIGHT * s

    if background_path and background_path.exists():
        img = Image.open(background_path).convert("RGB")
        img = img.resize((canvas_w, canvas_h), Image.LANCZOS)
    else:
        img = Image.new("RGB", (canvas_w, canvas_h), BACKGROUND_COLOR)

    draw = ImageDraw.Draw(img)

    if layout.has_number and slide.slide_type == SlideType.CONTENT:
        _draw_numbered_title(draw, slide, layout, s)
    else:
        _draw_centered_title(draw, slide, layout, s)

    if layout.has_subtitle and slide.content:
        _draw_subtitle(draw, slide, layout, s)
    elif slide.content and not layout.has_subtitle:
        _draw_body_blocks(draw, slide, layout, s)

    # Downscale for crisp text
    img = img.resize((CANVAS_WIDTH, CANVAS_HEIGHT), Image.LANCZOS)
    img.save(str(output_path), "PNG")
    return output_path


def _draw_numbered_title(
    draw: ImageDraw.ImageDraw, slide: CarouselSlide, layout: SlideLayout, s: int
) -> None:
    """Render '01 TITLE' with measured number width + gap."""
    parts = slide.title.split(" ", 1)
    if len(parts) == 2 and parts[0].isdigit():
        number_text = parts[0]
        title_text = parts[1]
    else:
        content_index = slide.number - 2
        number_text = f"{content_index:02d}"
        title_text = slide.title

    number_font = load_font(FONT_SIZE_NUMBER * s, bold=True)
    title_font = load_font(layout.title_font_size * s, bold=True)

    _, number_h = measure_text(draw, number_text, number_font)
    _, title_h = measure_text(draw, title_text, title_font)
    title_y_offset = number_h - title_h

    draw.text(
        (MARGIN_HORIZONTAL * s, layout.title_y * s),
        number_text,
        fill=NUMBER_COLOR,
        font=number_font,
    )

    number_width, _ = measure_text(draw, number_text, number_font)
    title_x = MARGIN_HORIZONTAL * s + number_width + NUMBER_TITLE_GAP * s

    draw.text(
        (title_x, layout.title_y * s + title_y_offset),
        title_text,
        fill=TEXT_COLOR,
        font=title_font,
    )


def _draw_centered_title(
    draw: ImageDraw.ImageDraw, slide: CarouselSlide, layout: SlideLayout, s: int
) -> None:
    """Render title centered horizontally."""
    font = load_font(layout.title_font_size * s, bold=True)
    text_width, _ = measure_text(draw, slide.title, font)
    x = (CANVAS_WIDTH * s - text_width) // 2

    draw.text(
        (x, layout.title_y * s),
        slide.title,
        fill=TEXT_COLOR,
        font=font,
    )


def _draw_subtitle(
    draw: ImageDraw.ImageDraw, slide: CarouselSlide, layout: SlideLayout, s: int
) -> None:
    """Render subtitle/question centered below title with word-wrap."""
    font = load_font(layout.body_font_size * s, bold=False)
    text = slide.content[0] if slide.content else ""
    if not text:
        return

    content_width = CONTENT_WIDTH * s
    wrapped_lines = wrap_text(draw, text, font, content_width)
    line_height = int(layout.body_font_size * s * LINE_SPACING_WITHIN)
    y = layout.subtitle_y * s

    for line in wrapped_lines:
        line_width, _ = measure_text(draw, line, font)
        x = (CANVAS_WIDTH * s - line_width) // 2
        draw.text((x, y), line, fill=TEXT_COLOR, font=font)
        y += line_height


def _draw_body_blocks(
    draw: ImageDraw.ImageDraw, slide: CarouselSlide, layout: SlideLayout, s: int
) -> None:
    """Render content list with text wrapping and block spacing."""
    font = load_font(layout.body_font_size * s, bold=False)
    y = layout.body_y * s
    line_height = int(layout.body_font_size * s * LINE_SPACING_WITHIN)
    block_spacing = int(layout.body_font_size * s * LINE_SPACING_BETWEEN)
    content_width = CONTENT_WIDTH * s

    for i, block_text in enumerate(slide.content):
        wrapped_lines = wrap_text(draw, block_text, font, content_width)

        for line in wrapped_lines:
            if layout.body_centered:
                line_width, _ = measure_text(draw, line, font)
                x = (CANVAS_WIDTH * s - line_width) // 2
            else:
                x = MARGIN_HORIZONTAL * s

            draw.text(
                (x, y),
                line,
                fill=TEXT_COLOR,
                font=font,
            )
            y += line_height

        if i < len(slide.content) - 1:
            y += block_spacing - line_height
