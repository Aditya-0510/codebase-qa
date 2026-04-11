import streamlit as st
import os
import subprocess
import tempfile
from dotenv import load_dotenv
from src.loader import load_codebase
from src.chunker import chunk_documents
from src.vector_store import VectorStoreDB
from src.generator import get_answer

load_dotenv()

st.set_page_config(
    page_title="CodeLens — Codebase Q&A",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Syne:wght@400;500;600;700&display=swap');

/* ── Reset & Base ─────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, .stApp {
    background-color: #080b10 !important;
    color: #c8d0dc;
    font-family: 'Syne', sans-serif;
}

/* ── Sidebar ──────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background-color: #0c1018 !important;
    border-right: 1px solid #1a2030 !important;
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] > div {
    padding: 1.5rem 1.25rem;
}

/* ── Sidebar Header Brand ─────────────────────────────────── */
.brand-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 1.25rem 0 1.5rem;
    border-bottom: 1px solid #1a2030;
    margin-bottom: 1.5rem;
}
.brand-logo {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #00d4aa 0%, #0066ff 100%);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: 700;
    color: #fff;
    flex-shrink: 0;
}
.brand-name {
    font-family: 'Syne', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: #e8edf4;
    letter-spacing: -0.3px;
}
.brand-tagline {
    font-size: 11px;
    color: #4a5568;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.05em;
    margin-top: 1px;
}

/* ── Section Labels ───────────────────────────────────────── */
.section-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #3d4f66;
    margin-bottom: 8px;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Status Badge ─────────────────────────────────────────── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
    margin-bottom: 1.5rem;
}
.status-badge.ready {
    background: rgba(0, 212, 170, 0.1);
    border: 1px solid rgba(0, 212, 170, 0.3);
    color: #00d4aa;
}
.status-badge.idle {
    background: rgba(74, 85, 104, 0.2);
    border: 1px solid rgba(74, 85, 104, 0.3);
    color: #4a5568;
}
.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
}
.status-dot.pulse {
    animation: pulse 1.8s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ── Stats Row ────────────────────────────────────────────── */
.stats-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 1.5rem;
}
.stat-card {
    background: #0f151f;
    border: 1px solid #1a2030;
    border-radius: 8px;
    padding: 10px 12px;
}
.stat-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 20px;
    font-weight: 500;
    color: #e8edf4;
    line-height: 1;
    margin-bottom: 3px;
}
.stat-label {
    font-size: 10px;
    color: #3d4f66;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Text Input ───────────────────────────────────────────── */
.stTextInput > div > div > input {
    background-color: #0f151f !important;
    color: #c8d0dc !important;
    border: 1px solid #1a2030 !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s ease;
}
.stTextInput > div > div > input:focus {
    border-color: #0066ff !important;
    box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.1) !important;
}
.stTextInput > div > div > input::placeholder {
    color: #2d3a4d !important;
}
.stTextInput label {
    font-size: 11px !important;
    color: #3d4f66 !important;
    font-family: 'JetBrains Mono', monospace !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* ── Buttons ──────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #0066ff 0%, #0044bb 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    width: 100% !important;
    letter-spacing: 0.02em;
    transition: all 0.2s ease !important;
    cursor: pointer;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(0, 102, 255, 0.3) !important;
}
.stButton > button:active {
    transform: translateY(0);
}

/* ── Main Area ────────────────────────────────────────────── */
.main-header {
    padding: 2rem 0 1.5rem;
    border-bottom: 1px solid #1a2030;
    margin-bottom: 2rem;
}
.main-title {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: #e8edf4;
    letter-spacing: -0.5px;
    margin: 0 0 6px;
}
.main-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #3d4f66;
    letter-spacing: 0.05em;
}

/* ── Empty State ──────────────────────────────────────────── */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 5rem 2rem;
    text-align: center;
}
.empty-icon {
    width: 64px;
    height: 64px;
    background: #0f151f;
    border: 1px solid #1a2030;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    margin-bottom: 1.5rem;
}
.empty-title {
    font-size: 18px;
    font-weight: 600;
    color: #e8edf4;
    margin-bottom: 8px;
    font-family: 'Syne', sans-serif;
}
.empty-body {
    font-size: 13px;
    color: #3d4f66;
    max-width: 380px;
    line-height: 1.6;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Chat Messages ────────────────────────────────────────── */
.stChatMessage {
    background: transparent !important;
    border: none !important;
    padding: 0.75rem 0 !important;
}
[data-testid="stChatMessageContent"] {
    background: #0f151f !important;
    border: 1px solid #1a2030 !important;
    border-radius: 12px !important;
    color: #c8d0dc !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 14px !important;
    line-height: 1.7 !important;
    padding: 14px 18px !important;
}
[data-testid="stChatMessageContent"] p {
    color: #c8d0dc !important;
}
[data-testid="stChatMessageContent"] code {
    background: #080b10 !important;
    color: #00d4aa !important;
    border-radius: 4px !important;
    padding: 2px 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}
[data-testid="stChatMessageContent"] pre {
    background: #080b10 !important;
    border: 1px solid #1a2030 !important;
    border-radius: 8px !important;
    padding: 14px !important;
}

/* User messages get a subtle accent */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    border-color: rgba(0, 102, 255, 0.25) !important;
    background: rgba(0, 102, 255, 0.04) !important;
}

