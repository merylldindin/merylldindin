"""Image optimization utilities for LinkedIn carousel slides."""

from pathlib import Path

from PIL import Image

from models.carousel import SLIDE_HEIGHT, SLIDE_WIDTH


def fit_and_center_crop(image_path: Path, output_path: Path | None = None) -> Path:
    """Scale down proportionally to fit, then center crop to exact dimensions.

    Process:
    1. Scale down proportionally so image fits within target (no distortion)
    2. Center crop only the minimal remaining difference

    This preserves content while achieving exact dimensions.

    Args:
        image_path: Path to source image
        output_path: Optional output path (defaults to overwriting source)

    Returns:
        Path to processed image
    """
    output_path = output_path or image_path

    with Image.open(image_path) as img:
        # Convert to RGB if necessary (handles RGBA, P mode, etc.)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        width, height = img.size

        # Calculate scale factor to fit target dimensions
        # Use the LARGER ratio so the image covers the target area
        width_ratio = SLIDE_WIDTH / width
        height_ratio = SLIDE_HEIGHT / height
        scale_factor = max(width_ratio, height_ratio)

        # Only scale if image is larger than target
        if scale_factor < 1.0:
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            width, height = img.size

        # Now center crop to exact dimensions (should be minimal cropping)
        left = (width - SLIDE_WIDTH) // 2
        top = (height - SLIDE_HEIGHT) // 2
        right = left + SLIDE_WIDTH
        bottom = top + SLIDE_HEIGHT

        # Ensure coordinates are within bounds
        left = max(0, left)
        top = max(0, top)
        right = min(width, right)
        bottom = min(height, bottom)

        cropped = img.crop((left, top, right, bottom))

        # If the cropped image is still not exact size (source was smaller),
        # create a white canvas and paste centered
        if cropped.size != (SLIDE_WIDTH, SLIDE_HEIGHT):
            canvas = Image.new("RGB", (SLIDE_WIDTH, SLIDE_HEIGHT), (255, 255, 255))
            paste_x = (SLIDE_WIDTH - cropped.width) // 2
            paste_y = (SLIDE_HEIGHT - cropped.height) // 2
            canvas.paste(cropped, (paste_x, paste_y))
            cropped = canvas

        cropped.save(output_path, "PNG", optimize=True)

    return output_path


# Keep old name for backwards compatibility
center_crop_to_linkedin = fit_and_center_crop


def optimize_slide_image(image_path: Path, output_path: Path | None = None) -> Path:
    """Optimize a slide image for LinkedIn.

    Scales proportionally then center crops to exact dimensions.

    Args:
        image_path: Path to source image
        output_path: Optional output path (defaults to overwriting source)

    Returns:
        Path to optimized image
    """
    output_path = output_path or image_path

    with Image.open(image_path) as img:
        width, height = img.size

        # Check if processing is needed
        if width != SLIDE_WIDTH or height != SLIDE_HEIGHT:
            return fit_and_center_crop(image_path, output_path)

        # Convert mode if necessary
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Save with optimization
        img.save(output_path, "PNG", optimize=True)

    return output_path


def get_image_dimensions(image_path: Path) -> tuple[int, int]:
    """Get dimensions of an image.

    Args:
        image_path: Path to image file

    Returns:
        Tuple of (width, height)
    """
    with Image.open(image_path) as img:
        return img.size
