"""Content generation for LinkedIn carousels using Gemini."""

import json

from google import genai
from google.genai import types

from models.carousel import (
    Carousel,
    CarouselSlide,
    PostCaption,
    SlideType,
)

GEMINI_TEXT_MODEL: str = "gemini-3-pro-preview"


def generate_outline(topic: str, slide_count: int = 6) -> Carousel:
    """Generate carousel outline from a topic.

    Args:
        topic: The topic or concept for the carousel
        slide_count: Target number of slides (default 6, min 5)

    Returns:
        Carousel object with structured slides and caption
    """
    slide_count = max(5, slide_count)  # Minimum 5 slides for proper structure

    # Calculate content slide count for numbering
    content_slide_count = slide_count - 4  # Minus cover, context, summary, cta

    prompt = f"""Create a LinkedIn carousel outline for the topic: "{topic}"

Generate exactly {slide_count} slides following this blueprint:

1. COVER (Slide 1): Bold, provocative title (5-8 words). Clear value promise. NO numbering.
2. CONTEXT (Slide 2): Why this matters. Problem statement with SPECIFIC data/statistics. NO numbering.
3. CONTENT (Slides 3 to {slide_count - 2}): One core idea per slide. MUST use consistent "0X TITLE" format.
   - Content slides are numbered 01, 02, 03... sequentially
   - Title format: "01 MAIN CONCEPT" (number + space + title in caps)
   - Include specific numbers, percentages, or data points in bullet points
4. SUMMARY (Slide {slide_count - 1}): Condensed checklist recap. Screenshot-worthy. NO numbering.
5. CTA (Slide {slide_count}): Single focused call to action. NO numbering. MINIMAL TEXT ONLY - just a headline and one short question. Do NOT repeat any data or findings from previous slides.

CONTENT SLIDE NUMBERING (CRITICAL):
- Slide 3 title format: "01 [CONCEPT]"
- Slide 4 title format: "02 [CONCEPT]"
- Slide 5 title format: "03 [CONCEPT]"
- And so on...

DATA REQUIREMENTS:
- Include specific statistics, percentages, or numbers wherever possible
- Example: "35-50% growth in usage" not "significant growth"
- Example: "280,000 academic talks analyzed" not "many talks analyzed"
- Ground claims in concrete data points

For each slide, provide:
- title: Main headline (for content slides, MUST start with "01 ", "02 ", "03 " etc.)
- content: 2-4 text lines with SPECIFIC data (for content slides) or empty for cover/CTA
- image_prompt: Detailed prompt for generating a professional LinkedIn slide image

TEXT FORMATTING (CRITICAL):
- NO bullet points, checkmarks, dashes, or any list markers
- Write content as plain text lines separated by whitespace
- Use generous line spacing between points

IMAGE PROMPT REQUIREMENTS (CRITICAL):
The image_prompt must explicitly describe:
- Pure white background (#FFFFFF) - NO borders, frames, or edges
- ALL content CENTERED in the middle of the slide with large margins
- Black text only - NO colors, NO gray backgrounds
- NO bullet points, checkmarks, or visual markers - plain text with spacing
- Generous line spacing (1.8x) between text lines
- For content slides: The number "01" (or 02, 03) in gray, followed by bold title
- Title must be SAME SIZE across all content slides

VISUAL ELEMENTS (each content slide should include ONE):
- A large data callout: big number (72pt) with small label below (e.g., "48%" with "increase in 'delve' usage")
- A simple trend line showing before/after change
- A minimal arrow diagram showing a relationship
- A timeline marking key dates

Example: "Create a slide with '01' in gray, 'THE FINDING' in bold black (same size as other slides). Include a large '48%' as a visual focal point with 'usage increase' below it. Add 1-2 lines of context text. Pure white background, black elements only."

NO DUPLICATED CONTENT - each text element appears exactly ONCE

Also generate:
- carousel_title: Overall title for the carousel
- caption: LinkedIn post caption with hook, teaser, cta, and hashtags

Respond in this exact JSON format:
{{
    "carousel_title": "string",
    "slides": [
        {{
            "number": 1,
            "slide_type": "cover|context|content|summary|cta",
            "title": "string",
            "content": ["bullet1", "bullet2"],
            "image_prompt": "string"
        }}
    ],
    "caption": {{
        "hook": "First 2 lines visible before See more",
        "teaser": "2-3 sentences after See more",
        "cta": "Single call to action",
        "hashtags": ["tag1", "tag2", "tag3"]
    }}
}}

TONE (CRITICAL):
- Direct and analytical, NOT sensationalist or alarmist
- Avoid dramatic phrases like "undeniable", "shocking", "crisis", "alarming"
- Use measured, evidence-based language
- Present findings objectively, let the data speak
- Example: "Research shows..." not "The data is undeniable..."
- Example: "A notable shift" not "A dramatic transformation"

Make the content actionable, specific, and data-driven. Use Meryll Dindin's voice: direct, analytical, evidence-based. Include specific numbers and statistics from the topic."""

    client: genai.Client = genai.Client()

    response = client.models.generate_content(
        model=GEMINI_TEXT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.7,
        ),
    )

    if not response.text:
        raise RuntimeError("Empty response from content generation")

    data = json.loads(response.text)

    slides = [
        CarouselSlide(
            number=s["number"],
            slide_type=SlideType(s["slide_type"]),
            title=s["title"],
            content=s.get("content", []),
            image_prompt=s["image_prompt"],
        )
        for s in data["slides"]
    ]

    caption = PostCaption(
        hook=data["caption"]["hook"],
        teaser=data["caption"]["teaser"],
        cta=data["caption"]["cta"],
        hashtags=data["caption"]["hashtags"],
    )

    return Carousel(
        topic=topic,
        title=data["carousel_title"],
        slides=slides,
        caption=caption,
    )


