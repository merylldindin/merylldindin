---
name: publish-linkedin
description: Generates LinkedIn carousels with AI-generated slides. Creates professional 1080x1350 portrait slides (4:5), assembles into PDF, and generates post captions with hashtags.
allowed-tools: Read, Edit, Write, Glob, Bash, WebFetch
---

# LinkedIn Carousel Generator

Generates LinkedIn carousel posts with consistent brand identity. Creates slides using Pillow text rendering + Gemini background/illustration generation, assembles them into a PDF carousel, and generates post captions with hashtags.

## When to Use

- Creating educational carousel posts for LinkedIn
- Generating thought leadership content
- Sharing frameworks, guides, or step-by-step processes
- Building personal brand through visual content

## Commands

Run from `.claude/skills/publish-linkedin/`:

```bash
# Generate full carousel from topic
uv run python scripts/publish_linkedin.py --topic "How to build a product roadmap"

# Generate with specific slide count
uv run python scripts/publish_linkedin.py --topic "MTSS Framework Guide" --slides 8

# Preview outline without generating images
uv run python scripts/publish_linkedin.py --outline "Topic"

# Review/rewrite existing draft
uv run python scripts/publish_linkedin.py --review "draft text here"
```

## Slide Blueprint

| Position     | Purpose         | Content Guidelines                    |
| ------------ | --------------- | ------------------------------------- |
| Slide 1      | Cover           | Bold title, clear value promise       |
| Slide 2      | Context         | Why this matters, problem statement   |
| Slides 3-N-2 | Content         | One core idea per slide               |
| Slide N-1    | Summary         | Checklist/recap (screenshot-worthy)   |
| Slide N      | CTA             | Single focused call to action         |

## Output Structure

Each generation creates a timestamped folder:

```
output/YYYYMMDD-HHMMSS/
├── metadata.json           # Generation details
├── caption.md              # Post caption (ALWAYS rework manually, see below)
├── slides/
│   ├── bg-01.png           # Gemini background+illustration per slide
│   ├── slide-01-cover.png  # Final slide with text rendered on background
│   ├── slide-02-context.png
│   └── ...
└── carousel.pdf            # Final assembled PDF
```

## Caption: Always Rework After Generation

The AI-generated caption is a **starting draft only**. Always rewrite `caption.md` before publishing:

- Add emojis sparingly at emphasis points (hook, paragraph ends, CTA)
- No emdashes: use commas, periods, or colons instead
- Structure: entry phrase, two paragraphs, closing question, hashtags
- Bundle sentences together, minimize breaklines
- Be more verbose than the draft: expand context, add specific data points and examples
- Clean up hashtags: single `#`, proper casing, mix of broad and niche (3-5 total)
- Consistent tone throughout

## Visual Identity

Slides use a hybrid rendering pipeline:

- **Backgrounds**: Gemini-generated per slide (white base + light gray texture + embedded illustration)
- **Text**: Pillow-rendered at 2x resolution with Helvetica Neue Medium, downscaled with LANCZOS for crisp typography
- **Illustrations**: Fine black line art (1px stroke) embedded in background, positioned in lower 25-30% of slide
- **Layout**: Clean, generous whitespace, centered titles with centered body text (except content slides which are left-aligned with numbered headers)
- **No author branding**: Clean slides without name/handle/photo
- **No borders**: Content extends to edges on white background
- **Content slides**: Use "01 TITLE", "02 TITLE" numbering format

## Specifications

- **Resolution**: 1080x1350 px (true 4:5 portrait)
- **Render scale**: 2x internal, LANCZOS downscaled
- **Font**: Helvetica Neue Medium (body), Helvetica Neue Bold (titles)
- **Format**: PNG slides + PDF carousel
- **Image model**: Gemini 3 Pro Image Preview
- **Text model**: Claude (outline + caption generation)

See `references/linkedin-guidelines.md` for publication strategy.
