"""Streamlit UI for the Multimodal AI Assistant."""

import io
import requests
import streamlit as st
from audio_recorder_streamlit import audio_recorder

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multimodal AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Constants ──────────────────────────────────────────────────────────────────
BACKEND_URL = "http://localhost:8000"

# ── Session state ──────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of {"role": str, "content": str, "modality": str}

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")
    backend_url = st.text_input("Backend URL", value=BACKEND_URL)

    st.markdown("---")
    st.markdown("### Input Mode")
    mode = st.radio(
        "Choose input type:",
        ["💬 Text", "📷 Image", "🎤 Voice"],
        index=0,
    )

    st.markdown("---")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("---")
    st.markdown(
        "**Multimodal AI Assistant**\n\n"
        "Powered by:\n"
        "- 🧠 GPT-4o (text + vision)\n"
        "- 🎙️ Whisper (speech-to-text)\n"
        "- ⚡ FastAPI backend\n"
    )

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🤖 Multimodal AI Assistant")
st.caption("Ask anything via text, upload an image for analysis, or record your voice.")

# ── Chat history display ────────────────────────────────────────────────────────
chat_container = st.container()
with chat_container:
    for msg in st.session_state.chat_history:
        role = msg["role"]
        content = msg["content"]
        modality = msg.get("modality", "text")

        icon_map = {"text": "💬", "image": "📷", "voice": "🎤"}
        with st.chat_message(role):
            if role == "user" and modality in ("image",):
                st.caption(f"{icon_map[modality]} Image uploaded")
            elif role == "user" and modality == "voice":
                st.caption(f"🎤 Voice transcription")
            st.markdown(content)


# ── Helper ─────────────────────────────────────────────────────────────────────
def add_message(role: str, content: str, modality: str = "text"):
    st.session_state.chat_history.append({"role": role, "content": content, "modality": modality})


def show_error(detail: str):
    st.error(f"❌ {detail}")


# ── Input area ─────────────────────────────────────────────────────────────────
st.divider()

# ── TEXT MODE ──────────────────────────────────────────────────────────────────
if mode == "💬 Text":
    with st.form("text_form", clear_on_submit=True):
        user_input = st.text_area(
            "Your message",
            placeholder="Ask me anything…",
            height=100,
        )
        submitted = st.form_submit_button("Send ➤", use_container_width=True)

    if submitted and user_input.strip():
        add_message("user", user_input, modality="text")
        with st.spinner("Thinking…"):
            try:
                resp = requests.post(
                    f"{backend_url}/text/chat",
                    json={
                        "message": user_input,
                        "conversation_history": [
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.chat_history[:-1]
                            if m["modality"] == "text"
                        ],
                    },
                    timeout=60,
                )
                if resp.ok:
                    answer = resp.json()["response"]
                    add_message("assistant", answer, modality="text")
                else:
                    show_error(resp.json().get("detail", resp.text))
            except requests.ConnectionError:
                show_error(f"Cannot reach backend at {backend_url}. Is it running?")
        st.rerun()

# ── IMAGE MODE ─────────────────────────────────────────────────────────────────
elif mode == "📷 Image":
    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png", "webp", "gif"],
        help="Supported: JPG, PNG, WebP, GIF",
    )

    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded image", use_container_width=True)

    with st.form("image_form", clear_on_submit=True):
        image_prompt = st.text_input(
            "Optional question about the image",
            placeholder="e.g. What is the nutritional value of this meal?",
        )
        analyze_btn = st.form_submit_button("Analyze Image 🔍", use_container_width=True)

    if analyze_btn:
        if not uploaded_file:
            st.warning("Please upload an image first.")
        else:
            add_message("user", f"[Image uploaded] {image_prompt or 'Analyze this image.'}", modality="image")
            with st.spinner("Analyzing image…"):
                try:
                    uploaded_file.seek(0)
                    resp = requests.post(
                        f"{backend_url}/image/analyze",
                        files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)},
                        data={"message": image_prompt},
                        timeout=90,
                    )
                    if resp.ok:
                        answer = resp.json()["response"]
                        add_message("assistant", answer, modality="image")
                    else:
                        show_error(resp.json().get("detail", resp.text))
                except requests.ConnectionError:
                    show_error(f"Cannot reach backend at {backend_url}. Is it running?")
            st.rerun()

# ── VOICE MODE ─────────────────────────────────────────────────────────────────
elif mode == "🎤 Voice":
    st.info("Click the microphone to record your question, then click again to stop.")

    audio_bytes = audio_recorder(
        text="",
        recording_color="#e87070",
        neutral_color="#6aa36f",
        icon_size="2x",
    )

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        if st.button("🚀 Send Voice Message", use_container_width=True):
            with st.spinner("Transcribing and answering…"):
                try:
                    resp = requests.post(
                        f"{backend_url}/voice/transcribe-and-answer",
                        files={"file": ("recording.wav", io.BytesIO(audio_bytes), "audio/wav")},
                        data={"context": ""},
                        timeout=90,
                    )
                    if resp.ok:
                        data = resp.json()
                        transcription = data["transcription"]
                        answer = data["response"]
                        add_message("user", f"🎤 _{transcription}_", modality="voice")
                        add_message("assistant", answer, modality="voice")
                    else:
                        show_error(resp.json().get("detail", resp.text))
                except requests.ConnectionError:
                    show_error(f"Cannot reach backend at {backend_url}. Is it running?")
            st.rerun()
