---
name: publish-linkedin
description: Generates LinkedIn carousels with AI-generated slides. Creates professional 1080x1350 portrait slides (4:5), assembles into PDF, and generates post captions with hashtags.
allowed-tools: Read, Glob, Bash, WebFetch
---

# LinkedIn Carousel Generator

Generates LinkedIn carousel posts with consistent brand identity. Creates slides using Gemini image generation, assembles them into a PDF carousel, and generates post captions with hashtags.

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
├── caption.md              # Post caption with hook + teaser + CTA + hashtags
├── slides/
│   ├── slide-01-cover.png
│   ├── slide-02-context.png
│   ├── slide-03-content.png
│   └── ...
└── carousel.pdf            # Final assembled PDF
```

## Visual Identity

Slides follow the portfolio's minimalist aesthetic:

- **Background**: Pure white (#FFFFFF)
- **Colors**: Black and white only - no colors, gradients, or gray tones
- **Text**: Bold, high-contrast, mobile-readable
- **Layout**: Clean, generous whitespace, all content CENTERED
- **Style**: Professional, modern, consistent
- **No author branding**: Clean slides without name/handle/photo
- **No borders**: Content extends to edges on white background
- **Content slides**: Use "01 TITLE", "02 TITLE" numbering format

## Specifications

- **Resolution**: 1080x1350 px (true 4:5 portrait)
- **Format**: PNG slides + PDF carousel
- **Model**: Gemini 3 Pro Image
- **Processing**: Center crop only (never resize/stretch)

See `references/visual-identity.md` for full style guidelines.
See `references/linkedin-guidelines.md` for publication strategy.
