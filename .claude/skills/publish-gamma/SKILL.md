---
name: publish-gamma
description: Generates LinkedIn carousels via Gamma MCP with AI-generated illustrations, exports PDF, and drafts post captions with hashtags.
allowed-tools: Read, Edit, Write, Glob, Bash, WebFetch, mcp__claude_ai_Gamma__generate, mcp__claude_ai_Gamma__get_themes, mcp__claude_ai_Gamma__get_folders
---

# LinkedIn Carousel Generator (Gamma MCP)

Generates LinkedIn carousel posts via the Gamma MCP integration. Creates slides with AI-generated conceptual illustrations, exports to PDF, and drafts post captions.

## When to Use

- Creating educational carousel posts for LinkedIn
- Generating thought leadership content with visual slides
- Sharing frameworks, guides, or step-by-step processes
- Building personal brand through visual carousel content

## Workflow

### Step 1: Structure the Content

Given a topic or raw content, structure it into 6-8 slides following the blueprint:

| Position     | Purpose  | Content Guidelines                  |
| ------------ | -------- | ----------------------------------- |
| Slide 1      | Cover    | Bold title, clear value promise     |
| Slide 2      | Context  | Why this matters, problem statement |
| Slides 3-N-2 | Content  | One core idea per slide             |
| Slide N-1    | Summary  | Checklist/recap (screenshot-worthy) |
| Slide N      | CTA      | Single focused question, no "share/tag" boilerplate |

### Step 2: Generate via Gamma MCP

Call `mcp__claude_ai_Gamma__generate` with these fixed settings:

```
format: "social"
cardOptions.dimensions: "4x5"
themeId: "sage" (default, or user-chosen)
textMode: "generate"
exportAs: "pdf"
imageOptions:
  source: "aiGenerated"
  model: "flux-1-pro"
  style: see Image Style section below
textOptions:
  tone: "professional"
  amount: "medium"
```

### Step 3: Draft Caption

Write a LinkedIn caption in `caption.md` following these rules:

- No emdashes (use commas, periods, or colons instead)
- Use emojis sparingly at emphasis points
- Structure: entry phrase, two paragraphs, closing sentence/question, hashtags
- Bundle sentences together, minimize breaklines
- Consistent tone throughout
- Hashtags: single `#`, proper casing, mix broad and niche (3-5 total)
- The draft is a starting point: always flag it needs manual rework before publishing

### Step 4: Review the PDF

After generation, download and review the exported PDF:

1. Download the PDF via `curl -sL -o /tmp/{slug}.pdf "{exportUrl}"`
2. Read the PDF with the Read tool to visually inspect all slides
3. Evaluate each slide against these criteria:
   - **Style consistency**: all images should match the hand-drawn ink sketch style with sage green accents. Flag any that drift to digital/vector, photorealistic, or different color palettes (cyan, teal, warm tones).
   - **No forbidden elements**: no text/labels in images, no realistic people/faces/hands, no real objects (pens, pencils, phones) that break the abstract/conceptual constraint.
   - **Background consistency**: cool gray or off-white tones across slides. Flag any warm beige or pure white backgrounds that break the visual rhythm.
   - **Illustration quality**: each image should be visually rich enough to match the strongest slides. Flag sparse or underwhelming illustrations.
   - **Text and layout**: verify text is concise, headlines are bold, and list-style slides use a consistent format throughout.
4. Present the review with:
   - What works well (strongest slides)
   - Issues to fix, organized by severity (required vs. optional)
   - For each image that needs fixing, provide a ready-to-use regeneration prompt that reinforces the hand-drawn ink style, specifies the conceptual metaphor, and explicitly excludes the problem observed (e.g., "No digital/vector styling", "No realistic objects")

### Step 5: Output Summary

Present to user:
- Gamma deck URL (for editing)
- PDF download URL
- Caption draft
- List of slides with titles
- Review findings with image fix prompts for any inconsistent slides

## Image Style Guidelines

Every slide gets a per-concept image brief in the prompt. All images must follow a single consistent style:

```
style: "minimalist hand-drawn scientific illustration, like a researcher's
notebook sketch. Thin ink lines, monochrome with subtle sage green accents
only. Slightly abstract, conceptual. No text, no words, no labels, no
letters inside the image. No realistic people, no faces, no hands, no
skin tones. Only scientific diagrams, conceptual sketches, and abstract
representations."
```

### Image Concept Rules

- Each slide's `inputText` must include an "Image concept:" line describing what the illustration should depict
- Concepts should be metaphorical/scientific: overflowing vessels, tangling paths, tipping scales, branching networks, converging arrows
- Never use: realistic human figures, colored objects that break monochrome, text/labels in images, stock-art style illustrations
- Maintain strict visual consistency: same line weight, same color palette (black ink + sage green accents), same abstraction level across all 8 slides

### additionalInstructions Template

Always include in `additionalInstructions`:

```
CRITICAL IMAGE RULES:
- All images must use the SAME consistent style: monochrome hand-drawn ink
  with subtle sage green accents. No color variation between slides.
- No text, words, labels, or letters rendered inside any image.
- No realistic people, faces, hands, or skin tones.
- Each slide has an "Image concept:" — use it to generate a unique,
  conceptually relevant illustration per slide.
- Use the theme's colored backgrounds on alternating slides (soft sage,
  muted green, warm off-white). No pure white backgrounds.
- Pick ONE layout pattern for list-style slides and use it consistently
  across all of them (either cards, numbered dividers, or inline lists —
  not a mix).
- Do NOT add "share this" / "tag someone" / promotional language to any slide.
- Do NOT include any personal attribution or author name on slides.
```

## Slide Text Rules

- Max ~40 words of body text per slide
- One core idea per content slide
- Bold headline at top of every slide
- For list slides: pick one format (numbered list with dividers recommended) and apply to ALL list slides consistently
- No bullet point mixing: do not alternate between card grids, inline lists, and numbered formats across slides
- Closing line on summary slide should be a memorable, quotable takeaway

## Caption Template

```markdown
[Entry phrase — hook the reader in one sentence]

[Paragraph 1 — context and core insight, 2-3 sentences bundled together]

[Paragraph 2 — key takeaway or implication, 2-3 sentences bundled together]

[Closing question or call to reflection]

#Hashtag1 #Hashtag2 #Hashtag3 #Hashtag4
```

## Theme Selection

Default theme is `sage`. If user requests a different visual feel:

1. Call `mcp__claude_ai_Gamma__get_themes` to browse options
2. Match theme tone/color keywords to user's request and topic
3. Adjust image style's accent color to match chosen theme

## Known Gamma Limitations

- Cannot review/screenshot generated slides via MCP (no read endpoint), but the exported PDF can be downloaded and reviewed directly via the Read tool
- `textMode: "preserve"` strips all visual styling — always use `generate`
- `noImages` removes all backgrounds and visual elements — avoid
- `pictographic` pulls from a generic stock library with frequent mismatches — avoid
- AI image generation may produce inconsistent styles across slides despite instructions; flag this for manual cleanup
- Gamma may re-inject "share/tag" boilerplate on CTA slides despite instructions; flag for removal

## Output Structure

No local files are created. Outputs are hosted on Gamma:

```
Gamma deck: https://gamma.app/docs/{id}    (editable)
PDF export: https://assets.api.gamma.app/... (downloadable)
Caption:    drafted inline or saved to caption.md in working directory
```
