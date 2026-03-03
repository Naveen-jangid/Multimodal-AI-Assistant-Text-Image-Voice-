"""Image preprocessing utilities for vision analysis."""

import base64
from PIL import Image
import io


SUPPORTED_FORMATS = {"image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"}
MAX_IMAGE_SIZE = (1024, 1024)  # Max dimensions to keep API costs reasonable


def encode_image(image_bytes: bytes, content_type: str = "image/jpeg") -> tuple[str, str]:
    """
    Encode image bytes to base64 and ensure size is within limits.

    Returns:
        Tuple of (base64_string, mime_type)
    """
    if content_type not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported image format: {content_type}. Supported: {SUPPORTED_FORMATS}")

    image = Image.open(io.BytesIO(image_bytes))

    # Convert RGBA/palette images to RGB for JPEG compatibility
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
        content_type = "image/jpeg"

    # Resize if larger than max dimensions while preserving aspect ratio
    if image.width > MAX_IMAGE_SIZE[0] or image.height > MAX_IMAGE_SIZE[1]:
        image.thumbnail(MAX_IMAGE_SIZE, Image.LANCZOS)

    buffer = io.BytesIO()
    fmt = "JPEG" if content_type == "image/jpeg" else content_type.split("/")[1].upper()
    image.save(buffer, format=fmt, quality=85)
    buffer.seek(0)

    encoded = base64.b64encode(buffer.read()).decode("utf-8")
    return encoded, content_type
