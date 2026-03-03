"""Voice (speech-to-text + LLM) route."""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from backend.models.speech import transcribe_audio
from backend.models.llm import get_text_response
from backend.utils.prompt import enrich_prompt

router = APIRouter(prefix="/voice", tags=["voice"])

SUPPORTED_AUDIO = {
    "audio/wav", "audio/wave", "audio/x-wav",
    "audio/mpeg", "audio/mp3",
    "audio/ogg", "audio/webm",
    "audio/flac", "audio/mp4",
}


class VoiceResponse(BaseModel):
    transcription: str
    response: str
    modality: str = "voice"


@router.post("/transcribe-and-answer", response_model=VoiceResponse)
async def transcribe_and_answer(
    file: UploadFile = File(...),
    context: str = Form(default=""),
):
    content_type = (file.content_type or "audio/wav").split(";")[0].strip()
    if content_type not in SUPPORTED_AUDIO:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported audio type '{content_type}'. Accepted: {sorted(SUPPORTED_AUDIO)}",
        )

    audio_bytes = await file.read()
    if len(audio_bytes) > 25 * 1024 * 1024:  # 25 MB Whisper limit
        raise HTTPException(status_code=413, detail="Audio file too large. Max 25 MB.")

    transcription = transcribe_audio(audio_bytes, filename=file.filename or "audio.wav")
    if not transcription:
        raise HTTPException(status_code=422, detail="Could not transcribe audio. Please try again.")

    enriched = enrich_prompt(transcription, modality="voice")
    conversation_history = [{"role": "user", "content": context}] if context else []
    reply = get_text_response(enriched, conversation_history)

    return VoiceResponse(transcription=transcription, response=reply)
