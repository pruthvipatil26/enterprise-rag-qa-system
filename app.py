# ============================================================
# FILE: app.py  —  Enterprise RAG  |  Aesthetic Overhaul v3
# ============================================================

import os
import tempfile
import streamlit as st

# ── Must be FIRST st.* call ────────────────────────────────
st.set_page_config(
    page_title="Enterprise Knowledge Base",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

from bedrock_rag import query_knowledge_base, upload_document_to_s3
from config import APP_TITLE, APP_ICON, S3_BUCKET_NAME


# ══════════════════════════════════════════════════════════
#  CSS  —  Cyan Glassmorphism / Dark Command Aesthetic
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Tokens ─────────────────────────────────────────────── */
:root {
  --base:        #04080f;
  --surface-1:   #080f1e;
  --surface-2:   #0c1529;
  --surface-3:   #101c34;
  --glass:       rgba(12, 21, 41, 0.7);
  --cyan:        #22d3ee;
  --cyan-dim:    #0891b2;
  --cyan-glow:   rgba(34,211,238,0.12);
  --cyan-glow2:  rgba(34,211,238,0.06);
  --cyan-border: rgba(34,211,238,0.25);
  --orange:      #f97316;
  --orange-dim:  rgba(249,115,22,0.15);
  --text-1:      #f0f6ff;
  --text-2:      #94a3b8;
  --text-3:      #475569;
  --success:     #10b981;
  --error:       #f43f5e;
  --warning:     #fbbf24;
  --radius-sm:   6px;
  --radius-md:   10px;
  --radius-lg:   16px;
  --radius-xl:   22px;
}

/* ── Full app reset ───────────────────────────────────────── */
html, body, .stApp {
  background: var(--base) !important;
  font-family: 'Space Grotesk', sans-serif !important;
  color: var(--text-1) !important;
}

/* Ambient radial glow behind content */
.stApp::after {
  content: '';
  position: fixed;
  top: -20%;
  left: 50%;
  transform: translateX(-50%);
  width: 80vw;
  height: 60vh;
  background: radial-gradient(ellipse, rgba(34,211,238,0.07) 0%, transparent 70%);
  pointer-events: none;
  z-index: 0;
}

/* Hide Streamlit default top bar chrome */
header[data-testid="stHeader"] {
  background: transparent !important;
  border-bottom: none !important;
}
#MainMenu, footer, header { visibility: hidden !important; }

/* ── Main container ───────────────────────────────────────── */
.main .block-container {
  padding: 3rem 3.5rem 6rem !important;
  max-width: 940px !important;
  position: relative;
  z-index: 1;
}

/* ── Typography ───────────────────────────────────────────── */
h1 {
  font-family: 'Space Grotesk', sans-serif !important;
  font-size: 2.4rem !important;
  font-weight: 700 !important;
  letter-spacing: -0.03em !important;
  color: var(--text-1) !important;
  line-height: 1.15 !important;
  margin-bottom: 0.4rem !important;
}

h2, h3 {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.72rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  color: var(--cyan) !important;
}

p, div, span, li {
  font-family: 'Space Grotesk', sans-serif !important;
}

/* ── Sidebar ──────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
  background: var(--surface-1) !important;
  border-right: 1px solid var(--cyan-border) !important;
  box-shadow: 4px 0 40px rgba(34,211,238,0.04) !important;
}
section[data-testid="stSidebar"] > div {
  padding: 2rem 1.75rem !important;
}

/* Sidebar brand header */
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 1.5rem;
}
.sidebar-brand-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--cyan);
  box-shadow: 0 0 10px var(--cyan);
  animation: breathe 3s ease-in-out infinite;
}
@keyframes breathe {
  0%,100% { opacity:1; box-shadow: 0 0 10px var(--cyan); }
  50%      { opacity:0.5; box-shadow: 0 0 4px var(--cyan); }
}
.sidebar-brand-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--cyan);
}

