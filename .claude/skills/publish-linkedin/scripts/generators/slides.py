"""Slide image generation using Gemini for LinkedIn carousels."""

import time
from pathlib import Path

from google import genai
from google.genai import types

from models.carousel import SLIDE_ASPECT_RATIO, CarouselSlide, SlideType

GEMINI_IMAGE_MODEL: str = "gemini-3-pro-image-preview"

# Visual identity for LinkedIn slides - adapted from portfolio style
SLIDE_STYLE_SUFFIX: str = """
Style Requirements (CRITICAL - MUST FOLLOW EXACTLY):

LAYOUT (CRITICAL FOR CROPPING):
- ALL content must be CENTERED both horizontally and vertically
- Keep ALL text and graphics within the CENTER 80% of the image
- Leave GENEROUS margins on ALL sides (at least 10% from each edge)
- Edges WILL be cropped - never place important content near edges

COLORS:
- Background: Pure WHITE (#FFFFFF) only
- Text: Pure BLACK (#000000) only
- Graphics/icons: Black lines on white only
- NO colors whatsoever - strictly black and white
- NO gray tones except for slide numbers (which can be light gray #AAAAAA)

TYPOGRAPHY (CRITICAL - MUST BE UNIFORM):
- Font: Clean sans-serif (like Helvetica, Arial, or Inter)
- Title text: BOLD weight, equivalent to 48-56pt
- Body text: REGULAR weight, equivalent to 24-28pt
- Slide numbers (01, 02, 03): BOLD weight, equivalent to 64-72pt, light gray (#AAAAAA)
- ALL slides must use IDENTICAL font family and weights
- Line spacing: 1.8x minimum - generous vertical space between lines
- Paragraph spacing: Extra space between distinct points (24pt+ gap)
- Letter spacing: Normal (not condensed, not expanded)

TEXT FORMATTING (CRITICAL):
- NO bullet points (•)
- NO checkmarks (✓)
- NO dashes or hyphens as list markers
- Use PLAIN TEXT only with generous line spacing
- Separate points with vertical whitespace, not markers

VISUAL ELEMENTS (ENCOURAGED):
- Large standalone numbers as focal points (e.g., "48%" in large text)
- Simple line charts showing trends (black lines on white)
- Minimal diagrams with arrows showing relationships
- Data callouts: big number + small label below
- Timeline markers for key dates
- Keep visuals simple, black and white, geometric

PROHIBITIONS:
- NO borders, frames, or edge decorations
- NO colors, gradients, or shadows
- NO complex graphics or busy backgrounds
- NO stock photo elements
- NO human faces or bodies
- NO content near edges (will be cropped)
- NO mixing of font weights (only BOLD for titles, REGULAR for body)
- NO decorative or script fonts
- NO bullet points (•) or list markers
- NO checkmarks (✓ or ✔)
- NO dashes, arrows, or icons as text prefixes
- NO emojis
- NO duplicated text - each line appears ONCE only
- NO repeated titles or content
- NO repeating the same sentence twice on one slide
- If a phrase appears once, it must NOT appear again

FORMAT: 1080x1350 pixels (4:5 portrait for LinkedIn carousel)

GRAPHS/CHARTS (if included):
- Black lines on white background only
- Label axes clearly with specific numbers
- Include real data points
- Keep chart centered with margins
- Use same font as slide text for labels
"""

# Style reference instruction when using previous slide as reference
STYLE_REFERENCE_INSTRUCTION: str = """
STYLE REFERENCE (CRITICAL - MATCH EXACTLY):
The attached image shows the EXACT style to replicate. You MUST match:
- EXACT same font family (do not change fonts)
- EXACT same font weights (bold titles, regular body)
- EXACT same title text size (measure it, match it precisely)
- EXACT same body text size
- EXACT same margins and spacing
- EXACT same layout structure

COMMON MISTAKES TO AVOID:
- Do NOT make the title smaller or larger than the reference
- Do NOT change font weights
- Do NOT add elements not in the reference (no icons, no decorations)
- Do NOT repeat text or duplicate content
- Each piece of text should appear ONCE only

Generate a new slide with different content but PIXEL-PERFECT identical typography.
"""


