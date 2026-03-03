"""Text input route."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.models.llm import get_text_response
from backend.utils.prompt import enrich_prompt

router = APIRouter(prefix="/text", tags=["text"])


class TextRequest(BaseModel):
    message: str
    conversation_history: list = []


class TextResponse(BaseModel):
    response: str
    modality: str = "text"


@router.post("/chat", response_model=TextResponse)
async def chat(request: TextRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    enriched = enrich_prompt(request.message, modality="text")
    reply = get_text_response(enriched, request.conversation_history)
    return TextResponse(response=reply)