/* ── Divider ──────────────────────────────────────────────── */
hr {
  border: none !important;
  border-top: 1px solid rgba(34,211,238,0.1) !important;
  margin: 1.25rem 0 !important;
}

/* ── Info/alert boxes ─────────────────────────────────────── */
div[data-testid="stAlert"] {
  background: var(--surface-3) !important;
  border: 1px solid var(--cyan-border) !important;
  border-radius: var(--radius-md) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.75rem !important;
  color: var(--text-2) !important;
}

/* ── File uploader ────────────────────────────────────────── */
div[data-testid="stFileUploader"] {
  background: var(--surface-2) !important;
  border: 1px dashed rgba(34,211,238,0.3) !important;
  border-radius: var(--radius-md) !important;
  padding: 0.8rem !important;
  transition: all 0.25s ease;
}
div[data-testid="stFileUploader"]:hover {
  border-color: var(--cyan) !important;
  background: var(--cyan-glow2) !important;
}
div[data-testid="stFileUploader"] * {
  color: var(--text-2) !important;
  font-size: 0.8rem !important;
}

/* ── Buttons ──────────────────────────────────────────────── */
div.stButton > button {
  width: 100% !important;
  background: transparent !important;
  color: var(--cyan) !important;
  border: 1px solid var(--cyan-border) !important;
  border-radius: var(--radius-sm) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.75rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.08em !important;
  padding: 0.55rem 1rem !important;
  transition: all 0.2s ease !important;
  text-transform: uppercase !important;
}
div.stButton > button:hover {
  background: var(--cyan-glow) !important;
  border-color: var(--cyan) !important;
  box-shadow: 0 0 20px var(--cyan-glow) !important;
  transform: translateY(-1px) !important;
}
div.stButton > button:active {
  transform: translateY(0) !important;
}

/* ── Chat messages ────────────────────────────────────────── */
div[data-testid="stChatMessage"] {
  background: var(--glass) !important;
  backdrop-filter: blur(12px) !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  border-radius: var(--radius-lg) !important;
  padding: 1.4rem 1.6rem !important;
  margin-bottom: 1rem !important;
  position: relative;
  overflow: hidden;
  transition: border-color 0.2s ease;
}
div[data-testid="stChatMessage"]:hover {
  border-color: rgba(34,211,238,0.15) !important;
}

/* Cyan top-stripe on assistant */
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--cyan), transparent 60%);
}

/* Orange top-stripe on user */
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--orange), transparent 60%);
}

/* Avatar */
div[data-testid="chatAvatarIcon-assistant"],
div[data-testid="chatAvatarIcon-user"] {
  background: var(--surface-3) !important;
  border: 1px solid var(--cyan-border) !important;
  border-radius: var(--radius-sm) !important;
}

/* Message text */
div[data-testid="stChatMessage"] p {
  color: var(--text-1) !important;
  font-size: 0.925rem !important;
  line-height: 1.8 !important;
  font-weight: 300 !important;
}
div[data-testid="stChatMessage"] strong {
  color: var(--text-1) !important;
  font-weight: 600 !important;
}
div[data-testid="stChatMessage"] code {
  background: rgba(34,211,238,0.08) !important;
  color: var(--cyan) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.8rem !important;
  border-radius: 4px !important;
  padding: 0.15em 0.5em !important;
  border: 1px solid rgba(34,211,238,0.15) !important;
}
div[data-testid="stChatMessage"] blockquote {
  border-left: 2px solid var(--cyan) !important;
  color: var(--text-2) !important;
  padding-left: 1rem !important;
  margin: 0.5rem 0 0.5rem 0 !important;
  font-style: italic !important;
}

