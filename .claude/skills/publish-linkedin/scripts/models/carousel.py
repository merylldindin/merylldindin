"""Data models for LinkedIn carousel generation."""

from enum import Enum

from pydantic import BaseModel, Field


class SlideType(str, Enum):
    """Slide type enumeration matching carousel blueprint."""

    COVER = "cover"
    CONTEXT = "context"
    CONTENT = "content"
    SUMMARY = "summary"
    CTA = "cta"


# Slide dimensions for LinkedIn carousel (4:5 portrait)
# True 4:5 ratio: 1080x1350
SLIDE_WIDTH: int = 1080
SLIDE_HEIGHT: int = 1350
SLIDE_ASPECT_RATIO: str = "4:5"


class CarouselSlide(BaseModel):
    """Single slide in a carousel."""

    number: int = Field(description="Slide position (1-indexed)")
    slide_type: SlideType = Field(description="Type of slide (cover, content, etc.)")
    title: str = Field(description="Main headline for the slide")
    content: list[str] = Field(
        default_factory=list,
        description="Bullet points or content lines (max 3-4 for readability)",
    )
    image_prompt: str | None = Field(
        default=None,
        description="Prompt for generating the slide image with Gemini",
    )
    local_path: str | None = Field(
        default=None, description="Local path to generated slide image"
    )


class PostCaption(BaseModel):
    """LinkedIn post caption with structured components."""

    hook: str = Field(
        description="First 2 lines visible before 'See more' - must stop the scroll"
    )
    teaser: str = Field(
        description="2-3 sentences after 'See more' expanding on the hook"
    )
    cta: str = Field(description="Single focused call to action")
    hashtags: list[str] = Field(
        description="3-5 relevant hashtags (mix of broad and niche)"
    )

    def format(self) -> str:
        """Format caption for LinkedIn posting."""
        hashtag_str = " ".join(f"#{tag}" for tag in self.hashtags)
        return f"{self.hook}\n\n{self.teaser}\n\n{self.cta}\n\n{hashtag_str}"


class Carousel(BaseModel):
    """Complete carousel with slides and caption."""

    topic: str = Field(description="Original topic/prompt for the carousel")
    title: str = Field(description="Carousel title (used in cover slide)")
    slides: list[CarouselSlide] = Field(description="Ordered list of slides")
    caption: PostCaption = Field(description="Post caption for the carousel")

    def get_slide_count(self) -> int:
        """Return total number of slides."""
        return len(self.slides)


class CarouselMetadata(BaseModel):
    """Metadata for a generated carousel."""

    topic: str = Field(description="Original topic/prompt")
    title: str = Field(description="Carousel title")
    slide_count: int = Field(description="Number of slides generated")
    slide_paths: list[str] = Field(description="Paths to individual slide images")
    pdf_path: str | None = Field(default=None, description="Path to assembled PDF")
    caption_path: str | None = Field(default=None, description="Path to caption file")
    output_dir: str = Field(description="Output directory path")
    timestamp: str = Field(description="Generation timestamp")