/* ── Chat Avatar ──────────────────────────────────────────── */
.stChatMessage .stAvatar {
    background: #0f151f !important;
    border: 1px solid #1a2030 !important;
    border-radius: 8px !important;
    overflow: hidden;
    position: relative;
}
[data-testid="chatAvatarIcon-user"],
[data-testid="chatAvatarIcon-assistant"] {
    opacity: 0 !important;
    font-size: 0 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stAvatar {
    background: rgba(0, 102, 255, 0.12) !important;
    border-color: rgba(0, 102, 255, 0.3) !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stAvatar::after {
    content: "";
    position: absolute;
    inset: 0;
    background-color: #4a90e2;
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='8' r='4'/%3E%3Cpath d='M4 20c0-4 3.6-7 8-7s8 3 8 7'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='8' r='4'/%3E%3Cpath d='M4 20c0-4 3.6-7 8-7s8 3 8 7'/%3E%3C/svg%3E");
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;
    -webkit-mask-position: center;
    mask-position: center;
    -webkit-mask-size: 60%;
    mask-size: 60%;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stAvatar {
    background: rgba(0, 212, 170, 0.08) !important;
    border-color: rgba(0, 212, 170, 0.25) !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stAvatar::after {
    content: "";
    position: absolute;
    inset: 0;
    background-color: #00d4aa;
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='16 18 22 12 16 6'/%3E%3Cpolyline points='8 6 2 12 8 18'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='16 18 22 12 16 6'/%3E%3Cpolyline points='8 6 2 12 8 18'/%3E%3C/svg%3E");
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;
    -webkit-mask-position: center;
    mask-position: center;
    -webkit-mask-size: 60%;
    mask-size: 60%;
}

/* ── Chat Input ───────────────────────────────────────────── */
[data-testid="stChatInput"] {
    background: #0c1018 !important;
    border: 1px solid #1a2030 !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #c8d0dc !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 14px !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #2d3a4d !important;
}
[data-testid="stChatInput"] button {
    background: #0066ff !important;
    border-radius: 8px !important;
    color: white !important;
}

/* ── Expander ─────────────────────────────────────────────── */
.stExpander {
    background: #0c1018 !important;
    border: 1px solid #1a2030 !important;
    border-radius: 10px !important;
    margin-top: 8px !important;
}
.stExpander summary {
    color: #4a5568 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}
.stExpander summary:hover {
    color: #c8d0dc !important;
}

/* ── Alerts / Messages ────────────────────────────────────── */
.stAlert {
    border-radius: 8px !important;
    border: 1px solid !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}
.stSuccess {
    background: rgba(0, 212, 170, 0.06) !important;
    border-color: rgba(0, 212, 170, 0.25) !important;
    color: #00d4aa !important;
}
.stError {
    background: rgba(255, 60, 80, 0.06) !important;
    border-color: rgba(255, 60, 80, 0.25) !important;
    color: #ff3c50 !important;
}
.stWarning {
    background: rgba(255, 170, 0, 0.06) !important;
    border-color: rgba(255, 170, 0, 0.25) !important;
    color: #ffaa00 !important;
}

/* ── Spinner ──────────────────────────────────────────────── */
.stSpinner > div {
    border-color: #0066ff transparent transparent transparent !important;
}

/* ── Divider ──────────────────────────────────────────────── */
hr {
    border-color: #1a2030 !important;
    margin: 1.5rem 0 !important;
}

/* ── Scrollbar ────────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #1a2030; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #2d3a4d; }

/* ── Code blocks in expander ──────────────────────────────── */
.stCode {
    background: #080b10 !important;
    border: 1px solid #1a2030 !important;
    border-radius: 6px !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Session State ─────────────────────────────────────────────────────────────
if "vectordb" not in st.session_state:
    st.session_state["vectordb"] = None
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "file_count" not in st.session_state:
    st.session_state["file_count"] = 0
if "chunk_count" not in st.session_state:
    st.session_state["chunk_count"] = 0
if "repo_name" not in st.session_state:
    st.session_state["repo_name"] = None

is_ready = st.session_state["vectordb"] is not None

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""
    <div class="brand-header">
        <div class="brand-logo">⬡</div>
        <div>
            <div class="brand-name">CodeLens</div>
            <div class="brand-tagline">RAG · Codebase Q&A</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Status
    if is_ready:
        st.markdown(f"""
        <div class="status-badge ready">
            <div class="status-dot pulse"></div>
            Index ready
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="stats-row">
            <div class="stat-card">
                <div class="stat-value">{st.session_state['file_count']}</div>
                <div class="stat-label">Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{st.session_state['chunk_count']}</div>
                <div class="stat-label">Chunks</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state["repo_name"]:
            st.markdown(f"""
            <div class="section-label">Source</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #4a5568;
                        background: #0f151f; border: 1px solid #1a2030; border-radius: 6px;
                        padding: 8px 10px; margin-bottom: 1.5rem; word-break: break-all;">
                {st.session_state['repo_name']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-badge idle">
            <div class="status-dot"></div>
            No index loaded
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Ingest Codebase</div>', unsafe_allow_html=True)
    codebase_input = st.text_input(
        "Path or GitHub URL",
        value="",
        placeholder="https://github.com/user/repo or ./my-project",
        label_visibility="collapsed",
    )

    if st.button("⬡ Ingest Codebase", use_container_width=True):
        if not codebase_input:
            st.error("Enter a path or GitHub URL.")
        else:
            actual_path = codebase_input
            display_name = codebase_input

            if codebase_input.startswith("http://") or codebase_input.startswith("https://"):
                repo_name = codebase_input.rstrip("/").split("/")[-1].removesuffix(".git")
                display_name = repo_name
                repos_dir = os.path.join(os.getcwd(), "repos")
                os.makedirs(repos_dir, exist_ok=True)
                target_dir = os.path.join(repos_dir, repo_name)

                with st.spinner(f"Cloning {repo_name}…"):
                    try:
                        import shutil, stat
                        def remove_readonly(func, path, _):
                            os.chmod(path, stat.S_IWRITE)
                            func(path)
                        if os.path.exists(target_dir):
                            shutil.rmtree(target_dir, onerror=remove_readonly)
                        subprocess.run(
                            ["git", "clone", codebase_input, target_dir],
                            check=True, capture_output=True,
                        )
                        actual_path = target_dir
                        st.success(f"Cloned into ./repos/{repo_name}")
                    except subprocess.CalledProcessError as e:
                        st.error(f"Clone failed: {e.stderr.decode('utf-8', errors='ignore')}")
                        actual_path = None

            docs = []
            if actual_path and not os.path.exists(actual_path):
                st.error("Directory not found.")
            elif actual_path:
                with st.spinner("Reading files…"):
                    docs = load_codebase(actual_path)

            if len(docs) > 0:
                with st.spinner("Chunking…"):
                    chunks = chunk_documents(docs)

                with st.spinner("Building vector index…"):
                    db = VectorStoreDB()
                    db.build_index(chunks)
                    st.session_state["vectordb"] = db
                    st.session_state["file_count"] = len(docs)
                    st.session_state["chunk_count"] = len(chunks)
                    st.session_state["repo_name"] = display_name
                    st.session_state["messages"] = []
                    st.success("Index built — start asking questions!")
                    st.rerun()
            elif actual_path:
                st.warning("No supported code files found.")

    # Clear chat
    if is_ready and st.session_state["messages"]:
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("Clear conversation", use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()

    # Footer
    st.markdown("""
    <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #1a2030;">
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #1a2030;
                    text-align: center; letter-spacing: 0.08em;">
            FAISS · Gemini · Streamlit
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Main Area ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <div class="main-title">Codebase Q&A</div>
    <div class="main-subtitle">// Ask anything about your code — RAG-powered answers with source context</div>
</div>
""", unsafe_allow_html=True)

# Empty state
if not is_ready:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">⬡</div>
        <div class="empty-title">No codebase loaded</div>
        <div class="empty-body">
            Paste a GitHub URL or local path in the sidebar,<br>
            then click <strong>Ingest Codebase</strong> to build your index.
        </div>
    </div>
    """, unsafe_allow_html=True)
elif not st.session_state["messages"]:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">💬</div>
        <div class="empty-title">Index ready — start asking</div>
        <div class="empty-body">
            Try: "What does the main entry point do?" or<br>
            "How is authentication handled?" or "List all API endpoints."
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Chat history ───────────────────────────────────────────────────────────────
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─── Chat input ─────────────────────────────────────────────────────────────────
if query := st.chat_input(
    "Ask about the codebase…" if is_ready else "Ingest a codebase first…",
    disabled=not is_ready,
):
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("GOOGLE_API_KEY is not set. Add it to your .env file.")
    else:
        st.session_state["messages"].append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            with st.spinner("Searching index…"):
                db: VectorStoreDB = st.session_state["vectordb"]
                try:
                    results = db.search(query, top_k=4)
                    context_chunks = [res[0] for res in results]
                    answer = get_answer(query, context_chunks, st.session_state["messages"])
                    st.markdown(answer)
                    st.session_state["messages"].append({"role": "assistant", "content": answer})

                    with st.expander("⬡ Retrieved context snippets"):
                        for i, (doc, score) in enumerate(results):
                            file_path = doc.metadata.get("file_path", "unknown")
                            st.markdown(
                                f"<span style='font-family:JetBrains Mono,monospace;font-size:11px;"
                                f"color:#3d4f66;'>#{i+1} · </span>"
                                f"<span style='font-family:JetBrains Mono,monospace;font-size:11px;"
                                f"color:#4a90e2;'>{file_path}</span>"
                                f"<span style='font-family:JetBrains Mono,monospace;font-size:10px;"
                                f"color:#1a2030;'> · dist {score:.4f}</span>",
                                unsafe_allow_html=True,
                            )
                            st.code(doc.page_content, language="python")
                except Exception as e:
                    st.error(f"Error: {e}")