"""Layout constants and per-slide-type configurations."""

from dataclasses import dataclass

from models.carousel import SlideType

# Canvas dimensions (LinkedIn 4:5 portrait)
CANVAS_WIDTH: int = 1080
CANVAS_HEIGHT: int = 1350
BACKGROUND_COLOR: str = "#FFFFFF"
TEXT_COLOR: str = "#000000"
NUMBER_COLOR: str = "#AAAAAA"

# Margins
MARGIN_HORIZONTAL: int = 80
MARGIN_TOP: int = 100
CONTENT_WIDTH: int = CANVAS_WIDTH - 2 * MARGIN_HORIZONTAL  # 920px

# Font sizes
FONT_SIZE_TITLE_LARGE: int = 104  # Cover/CTA titles
FONT_SIZE_NUMBER: int = 76  # Content slide numbers
FONT_SIZE_TITLE: int = 76  # Content/context/summary titles
FONT_SIZE_SUBTITLE: int = 46  # Subtitles
FONT_SIZE_BODY: int = 44  # Body text

# Spacing multipliers (relative to font size)
LINE_SPACING_WITHIN: float = 1.8  # Within a block
LINE_SPACING_BETWEEN: float = 2.6  # Between blocks

# Number-title gap
NUMBER_TITLE_GAP: int = 20


@dataclass(frozen=True)
class SlideLayout:
    """Layout configuration for a slide type."""

    title_y: int
    title_font_size: int
    title_centered: bool
    body_y: int
    body_font_size: int
    body_centered: bool
    has_number: bool = False
    has_subtitle: bool = False
    subtitle_y: int = 0


SLIDE_LAYOUTS: dict[SlideType, SlideLayout] = {
    SlideType.COVER: SlideLayout(
        title_y=460,
        title_font_size=FONT_SIZE_TITLE_LARGE,
        title_centered=True,
        body_y=640,
        body_font_size=FONT_SIZE_SUBTITLE,
        body_centered=True,
        has_subtitle=True,
        subtitle_y=640,
    ),
    SlideType.CONTEXT: SlideLayout(
        title_y=120,
        title_font_size=FONT_SIZE_TITLE,
        title_centered=True,
        body_y=300,
        body_font_size=FONT_SIZE_BODY,
        body_centered=True,
    ),
    SlideType.CONTENT: SlideLayout(
        title_y=120,
        title_font_size=FONT_SIZE_TITLE,
        title_centered=False,
        body_y=320,
        body_font_size=FONT_SIZE_BODY,
        body_centered=False,
        has_number=True,
    ),
    SlideType.SUMMARY: SlideLayout(
        title_y=120,
        title_font_size=FONT_SIZE_TITLE,
        title_centered=True,
        body_y=300,
        body_font_size=FONT_SIZE_BODY,
        body_centered=True,
    ),
    SlideType.CTA: SlideLayout(
        title_y=460,
        title_font_size=FONT_SIZE_TITLE_LARGE,
        title_centered=True,
        body_y=650,
        body_font_size=FONT_SIZE_SUBTITLE,
        body_centered=True,
        has_subtitle=True,
        subtitle_y=650,
    ),
}
