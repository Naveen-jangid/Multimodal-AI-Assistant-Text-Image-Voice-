"""Multimodal AI Assistant — Beautiful Redesigned UI."""

import io
import requests
import streamlit as st
from audio_recorder_streamlit import audio_recorder

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multimodal AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BACKEND_URL = "http://localhost:8000"

# ── Session state ──────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "active_mode" not in st.session_state:
    st.session_state.active_mode = "text"
if "backend_url" not in st.session_state:
    st.session_state.backend_url = BACKEND_URL

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f !important;
    font-family: 'Inter', sans-serif !important;
    color: #e2e8f0 !important;
}

/* hide default Streamlit chrome */
#MainMenu, footer, header { display: none !important; }
[data-testid="stSidebar"] { background: #0f0f1a !important; border-right: 1px solid rgba(139,92,246,0.2); }
[data-testid="stSidebarContent"] { padding: 1.5rem 1rem; }
[data-testid="collapsedControl"] { color: #a78bfa !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #4c1d95; border-radius: 3px; }

/* ── App wrapper ── */
[data-testid="stAppViewContainer"] > .main { padding: 0 !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Hero header ── */
.hero-header {
    background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 40%, #1a0533 100%);
    border-bottom: 1px solid rgba(139,92,246,0.3);
    padding: 1.6rem 2.5rem 1.4rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -60px; left: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(139,92,246,0.25) 0%, transparent 70%);
    pointer-events: none;
}
.hero-header::after {
    content: '';
    position: absolute;
    bottom: -80px; right: 5%;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.hero-logo {
    font-size: 2.8rem;
    line-height: 1;
    filter: drop-shadow(0 0 12px rgba(139,92,246,0.7));
    animation: pulse-glow 3s ease-in-out infinite;
}
@keyframes pulse-glow {
    0%, 100% { filter: drop-shadow(0 0 8px rgba(139,92,246,0.6)); }
    50% { filter: drop-shadow(0 0 20px rgba(139,92,246,1)); }
}
.hero-text h1 {
    margin: 0;
    font-size: 1.7rem;
    font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
}
.hero-text p {
    margin: 0.25rem 0 0;
    font-size: 0.85rem;
    color: #94a3b8;
    letter-spacing: 0.01em;
}
.hero-badge {
    margin-left: auto;
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.badge {
    background: rgba(139,92,246,0.15);
    border: 1px solid rgba(139,92,246,0.4);
    border-radius: 999px;
    padding: 0.3rem 0.75rem;
    font-size: 0.7rem;
    font-weight: 600;
    color: #c4b5fd;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.badge.blue  { background: rgba(59,130,246,0.15); border-color: rgba(59,130,246,0.4); color: #93c5fd; }
.badge.green { background: rgba(52,211,153,0.15); border-color: rgba(52,211,153,0.4); color: #6ee7b7; }

/* ── Two-column layout ── */
.main-layout {
    display: grid;
    grid-template-columns: 280px 1fr;
    height: calc(100vh - 90px);
    overflow: hidden;
}

/* ── Left panel ── */
.left-panel {
    background: rgba(15,15,26,0.95);
    border-right: 1px solid rgba(139,92,246,0.15);
    padding: 1.5rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    overflow-y: auto;
}
.panel-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #64748b;
    padding: 0 0.5rem;
    margin-bottom: 0.25rem;
    margin-top: 0.75rem;
}

/* Mode cards */
.mode-card {
    display: flex;
    align-items: center;
    gap: 0.9rem;
    padding: 0.85rem 1rem;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid transparent;
    text-decoration: none;
    color: #94a3b8;
    background: transparent;
    margin-bottom: 0.25rem;
}
.mode-card:hover {
    background: rgba(139,92,246,0.08);
    border-color: rgba(139,92,246,0.2);
    color: #c4b5fd;
}
.mode-card.active {
    background: linear-gradient(135deg, rgba(139,92,246,0.2), rgba(59,130,246,0.1));
    border-color: rgba(139,92,246,0.5);
    color: #e2e8f0;
    box-shadow: 0 0 20px rgba(139,92,246,0.15), inset 0 1px 0 rgba(255,255,255,0.05);
}
.mode-icon {
    width: 38px; height: 38px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
    background: rgba(255,255,255,0.05);
    transition: all 0.2s;
}
.mode-card.active .mode-icon { background: linear-gradient(135deg, #7c3aed, #3b82f6); box-shadow: 0 4px 12px rgba(124,58,237,0.4); }
.mode-info strong { display: block; font-size: 0.875rem; font-weight: 600; }
.mode-info span { font-size: 0.72rem; color: #64748b; }
.mode-card.active .mode-info span { color: #94a3b8; }

/* Stats row */
.stats-row {
    display: flex;
    gap: 0.5rem;
    margin-top: auto;
    padding-top: 1rem;
    border-top: 1px solid rgba(139,92,246,0.1);
}
.stat-pill {
    flex: 1;
    background: rgba(139,92,246,0.08);
    border: 1px solid rgba(139,92,246,0.15);
    border-radius: 8px;
    padding: 0.5rem;
    text-align: center;
}
.stat-pill .num { font-size: 1.1rem; font-weight: 700; color: #a78bfa; }
.stat-pill .lbl { font-size: 0.6rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; }

/* ── Right panel ── */
.right-panel {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: #0d0d18;
}

/* Chat area */
.chat-area {
    flex: 1;
    overflow-y: auto;
    padding: 1.5rem 2rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

/* Empty state */
.empty-state {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    gap: 1rem;
    color: #475569;
    padding: 2rem;
}
.empty-state .glyph { font-size: 3.5rem; opacity: 0.4; }
.empty-state h3 { font-size: 1.1rem; font-weight: 600; color: #64748b; margin: 0; }
.empty-state p { font-size: 0.82rem; max-width: 320px; line-height: 1.6; margin: 0; }

/* capability cards in empty state */
.cap-grid { display: flex; gap: 0.75rem; flex-wrap: wrap; justify-content: center; margin-top: 0.5rem; }
.cap-card {
    background: rgba(139,92,246,0.07);
    border: 1px solid rgba(139,92,246,0.18);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    width: 140px;
    text-align: center;
}
.cap-card .cap-icon { font-size: 1.4rem; margin-bottom: 0.3rem; }
.cap-card .cap-title { font-size: 0.75rem; font-weight: 600; color: #a78bfa; }
.cap-card .cap-desc { font-size: 0.65rem; color: #64748b; margin-top: 0.2rem; line-height: 1.4; }

/* Chat bubbles */
.bubble-row {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
    animation: fadeUp 0.3s ease;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.bubble-row.user { flex-direction: row-reverse; }
.avatar {
    width: 34px; height: 34px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem;
    flex-shrink: 0;
    font-weight: 600;
}
.avatar.assistant { background: linear-gradient(135deg, #7c3aed, #3b82f6); box-shadow: 0 2px 10px rgba(124,58,237,0.4); }
.avatar.user { background: linear-gradient(135deg, #0f766e, #059669); box-shadow: 0 2px 10px rgba(15,118,110,0.4); }
.bubble {
    max-width: 70%;
    padding: 0.85rem 1.1rem;
    border-radius: 16px;
    font-size: 0.875rem;
    line-height: 1.65;
    position: relative;
}
.bubble.assistant {
    background: rgba(30,27,75,0.8);
    border: 1px solid rgba(139,92,246,0.2);
    border-top-left-radius: 4px;
    color: #e2e8f0;
}
.bubble.user {
    background: linear-gradient(135deg, rgba(15,118,110,0.3), rgba(5,150,105,0.2));
    border: 1px solid rgba(52,211,153,0.2);
    border-top-right-radius: 4px;
    color: #e2e8f0;
}
.bubble-meta { font-size: 0.65rem; color: #475569; margin-top: 0.4rem; }
.modality-tag {
    display: inline-flex; align-items: center; gap: 0.3rem;
    font-size: 0.65rem; font-weight: 600;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    margin-bottom: 0.4rem;
}
.modality-tag.image { background: rgba(59,130,246,0.15); color: #93c5fd; border: 1px solid rgba(59,130,246,0.3); }
.modality-tag.voice { background: rgba(239,68,68,0.12); color: #fca5a5; border: 1px solid rgba(239,68,68,0.25); }
.modality-tag.text  { background: rgba(139,92,246,0.12); color: #c4b5fd; border: 1px solid rgba(139,92,246,0.25); }

/* ── Input dock ── */
.input-dock {
    padding: 1rem 2rem 1.4rem;
    background: rgba(10,10,15,0.95);
    border-top: 1px solid rgba(139,92,246,0.12);
    backdrop-filter: blur(12px);
}
.dock-inner {
    background: rgba(20,20,35,0.9);
    border: 1px solid rgba(139,92,246,0.25);
    border-radius: 16px;
    padding: 0.85rem 1.1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    box-shadow: 0 0 30px rgba(139,92,246,0.08);
    transition: border-color 0.2s;
}
.dock-inner:focus-within {
    border-color: rgba(139,92,246,0.5);
    box-shadow: 0 0 30px rgba(139,92,246,0.15);
}

/* Streamlit form tweaks inside dock */
.input-dock .stTextArea textarea {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    resize: none !important;
    padding: 0 !important;
}
.input-dock .stTextArea textarea::placeholder { color: #475569 !important; }
.input-dock .stTextArea textarea:focus { box-shadow: none !important; }
[data-testid="stForm"] { border: none !important; padding: 0 !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 0.55rem 1.2rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(124,58,237,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(124,58,237,0.5) !important;
    background: linear-gradient(135deg, #8b5cf6, #6366f1) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Submit button in form */
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #7c3aed, #3b82f6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.2rem !important;
    box-shadow: 0 4px 14px rgba(124,58,237,0.35) !important;
    transition: all 0.2s !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(124,58,237,0.5) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploaderDropzone"] {
    background: rgba(139,92,246,0.05) !important;
    border: 2px dashed rgba(139,92,246,0.3) !important;
    border-radius: 12px !important;
    transition: all 0.2s !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: rgba(139,92,246,0.6) !important;
    background: rgba(139,92,246,0.1) !important;
}

/* ── Image preview ── */
[data-testid="stImage"] img {
    border-radius: 12px !important;
    border: 1px solid rgba(139,92,246,0.2) !important;
    box-shadow: 0 8px 30px rgba(0,0,0,0.5) !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 0.82rem !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] { color: #a78bfa !important; }

/* ── Text input ── */
.stTextInput > div > div > input {
    background: rgba(20,20,35,0.8) !important;
    border: 1px solid rgba(139,92,246,0.25) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-size: 0.82rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(139,92,246,0.6) !important;
    box-shadow: 0 0 0 2px rgba(139,92,246,0.15) !important;
}

/* ── Audio player ── */
audio {
    width: 100%;
    border-radius: 10px;
    filter: hue-rotate(230deg) saturate(0.6) brightness(0.85);
}

/* ── Sidebar tweaks ── */
[data-testid="stSidebar"] .stTextInput input {
    background: rgba(20,20,35,0.8) !important;
    border-color: rgba(139,92,246,0.2) !important;
    color: #e2e8f0 !important;
    font-size: 0.78rem !important;
}
[data-testid="stSidebar"] label { color: #94a3b8 !important; font-size: 0.75rem !important; }

/* ── Info box ── */
.info-box {
    background: rgba(59,130,246,0.08);
    border: 1px solid rgba(59,130,246,0.25);
    border-radius: 10px;
    padding: 0.7rem 1rem;
    font-size: 0.78rem;
    color: #93c5fd;
    display: flex; align-items: center; gap: 0.5rem;
}

/* ── Divider ── */
hr { border-color: rgba(139,92,246,0.15) !important; margin: 0.5rem 0 !important; }

/* ── Markdown in bubbles ── */
.bubble p { margin: 0 0 0.5rem; }
.bubble p:last-child { margin-bottom: 0; }
.bubble ul, .bubble ol { padding-left: 1.2rem; margin: 0.3rem 0; }
.bubble code {
    background: rgba(139,92,246,0.15);
    border-radius: 4px;
    padding: 0.1rem 0.4rem;
    font-size: 0.8rem;
    color: #c4b5fd;
}
.bubble pre {
    background: rgba(0,0,0,0.4);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 8px;
    padding: 0.75rem;
    overflow-x: auto;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)


# ── Hero Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <div class="hero-logo">🤖</div>
    <div class="hero-text">
        <h1>Multimodal AI Assistant</h1>
        <p>Chat · Analyze images · Speak naturally — all in one place</p>
    </div>
    <div class="hero-badge">
        <span class="badge">GPT-4o</span>
        <span class="badge blue">Whisper</span>
        <span class="badge green">FastAPI</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def add_message(role: str, content: str, modality: str = "text"):
    st.session_state.chat_history.append({"role": role, "content": content, "modality": modality})


def show_error(detail: str):
    st.error(f"**Error:** {detail}")


def count_by_role(role):
    return sum(1 for m in st.session_state.chat_history if m["role"] == role)


# ── Layout ─────────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 3.5], gap="small")

# ═══════════════════════════════════════════════════════════════════
# LEFT PANEL — mode selector + stats
# ═══════════════════════════════════════════════════════════════════
with left_col:
    st.markdown('<div class="panel-label">Input Mode</div>', unsafe_allow_html=True)

    modes = [
        ("text",  "💬", "Text Chat",    "Conversational Q&A"),
        ("image", "📷", "Image Vision", "Upload & analyze"),
        ("voice", "🎤", "Voice Input",  "Speak your question"),
    ]
    for key, icon, title, desc in modes:
        active = "active" if st.session_state.active_mode == key else ""
        if st.button(
            f"{icon}  {title}",
            key=f"mode_{key}",
            use_container_width=True,
            help=desc,
        ):
            st.session_state.active_mode = key
            st.rerun()

    st.markdown('<div class="panel-label" style="margin-top:1.5rem">Session</div>', unsafe_allow_html=True)
    total_msgs = len(st.session_state.chat_history)
    user_msgs  = count_by_role("user")
    ai_msgs    = count_by_role("assistant")

    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-pill"><div class="num">{total_msgs}</div><div class="lbl">Total</div></div>
        <div class="stat-pill"><div class="num">{user_msgs}</div><div class="lbl">You</div></div>
        <div class="stat-pill"><div class="num">{ai_msgs}</div><div class="lbl">AI</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    if st.button("🗑️ Clear history", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown('<div class="panel-label" style="margin-top:1.5rem">Backend URL</div>', unsafe_allow_html=True)
    backend_url = st.text_input("", value=st.session_state.backend_url, label_visibility="collapsed")
    st.session_state.backend_url = backend_url

    st.markdown('<div class="panel-label" style="margin-top:1.5rem">Powered by</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.72rem; color:#64748b; line-height:2; padding:0 0.25rem;">
        🧠 &nbsp;GPT-4o · Text + Vision<br>
        🎙️ &nbsp;Whisper · Speech-to-text<br>
        ⚡ &nbsp;FastAPI · Python backend<br>
        🎨 &nbsp;Streamlit · Frontend
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# RIGHT PANEL — chat history + input dock
# ═══════════════════════════════════════════════════════════════════
with right_col:
    mode = st.session_state.active_mode

    # ── Chat history ──────────────────────────────────────────────
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="empty-state">
            <div class="glyph">✨</div>
            <h3>Start a conversation</h3>
            <p>Choose an input mode on the left and start chatting, upload an image, or record your voice.</p>
            <div class="cap-grid">
                <div class="cap-card">
                    <div class="cap-icon">💬</div>
                    <div class="cap-title">Text Chat</div>
                    <div class="cap-desc">Ask anything, hold multi-turn conversations</div>
                </div>
                <div class="cap-card">
                    <div class="cap-icon">📷</div>
                    <div class="cap-title">Vision</div>
                    <div class="cap-desc">Upload food, photos — get instant analysis</div>
                </div>
                <div class="cap-card">
                    <div class="cap-icon">🎤</div>
                    <div class="cap-title">Voice</div>
                    <div class="cap-desc">Record a question, get a spoken-style answer</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        modality_icons = {"text": "💬", "image": "📷", "voice": "🎤"}
        for msg in st.session_state.chat_history:
            role     = msg["role"]
            content  = msg["content"]
            modality = msg.get("modality", "text")
            tag_html = ""
            if modality != "text":
                tag_html = f'<span class="modality-tag {modality}">{modality_icons[modality]} {modality.capitalize()}</span><br>'
            avatar_char = "AI" if role == "assistant" else "You"
            with st.chat_message(role):
                if modality != "text":
                    st.markdown(f'<span class="modality-tag {modality}">{modality_icons[modality]} {modality.capitalize()}</span>', unsafe_allow_html=True)
                st.markdown(content)

    st.divider()

    # ═══════════════════════════════════════════════════════════════
    # INPUT DOCK
    # ═══════════════════════════════════════════════════════════════

    # ── TEXT MODE ──────────────────────────────────────────────────
    if mode == "text":
        with st.form("text_form", clear_on_submit=True):
            user_input = st.text_area(
                "Message",
                placeholder="Ask me anything… (Shift+Enter for new line)",
                height=90,
                label_visibility="collapsed",
            )
            col_a, col_b = st.columns([5, 1])
            with col_b:
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
                        add_message("assistant", resp.json()["response"], modality="text")
                    else:
                        show_error(resp.json().get("detail", resp.text))
                except requests.ConnectionError:
                    show_error(f"Cannot reach backend at `{backend_url}`. Is it running?")
            st.rerun()

    # ── IMAGE MODE ─────────────────────────────────────────────────
    elif mode == "image":
        uploaded_file = st.file_uploader(
            "Drop an image here or click to browse",
            type=["jpg", "jpeg", "png", "webp", "gif"],
            label_visibility="visible",
        )
        if uploaded_file:
            col_prev, col_form = st.columns([1, 2])
            with col_prev:
                st.image(uploaded_file, use_container_width=True)
            with col_form:
                with st.form("image_form", clear_on_submit=True):
                    image_prompt = st.text_input(
                        "Question (optional)",
                        placeholder="e.g. What is the calorie count of this meal?",
                    )
                    analyze_btn = st.form_submit_button("🔍 Analyze Image", use_container_width=True)

            if analyze_btn:
                add_message("user", f"📷 _{uploaded_file.name}_ — {image_prompt or 'Analyze this image.'}", modality="image")
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
                            add_message("assistant", resp.json()["response"], modality="image")
                        else:
                            show_error(resp.json().get("detail", resp.text))
                    except requests.ConnectionError:
                        show_error(f"Cannot reach backend at `{backend_url}`. Is it running?")
                st.rerun()

    # ── VOICE MODE ─────────────────────────────────────────────────
    elif mode == "voice":
        st.markdown("""
        <div class="info-box">
            🎙️ &nbsp; Click the microphone button to start recording — click again to stop.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")

        col_mic, col_ctrl = st.columns([1, 3])
        with col_mic:
            audio_bytes = audio_recorder(
                text="",
                recording_color="#ef4444",
                neutral_color="#7c3aed",
                icon_size="2x",
            )
        with col_ctrl:
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")
                if st.button("🚀 Transcribe & Answer", use_container_width=True):
                    with st.spinner("Transcribing audio and generating answer…"):
                        try:
                            resp = requests.post(
                                f"{backend_url}/voice/transcribe-and-answer",
                                files={"file": ("recording.wav", io.BytesIO(audio_bytes), "audio/wav")},
                                data={"context": ""},
                                timeout=90,
                            )
                            if resp.ok:
                                data = resp.json()
                                add_message("user", f'🎤 *"{data["transcription"]}"*', modality="voice")
                                add_message("assistant", data["response"], modality="voice")
                            else:
                                show_error(resp.json().get("detail", resp.text))
                        except requests.ConnectionError:
                            show_error(f"Cannot reach backend at `{backend_url}`. Is it running?")
                    st.rerun()
            else:
                st.markdown('<p style="color:#475569; font-size:0.82rem; margin-top:0.5rem;">No recording yet — press the purple mic button to start.</p>', unsafe_allow_html=True)
