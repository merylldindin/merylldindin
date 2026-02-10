"""Slide background generation using Gemini with embedded illustrations."""

import time
from pathlib import Path

from google import genai
from google.genai import types

from models.carousel import CarouselSlide, SlideType

GEMINI_IMAGE_MODEL: str = "gemini-3-pro-image-preview"

ILLUSTRATION_HINTS: dict[SlideType, str] = {
    SlideType.COVER: "An abstract, conceptual visual representing the topic. Geometric shapes, flowing lines, or symbolic imagery.",
    SlideType.CONTEXT: "A data visualization icon or concept diagram. Think charts, graphs, or analytical symbols.",
    SlideType.CONTENT: "A concept-specific diagram or icon illustrating the key idea. Simple, explanatory visual.",
    SlideType.SUMMARY: "A clean recap visual. Connected elements, synthesis diagram, or unified composition.",
    SlideType.CTA: "A minimal directional element. An arrow, a path, or a simple gesture toward action.",
}

PLACEMENT_HINTS: dict[SlideType, str] = {
    SlideType.COVER: "Text will occupy the center of the slide. Place a small illustration in the bottom 25%, centered horizontally. Keep it compact.",
    SlideType.CONTEXT: "Title is at the top, body text fills the upper 45%. Place a small illustration in the bottom 30%, centered horizontally. Keep it compact.",
    SlideType.CONTENT: "Title and body text occupy the upper 50%. Place a small illustration in the bottom 30%, centered horizontally. Keep it compact.",
    SlideType.SUMMARY: "Title is at the top, recap points fill the upper 50%. Place a small illustration in the bottom 25%, centered horizontally. Keep it compact.",
    SlideType.CTA: "Text is centered in the middle of the slide. Place a small illustration in the bottom 25%, centered horizontally. Keep it compact.",
}


def _build_prompt(slide: CarouselSlide) -> str:
    """Build prompt for combined background + illustration generation."""
    illustration_hint = ILLUSTRATION_HINTS.get(slide.slide_type, "A simple conceptual icon.")
    placement_hint = PLACEMENT_HINTS.get(slide.slide_type, "Place the illustration in the bottom 40%.")

    content_context = ""
    if slide.content:
        content_context = f"\nSlide content for context: {', '.join(slide.content[:3])}"

    return f"""Generate a professional slide background with an embedded illustration element.

Topic context: {slide.title}{content_context}

BACKGROUND (covers the entire slide):
- Pure white base (#FFFFFF) with very subtle light gray accents (#F0F0F0 to #E8E8E8)
- Abstract geometric texture: soft circles, thin lines, gentle arcs, or organic forms
- Extremely minimal and understated, like a watermark
- The texture should flow naturally across the entire slide

ILLUSTRATION (small, embedded in the background, not a separate layer):
- Delicate black line art (#000000) with fine, consistent 1px stroke weight
- Keep the illustration SMALL and compact, no more than 20% of the slide area
- {illustration_hint}
- {placement_hint}
- The illustration should blend naturally with the background texture
- NO text, words, letters, or numbers in the illustration

OVERALL:
- Portrait 4:5 aspect ratio (1080x1350)
- Leave the text areas clear for overlay (text will be rendered on top separately)
- Clean, sophisticated, editorial feel
- The background and illustration should feel like one cohesive composition
- NO borders or frames
"""


def _extract_image(response: types.GenerateContentResponse) -> bytes:
    """Extract image bytes from a Gemini response."""
    if not response.candidates:
        raise RuntimeError("No candidates in generation response")

    candidate = response.candidates[0]
    if not candidate.content or not candidate.content.parts:
        raise RuntimeError("Empty content in generation response")

    for part in candidate.content.parts:
        if part.inline_data is not None:
            return part.inline_data.data

    raise RuntimeError("No image data found in response")


def generate_slide_background(
    slide: CarouselSlide,
    output_path: Path,
    max_retries: int = 3,
) -> Path:
    """Generate a slide background with embedded illustration using Gemini.

    Produces a single image combining subtle background texture and
    illustration element, avoiding the white-rectangle-on-texture problem
    that separate generation + compositing creates.

    Args:
        slide: CarouselSlide with content context
        output_path: Path to save the PNG file
        max_retries: Maximum retry attempts on failure

    Returns:
        Path to the generated background image
    """
    client: genai.Client = genai.Client()
    prompt = _build_prompt(slide)

    print(f"  Generating background for slide {slide.number} ({slide.slide_type.value})...")

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_IMAGE_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(
                        aspectRatio="4:5",
                        imageSize="2K",
                    ),
                ),
            )

            image_data = _extract_image(response)
            output_path.write_bytes(image_data)
            print(f"    Saved: {output_path.name}")
            return output_path

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time: float = (attempt + 1) * 2.0
                print(f"    Retry {attempt + 1}/{max_retries} after {wait_time}s: {e}")
                time.sleep(wait_time)
            else:
                raise RuntimeError(
                    f"Failed to generate background for slide {slide.number} after {max_retries} attempts: {e}"
                ) from e

    raise RuntimeError(f"Failed to generate background for slide {slide.number}")
