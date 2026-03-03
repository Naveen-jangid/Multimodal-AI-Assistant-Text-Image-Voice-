# Multimodal AI Assistant – Text · Image · Voice

A smart AI assistant that accepts **text**, **voice**, and **image** inputs and responds intelligently using GPT-4o and Whisper. Similar to ChatGPT + Vision + Voice in a single app.

---

## Features

| Modality | What you can do | Under the hood |
|---|---|---|
| **Text** | Ask any question, hold a conversation | GPT-4o |
| **Image** | Upload food/photo → get analysis & nutrition info | GPT-4o Vision |
| **Voice** | Record a question → get transcription + answer | Whisper + GPT-4o |

---

## Architecture

```
┌─────────────────────────────┐
│   Streamlit Frontend (UI)   │  ← port 8501
└────────────┬────────────────┘
             │ REST API
┌────────────▼────────────────┐
│   FastAPI Backend           │  ← port 8000
│  ├── /text/chat             │
│  ├── /image/analyze         │
│  └── /voice/transcribe...   │
└────────────┬────────────────┘
             │
┌────────────▼────────────────┐
│   OpenAI APIs               │
│  ├── GPT-4o  (text+vision)  │
│  └── Whisper (speech→text)  │
└─────────────────────────────┘
```

## Project Structure

```
Multimodal-AI-Assistant/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── models/
│   │   ├── llm.py           # GPT-4o text & vision calls
│   │   ├── speech.py        # Whisper transcription
│   │   └── vision.py        # Image pre-processing
│   ├── routes/
│   │   ├── text.py          # POST /text/chat
│   │   ├── image.py         # POST /image/analyze
│   │   └── voice.py         # POST /voice/transcribe-and-answer
│   └── utils/
│       └── prompt.py        # Prompt engineering helpers
├── frontend/
│   └── app.py               # Streamlit UI
├── requirements.txt
├── .env.example
└── README.md
```

---

## Quick Start

### 1. Clone & install dependencies

```bash
git clone <repo-url>
cd Multimodal-AI-Assistant-Text-Image-Voice-
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set up your API key

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-...
```

You can get an API key at [platform.openai.com](https://platform.openai.com/api-keys).

### 3. Start the backend

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` to explore the interactive API docs.

### 4. Start the frontend (in a separate terminal)

```bash
streamlit run frontend/app.py
```

Open `http://localhost:8501` in your browser.

---

## API Endpoints

### `POST /text/chat`
Send a text message and get a response.

```json
{
  "message": "What is the capital of France?",
  "conversation_history": []
}
```

### `POST /image/analyze`
Upload an image (multipart/form-data) with an optional question.

```
file=<image file>
message="What are the calories in this meal?"
```

### `POST /voice/transcribe-and-answer`
Upload an audio file. Returns transcription + AI answer.

```
file=<audio file (.wav/.mp3/.webm)>
context=""
```

---

## Example Use Cases

- **Food nutrition analysis**: Upload a plate photo → get estimated calories, macros, vitamins
- **Voice Q&A**: Record a question → get transcription + detailed answer
- **Conversational chat**: Multi-turn text conversations with context
- **Image description**: Upload any photo → get a detailed description

---

## Technologies

| Layer | Technology |
|---|---|
| LLM (text + vision) | OpenAI GPT-4o |
| Speech-to-text | OpenAI Whisper |
| Backend | Python 3.11 + FastAPI |
| Frontend | Streamlit |
| Image processing | Pillow |

---

## Skills Learned

- **Multimodal AI** – combining text, vision, and audio in one pipeline
- **Prompt engineering** – crafting effective prompts for different modalities
- **LLM pipelines** – chaining transcription → reasoning → response
- **API integration** – OpenAI SDK, FastAPI REST, Streamlit UI
- **File handling** – audio and image upload, validation, processing
