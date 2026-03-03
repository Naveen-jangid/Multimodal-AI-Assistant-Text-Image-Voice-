"""Speech-to-text using OpenAI Whisper API."""

import os
import tempfile
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """Transcribe audio bytes to text using Whisper."""
    with tempfile.NamedTemporaryFile(suffix=f"_{filename}", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
            )
        return transcription.strip()
    finally:
        os.unlink(tmp_path)