def build_slide_prompt(slide: CarouselSlide) -> str:
    """Build enhanced prompt for slide image generation.

    Args:
        slide: CarouselSlide with content to render

    Returns:
        Enhanced prompt with style requirements
    """
    # Build content description
    content_desc = ""
    if slide.content:
        content_desc = "\n".join(f"• {item}" for item in slide.content)

    # Customize prompt based on slide type
    if slide.slide_type == SlideType.COVER:
        type_instruction = """
This is a COVER SLIDE. Design requirements:
- Title: TWO WORDS ONLY, BOLD sans-serif (NOT italic), 56-64pt, perfectly CENTERED
- Title must be BLACK, BOLD, SANS-SERIF - same font family as all slides
- Title must fit on ONE line - never break across lines
- NO italic fonts anywhere
- Subtitle (if any): REGULAR weight sans-serif, 24-28pt, below title with spacing
- Maximum impact, minimum text
- The title dominates the CENTER of the slide
- Keep text away from edges (will be cropped)
- NO numbering on cover slide
"""
    elif slide.slide_type == SlideType.CONTEXT:
        type_instruction = """
This is a CONTEXT SLIDE. Design requirements:
- Title: TWO WORDS ONLY, BOLD sans-serif (NOT italic), 48-56pt, CENTERED at top
- Title must fit on ONE line - never break across lines
- Title must be BLACK, BOLD, SANS-SERIF
- NO italic fonts anywhere
- Body text: REGULAR weight sans-serif, 24-28pt
- NO bullet points or markers - plain text only
- Generous line spacing (1.8x) between lines
- Can include ONE simple visual (icon, small chart, or data callout)
- All content CENTERED in the middle 80% of the slide
- Include SPECIFIC statistics or data points
- Keep generous margins - edges will be cropped
- NO numbering on context slide
"""
    elif slide.slide_type == SlideType.CONTENT:
        type_instruction = f"""
This is a CONTENT SLIDE. Design requirements:

TITLE AREA (CRITICAL - MUST BE PIXEL-PERFECT ACROSS ALL CONTENT SLIDES):
- The title area starts at EXACTLY Y=100px from the top edge
- NUMBER: "{slide.number - 2:02d}" in BOLD, 64-72pt, light gray (#AAAAAA), at X=80px Y=100px
- TITLE: BOLD sans-serif, 48pt EXACTLY (not 46, not 50 - exactly 48pt), black
- Title positioned immediately right of number on the SAME LINE
- Layout: "{slide.number - 2:02d}  TITLE" on one line at Y=100px
- Title MUST NOT wrap to a second line - keep it to 2-3 words
- The number+title combination must look IDENTICAL in position and size on every content slide

BODY AREA:
- Body text starts at EXACTLY Y=250px from top edge (same on all content slides)
- Body text: REGULAR weight, 24-28pt, black
- NO bullet points or markers - plain text only
- Generous line spacing (1.8x) between lines

VISUAL ELEMENTS (include one, positioned consistently):
- A large data callout (e.g., "48%" in 72pt with small label below)
- A simple trend line or chart (black lines, labeled)
- A minimal icon or diagram
- Visual element should be placed BELOW body text or integrated into layout

- All content CENTERED within the middle 80% of the slide
- Keep ALL content away from edges
- Same font family as all other slides
- NO duplicated text - each element appears ONCE
"""
    elif slide.slide_type == SlideType.SUMMARY:
        type_instruction = """
This is a SUMMARY SLIDE. Design requirements:
- Title: TWO WORDS ONLY, BOLD sans-serif (NOT italic), 48-56pt, CENTERED at top
- Title must fit on ONE line - never break across lines
- Title must be BLACK, BOLD, SANS-SERIF
- NO italic fonts anywhere
- Body text: REGULAR weight sans-serif, 24-28pt
- NO checkmarks, bullets, or any visual markers
- Plain text only with generous vertical spacing
- Generous line spacing (1.8x) between lines
- All key points visible, properly spaced
- Keep content in center 80% - edges will be cropped
- NO numbering on summary slide
"""
    elif slide.slide_type == SlideType.CTA:
        type_instruction = """
This is a CTA (Call to Action) SLIDE. Design requirements:
- Title: TWO WORDS ONLY, BOLD sans-serif (NOT italic), 56-64pt, CENTERED
- Title must fit on ONE line - never break across lines
- Title must be BLACK, BOLD, SANS-SERIF
- NO italic fonts anywhere

CONTENT RULES (CRITICAL - THIS SLIDE MUST BE DIFFERENT FROM THE SUMMARY):
- ONLY include: the two-word title + one short question below it
- Maximum 2 lines of text total (title + question)
- DO NOT repeat ANY content from the summary or other slides
- DO NOT include statistics, data, findings, or recap points
- DO NOT list multiple points - just ONE question
- Keep it minimal: lots of whitespace

- Simple design with lots of whitespace
- Keep text in CENTER - away from all edges
- NO numbering on CTA slide
"""
    else:
        type_instruction = ""

    prompt = f"""Create a professional LinkedIn carousel slide image.

SLIDE TYPE: {slide.slide_type.value.upper()}
{type_instruction}

TITLE: {slide.title}

{f"CONTENT:{chr(10)}{content_desc}" if content_desc else ""}

{slide.image_prompt}

{SLIDE_STYLE_SUFFIX}"""

    return prompt