/* ── Chat input ───────────────────────────────────────────── */
div[data-testid="stChatInput"] {
  background: var(--surface-2) !important;
  border: 1px solid var(--cyan-border) !important;
  border-radius: var(--radius-xl) !important;
  transition: all 0.25s ease;
}
div[data-testid="stChatInput"]:focus-within {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 4px rgba(34,211,238,0.08), 0 0 32px rgba(34,211,238,0.1) !important;
}
div[data-testid="stChatInput"] textarea {
  background: transparent !important;
  color: var(--text-1) !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-size: 0.9rem !important;
  font-weight: 300 !important;
  caret-color: var(--cyan) !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
  color: var(--text-3) !important;
}
div[data-testid="stChatInput"] button {
  color: var(--cyan) !important;
}

/* ── Expander ─────────────────────────────────────────────── */
details {
  background: var(--surface-2) !important;
  border: 1px solid rgba(34,211,238,0.12) !important;
  border-radius: var(--radius-md) !important;
  margin-top: 1rem !important;
  overflow: hidden;
  transition: border-color 0.2s ease;
}
details:hover { border-color: var(--cyan-border) !important; }
details[open] { border-color: var(--cyan-border) !important; }
details summary {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.75rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.06em !important;
  color: var(--cyan) !important;
  padding: 0.85rem 1.1rem !important;
  cursor: pointer;
  text-transform: uppercase;
}
details summary:hover { background: var(--cyan-glow2) !important; }

/* ── Spinner ──────────────────────────────────────────────── */
div[data-testid="stSpinner"] { color: var(--cyan) !important; }
div[data-testid="stSpinner"] svg { stroke: var(--cyan) !important; }

/* ── Scrollbar ────────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--base); }
::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--cyan-dim); }

/* ── Sidebar text ─────────────────────────────────────────── */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] ol li,
section[data-testid="stSidebar"] ul li {
  color: var(--text-2) !important;
  font-size: 0.82rem !important;
  line-height: 1.65 !important;
}

/* ── Custom component classes ─────────────────────────────── */

/* Metric strip card */
.stat-card {
  background: var(--surface-2);
  border: 1px solid rgba(34,211,238,0.12);
  border-radius: var(--radius-md);
  padding: 0.9rem 1.1rem;
  text-align: center;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.stat-card:hover {
  border-color: var(--cyan-border);
  box-shadow: 0 0 20px var(--cyan-glow2);
}
.stat-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-3);
  margin-bottom: 4px;
}
.stat-value {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: var(--cyan);
  letter-spacing: -0.01em;
}

/* Badge pill */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: rgba(34,211,238,0.07);
  border: 1px solid rgba(34,211,238,0.2);
  border-radius: 99px;
  padding: 5px 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 0.04em;
  color: var(--cyan);
}
.badge-dot {
  width: 5px; height: 5px;
  border-radius: 50%;
  background: var(--success);
  box-shadow: 0 0 6px var(--success);
  animation: breathe 3s ease-in-out infinite;
}

/* Citation row */
.cite-header {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--cyan);
  margin-bottom: 4px;
  padding: 0.6rem 0.8rem;
  background: rgba(34,211,238,0.05);
  border-radius: 6px;
  border-left: 2px solid var(--cyan);
}

/* Title accent line */
.title-accent {
  width: 40px; height: 2px;
  background: linear-gradient(90deg, var(--cyan), transparent);
  border-radius: 2px;
  margin: 8px 0 20px 0;
}

