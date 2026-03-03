"""Multimodal AI Assistant – FastAPI entry point."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from backend.routes import text, image, voice

load_dotenv()

app = FastAPI(
    title="Multimodal AI Assistant",
    description="An AI assistant that accepts text, image, and voice input powered by GPT-4o and Whisper.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(text.router)
app.include_router(image.router)
app.include_router(voice.router)


@app.get("/", tags=["health"])
async def root():
    return {
        "status": "ok",
        "message": "Multimodal AI Assistant is running.",
        "endpoints": {
            "text": "/text/chat",
            "image": "/image/analyze",
            "voice": "/voice/transcribe-and-answer",
            "docs": "/docs",
        },
    }


@app.get("/health", tags=["health"])
async def health():
    api_key_set = bool(os.getenv("OPENAI_API_KEY"))
    return {"status": "ok", "openai_api_key_configured": api_key_set}