def generate_slide_image(
    slide: CarouselSlide,
    output_path: Path,
    reference_image_path: Path | None = None,
    max_retries: int = 3,
) -> Path:
    """Generate a single slide image using Gemini.

    Args:
        slide: CarouselSlide with content to render
        output_path: Path to save the PNG file
        reference_image_path: Optional path to previous slide for style consistency
        max_retries: Maximum retry attempts on failure

    Returns:
        Path to the generated image
    """
    client: genai.Client = genai.Client()

    enhanced_prompt = build_slide_prompt(slide)

    # Build multimodal content if reference image provided
    if reference_image_path and reference_image_path.exists():
        print(f"  Generating slide {slide.number} ({slide.slide_type.value}) with style reference...")
        # Add style reference instruction
        enhanced_prompt = STYLE_REFERENCE_INSTRUCTION + "\n\n" + enhanced_prompt
        # Load reference image
        reference_image_bytes = reference_image_path.read_bytes()
        contents = [
            types.Part.from_bytes(data=reference_image_bytes, mime_type="image/png"),
            enhanced_prompt,
        ]
    else:
        print(f"  Generating slide {slide.number} ({slide.slide_type.value})...")
        contents = enhanced_prompt

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_IMAGE_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(
                        aspectRatio=SLIDE_ASPECT_RATIO,
                        imageSize="2K",
                    ),
                ),
            )

            if not response.candidates:
                raise RuntimeError("No candidates in image generation response")

            candidate = response.candidates[0]
            if not candidate.content or not candidate.content.parts:
                raise RuntimeError("Empty content in image generation response")

            for part in candidate.content.parts:
                if part.inline_data is not None:
                    image_data: bytes = part.inline_data.data
                    output_path.write_bytes(image_data)
                    print(f"    Saved: {output_path.name}")
                    return output_path

            raise RuntimeError("No image data found in response")

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time: float = (attempt + 1) * 2.0
                print(f"    Retry {attempt + 1}/{max_retries} after {wait_time}s: {e}")
                time.sleep(wait_time)
            else:
                raise RuntimeError(
                    f"Failed to generate slide {slide.number} after {max_retries} attempts: {e}"
                ) from e

    # This should never be reached due to the raise in the loop
    raise RuntimeError(f"Failed to generate slide {slide.number}")