/* Section divider with label */
.section-tag {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 1.5rem 0 0.75rem;
}
.section-tag-line {
  flex: 1;
  height: 1px;
  background: rgba(34,211,238,0.1);
}
.section-tag-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-3);
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════
with st.sidebar:

    # Brand
    st.markdown("""
    <div class="sidebar-brand">
      <div class="sidebar-brand-dot"></div>
      <div class="sidebar-brand-text">RAG System</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="badge"><span class="badge-dot"></span>Knowledge Base Live</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Knowledge Base ──
    st.markdown("""<div class="section-tag">
      <div class="section-tag-line"></div>
      <div class="section-tag-text">Knowledge Base</div>
      <div class="section-tag-line"></div>
    </div>""", unsafe_allow_html=True)

    st.info(f"Bucket: `{S3_BUCKET_NAME}`")

    # ── Upload ──
    st.markdown("""<div class="section-tag">
      <div class="section-tag-line"></div>
      <div class="section-tag-text">Upload Docs</div>
      <div class="section-tag-line"></div>
    </div>""", unsafe_allow_html=True)

    st.write("Add documents to the knowledge base.")

    uploaded_file = st.file_uploader(
        label="Choose a file",
        type=["pdf", "txt", "docx"],
        help="PDF, TXT or DOCX"
    )

    if uploaded_file is not None:
        if st.button("⬆  Upload to S3"):
            with st.spinner("Uploading..."):
                temp_path = os.path.join(tempfile.gettempdir(), uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                success = upload_document_to_s3(temp_path, uploaded_file.name)
                if success:
                    st.success("Done! Sync your Bedrock KB.")
                else:
                    st.error("Upload failed — check logs.")

    # ── How to use ──
    st.markdown("""<div class="section-tag">
      <div class="section-tag-line"></div>
      <div class="section-tag-text">How to use</div>
      <div class="section-tag-line"></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    1. Type your question below
    2. Press **Enter** to submit
    3. Read the AI-generated answer
    4. Expand **Sources** for citations
    """)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("↺  Clear History"):
        st.session_state.messages = []
        st.rerun()


# ══════════════════════════════════════════════════════════
#  MAIN HEADER
# ══════════════════════════════════════════════════════════
st.markdown(f"""
<div style="margin-bottom: 0.25rem;">
  <div style="font-size:0.7rem;font-family:'JetBrains Mono',monospace;
              letter-spacing:0.14em;text-transform:uppercase;
              color:var(--text-3);margin-bottom:0.5rem;">
    ◈ Enterprise Intelligence
  </div>
  <h1>{APP_ICON} {APP_TITLE}</h1>
  <div class="title-accent"></div>
  <p style="color:var(--text-2);font-size:0.88rem;font-weight:300;margin:0;">
    Ask questions about company documents — accurate, cited answers via Amazon Bedrock RAG.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Stat strip ──
msg_count = len([m for m in st.session_state.get("messages", []) if m["role"] == "user"])

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        '<div class="stat-card"><div class="stat-label">Engine</div>'
        '<div class="stat-value">Amazon Bedrock</div></div>',
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        '<div class="stat-card"><div class="stat-label">Method</div>'
        '<div class="stat-value">RAG Pipeline</div></div>',
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        f'<div class="stat-card"><div class="stat-label">Queries</div>'
        f'<div class="stat-value">{msg_count} this session</div></div>',
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = []


# ══════════════════════════════════════════════════════════
#  CHAT HISTORY
# ══════════════════════════════════════════════════════════
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ══════════════════════════════════════════════════════════
#  CHAT INPUT
# ══════════════════════════════════════════════════════════
if question := st.chat_input("Ask anything about your company documents…"):

    with st.chat_message("user"):
        st.markdown(question)

    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base…"):
            result = query_knowledge_base(question)

        if result["success"]:
            st.markdown(result["answer"])

            if result["citations"]:
                with st.expander(f"◎  Sources  —  {len(result['citations'])} document(s) referenced"):
                    for i, citation in enumerate(result["citations"], start=1):
                        file_name = citation["source"].split("/")[-1]
                        st.markdown(
                            f'<div class="cite-header">Source {i} &nbsp;/&nbsp; {file_name}</div>',
                            unsafe_allow_html=True
                        )
                        st.markdown(f"> {citation['excerpt']}")
                        if i < len(result["citations"]):
                            st.divider()
            else:
                st.warning("No citations found for this answer.")
        else:
            st.error(f"Error: {result['answer']}")

    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})