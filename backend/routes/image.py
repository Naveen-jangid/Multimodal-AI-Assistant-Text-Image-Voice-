"""Image analysis route."""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from backend.models.llm import get_vision_response
from backend.models.vision import encode_image, SUPPORTED_FORMATS
from backend.utils.prompt import enrich_prompt

router = APIRouter(prefix="/image", tags=["image"])


class ImageResponse(BaseModel):
    response: str
    modality: str = "image"
    transcribed_text: str = ""


@router.post("/analyze", response_model=ImageResponse)
async def analyze_image(
    file: UploadFile = File(...),
    message: str = Form(default=""),
):
    content_type = file.content_type or "image/jpeg"
    if content_type not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{content_type}'. Accepted: {sorted(SUPPORTED_FORMATS)}",
        )

    image_bytes = await file.read()
    if len(image_bytes) > 20 * 1024 * 1024:  # 20 MB guard
        raise HTTPException(status_code=413, detail="Image file too large. Max 20 MB.")

    try:
        image_b64, mime = encode_image(image_bytes, content_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    enriched_prompt = enrich_prompt(message, modality="image")
    reply = get_vision_response(enriched_prompt, image_b64, mime)
    return ImageResponse(response=reply)