def generate_caption(topic: str, slide_titles: list[str]) -> PostCaption:
    """Generate LinkedIn post caption for a carousel.

    Args:
        topic: The carousel topic
        slide_titles: List of slide titles for context

    Returns:
        PostCaption with hook, teaser, cta, and hashtags
    """
    prompt = f"""Create a LinkedIn post caption for a carousel about: "{topic}"

The carousel covers these points:
{chr(10).join(f'- {title}' for title in slide_titles)}

Generate:
1. hook: First 2 lines visible before "See more" - must stop the scroll
2. teaser: 2-3 sentences expanding on the hook (shown after clicking "See more")
3. cta: Single focused call to action (save, follow, comment, or share)
4. hashtags: 3-5 relevant hashtags (mix of broad reach and niche)

Use Meryll Dindin's voice: direct, analytical, no fluff.

Respond in JSON format:
{{
    "hook": "string",
    "teaser": "string",
    "cta": "string",
    "hashtags": ["tag1", "tag2", "tag3"]
}}"""

    client: genai.Client = genai.Client()

    response = client.models.generate_content(
        model=GEMINI_TEXT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.7,
        ),
    )

    if not response.text:
        raise RuntimeError("Empty response from caption generation")

    data = json.loads(response.text)

    return PostCaption(
        hook=data["hook"],
        teaser=data["teaser"],
        cta=data["cta"],
        hashtags=data["hashtags"],
    )


def review_draft(draft: str) -> str:
    """Review and improve a carousel draft.

    Args:
        draft: Existing draft text to review

    Returns:
        Improved version with suggestions
    """
    prompt = f"""Review this LinkedIn carousel draft and improve it:

{draft}

Provide:
1. Specific improvements for each slide
2. Hook optimization suggestions
3. Better phrasing for clarity and impact
4. Any missing elements from the carousel blueprint

Format your response as actionable feedback with improved text alternatives."""

    client: genai.Client = genai.Client()

    response = client.models.generate_content(
        model=GEMINI_TEXT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
        ),
    )

    if not response.text:
        raise RuntimeError("Empty response from review")

    return response.text
