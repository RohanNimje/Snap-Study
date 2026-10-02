import os
import streamlit as st
import google.generativeai as genai
from PIL import Image

# Load .env for local development (safe no-op if file absent or dotenv not installed)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed — that's fine in cloud environments

# -----------------------------------------------------------------------------
# 1. Page Configuration (Split-Screen Workspace)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Snap & Study | AI Note Architect",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# 2. Ultra-Premium Dark SaaS CSS Styling
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* Completely strip default Streamlit chrome */
#MainMenu {visibility: hidden; display: none !important;}
footer {visibility: hidden; display: none !important;}
header {visibility: hidden; display: none !important;}
div[data-testid="stDecoration"] {display: none !important;}
div[data-testid="stToolbar"] {display: none !important;}

/* Global Typography & Deep Dark Background */
html, body, [class*="css"], .stMarkdown {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    letter-spacing: -0.013em;
    -webkit-font-smoothing: antialiased;
}

.stApp {
    background-color: #0E1015 !important;
    color: #E2E8F0 !important;
}

.main .block-container {
    padding-top: 0.6rem !important;
    padding-bottom: 0 !important;
    max-width: 1440px !important;
    overflow: hidden !important;
}

/* ── Force both columns to share the same top edge ── */
[data-testid="stHorizontalBlock"] {
    align-items: flex-start !important;
}

/* ── Right Panel: strict 70vh flex column, never grows ── */
.right-panel-wrapper {
    display: flex;
    flex-direction: column;
    height: 70vh;
    max-height: 70vh;
    overflow: hidden;
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* Scrollable middle zone — expands to fill remaining height */
.content-scroll-area {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding-right: 0.4rem;
    scroll-behavior: smooth;
    padding-top: 0 !important;
    margin-top: 0 !important;
}

/* Left Control Panel Glass Card */
[data-testid="column"]:first-child > div:first-child {
    background: #151821;
    border-radius: 18px;
    padding: 1.75rem 1.5rem !important;
    border: 1px solid rgba(255, 255, 255, 0.07);
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
}

/* Right Output Column */
[data-testid="column"]:last-child {
    background: transparent !important;
}
[data-testid="column"]:last-child > div:first-child {
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
}

/* Brand Badge Pill */
.brand-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.28rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.15), rgba(236, 72, 153, 0.15));
    border: 1px solid rgba(168, 85, 247, 0.35);
    color: #D8B4FE;
    margin-bottom: 0.65rem;
}

/* Gradient Hero Brand Title */
.brand-title {
    font-size: 1.85rem;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 0.35rem;
    background: linear-gradient(135deg, #A855F7 0%, #EC4899 50%, #EF4444 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.brand-tagline {
    font-size: 0.875rem;
    line-height: 1.5;
    color: #94A3B8;
    margin-bottom: 1.4rem;
}

/* File Uploader Custom Dark Mode */
div[data-testid="stFileUploader"] {
    margin-bottom: 1rem;
}

div[data-testid="stFileUploader"] section {
    border-radius: 12px;
    border: 1.5px dashed rgba(168, 85, 247, 0.35) !important;
    background-color: rgba(255, 255, 255, 0.02) !important;
    transition: all 0.25s ease;
    padding: 1.2rem 0.75rem;
}

div[data-testid="stFileUploader"] section:hover {
    border-color: #A855F7 !important;
    background-color: rgba(168, 85, 247, 0.06) !important;
    transform: translateY(-1px);
}

/* Primary Vibrant Button */
div.stButton > button {
    background: linear-gradient(135deg, #8B5CF6 0%, #D946EF 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.72rem 1.4rem !important;
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.35) !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(139, 92, 246, 0.55) !important;
    background: linear-gradient(135deg, #7C3AED 0%, #C026D3 100%) !important;
}

/* Source Preview Card on Upload */
.source-preview-card {
    background: rgba(21, 24, 33, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 1.25rem;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
}

/* Expander Dark Theme Styling */
div[data-testid="stExpander"] {
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    background-color: rgba(255, 255, 255, 0.02) !important;
    margin-bottom: 1.25rem !important;
}

/* Dopamine Fade In Animation */
@keyframes fadeInUp {
    0% {
        opacity: 0;
        transform: translateY(24px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Glowing Dopamine Card Artifact */
.dopamine-card {
    animation: fadeInUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
    background: rgba(21, 24, 33, 0.85) !important;
    border: 1px solid rgba(168, 85, 247, 0.3);
    border-radius: 20px;
    padding: 2.4rem 2.6rem;
    backdrop-filter: blur(14px);
    box-shadow:
        0 1px 3px rgba(0, 0, 0, 0.4),
        0 12px 32px -8px rgba(168, 85, 247, 0.18),
        0 32px 64px -16px rgba(0, 0, 0, 0.6);
    position: relative;
    overflow: hidden;
    margin-bottom: 1.5rem;
}

.dopamine-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #8B5CF6 0%, #EC4899 50%, #EF4444 100%);
    z-index: 1;
}

/* Floating Action Bar */
.floating-action-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(21, 24, 33, 0.95);
    border: 1px solid rgba(168, 85, 247, 0.25);
    border-radius: 12px;
    padding: 0.75rem 1.2rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.action-bar-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.action-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.76rem;
    font-weight: 700;
    padding: 0.25rem 0.65rem;
    border-radius: 6px;
    background: rgba(168, 85, 247, 0.18);
    color: #D8B4FE;
    border: 1px solid rgba(168, 85, 247, 0.4);
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

.action-meta {
    font-size: 0.82rem;
    color: #94A3B8;
    font-weight: 500;
}

/* Typography inside Dopamine Artifact */
.dopamine-card h1, .dopamine-card h2 {
    font-size: 1.35rem !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
    margin-top: 1.6rem !important;
    margin-bottom: 0.75rem !important;
    padding-bottom: 0.4rem !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
}

.dopamine-card h3 {
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    color: #F1F5F9 !important;
    margin-top: 1.2rem !important;
    margin-bottom: 0.5rem !important;
}

.dopamine-card p, .dopamine-card li {
    font-size: 0.96rem !important;
    line-height: 1.8 !important;
    color: #CBD5E1 !important;
}

.dopamine-card ul, .dopamine-card ol {
    padding-left: 1.45rem !important;
    margin-bottom: 1rem !important;
}

.dopamine-card blockquote {
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%) !important;
    border-left: 4px solid #A855F7 !important;
    border-radius: 0 12px 12px 0 !important;
    padding: 1rem 1.4rem !important;
    margin: 1.4rem 0 !important;
}

.dopamine-card blockquote p {
    color: #E9D5FF !important;
    font-weight: 600 !important;
}

.dopamine-card code {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    background: rgba(168, 85, 247, 0.15) !important;
    color: #D8B4FE !important;
    padding: 0.15rem 0.4rem !important;
    border-radius: 4px !important;
}

/* Empty State Canvas */
@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
    100% { transform: translateY(0px); }
}

.empty-state-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 5rem 2rem;
    border: 1.5px dashed rgba(168, 85, 247, 0.25);
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.015);
    min-height: 480px;
    animation: float 6s ease-in-out infinite;
}

.empty-state-glyph {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    filter: drop-shadow(0 4px 15px rgba(168, 85, 247, 0.4));
}

.empty-state-heading {
    font-size: 1.6rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, #A855F7 0%, #EC4899 50%, #EF4444 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.empty-state-copy {
    font-size: 0.95rem;
    max-width: 440px;
    color: #94A3B8;
    line-height: 1.6;
}

/* Chat Message Custom Dark Theme Styling */
div[data-testid="stChatMessage"] {
    background-color: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.07) !important;
    border-radius: 14px !important;
    padding: 1.1rem 1.3rem !important;
    margin-bottom: 0.85rem !important;
    backdrop-filter: blur(10px);
}

div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.08), rgba(236, 72, 153, 0.05)) !important;
    border: 1px solid rgba(168, 85, 247, 0.25) !important;
}

div[data-testid="stChatMessageContent"] {
    color: #E2E8F0 !important;
    font-size: 0.95rem !important;
    line-height: 1.7 !important;
}

/* Chat Input — in-column, natively anchored by Streamlit */
div[data-testid="stChatInput"] {
    position: sticky !important;
    bottom: 0 !important;
    z-index: 999 !important;
    border: 1px solid rgba(168, 85, 247, 0.35) !important;
    border-top: 2px solid rgba(168, 85, 247, 0.5) !important;
    border-radius: 14px !important;
    box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.6) !important;
    background: #0E1015 !important;
    margin-top: 0.5rem !important;
}

div[data-testid="stChatInput"]:focus-within {
    border-color: #A855F7 !important;
    box-shadow: 0 0 0 2px rgba(168, 85, 247, 0.25), 0 -4px 24px rgba(0, 0, 0, 0.6) !important;
}

div[data-testid="stChatInput"] textarea {
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    font-size: 0.95rem !important;
    caret-color: #0f172a !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
}

div[data-testid="stChatInput"] button {
    color: #7C3AED !important;
}

/* Sleek Download Button */
div[data-testid="stDownloadButton"] > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.2rem !important;
    border: 1.5px solid rgba(168, 85, 247, 0.4) !important;
    background: rgba(168, 85, 247, 0.08) !important;
    color: #D8B4FE !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stDownloadButton"] > button:hover {
    background: rgba(168, 85, 247, 0.18) !important;
    border-color: #A855F7 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(168, 85, 247, 0.3) !important;
}

/* Chat message list — fills space inside the flex scroll area */
.chat-scroll-container {
    display: flex;
    flex-direction: column;
    gap: 0;
    padding-bottom: 0.5rem;
}

/* Scrollbar for content-scroll-area */
.content-scroll-area::-webkit-scrollbar {
    width: 5px;
}

.content-scroll-area::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.03);
    border-radius: 4px;
}

.content-scroll-area::-webkit-scrollbar-thumb {
    background: rgba(168, 85, 247, 0.35);
    border-radius: 4px;
}

.content-scroll-area::-webkit-scrollbar-thumb:hover {
    background: rgba(168, 85, 247, 0.6);
}

/* Chat input — sits at the bottom of right-panel-wrapper naturally */
/* (flex-shrink:0 prevents it from being squeezed by scroll area) */
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. API Key & Gemini Client Configuration
# Priority: st.secrets (Streamlit Cloud) → OS environment var → .env file
# -----------------------------------------------------------------------------
try:
    api_key = (
        st.secrets.get("GEMINI_API_KEY")          # 1️⃣  Streamlit Cloud secrets.toml
        or os.environ.get("GEMINI_API_KEY")        # 2️⃣  Shell / CI environment variable
    )
    if not api_key:
        st.error(
            "🔑 **GEMINI_API_KEY not found.**\n\n"
            "**Locally:** Create a `.env` file with `GEMINI_API_KEY=your_key_here`, "
            "or set it as a shell environment variable.\n\n"
            "**Streamlit Cloud:** Add it under *Settings → Secrets* in the dashboard."
        )
        st.stop()
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"⚠️ **Authentication Error**: Failed to configure Gemini API client. Details: {str(e)}")
    st.stop()

# -----------------------------------------------------------------------------
# 4. Session State Initialization
# -----------------------------------------------------------------------------
if "study_guide_result" not in st.session_state:
    st.session_state.study_guide_result = None
if "study_mode_used" not in st.session_state:
    st.session_state.study_mode_used = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# -----------------------------------------------------------------------------
# 5. Split-Screen Layout (Left: 3 cols, Right: 7 cols)
# -----------------------------------------------------------------------------
col_control, col_output = st.columns([3, 7], gap="large")

# =============================================================================
# LEFT PANEL (Width 3): Clean Control Deck (No Tabs, No Expander)
# =============================================================================
with col_control:
    st.markdown(
        """
        <div class="brand-badge">⚡ AI Study Studio</div>
        <h1 class="brand-title">Snap & Study</h1>
        <p class="brand-tagline">Turn textbook pages, handwritten notes, and sketches into structured study guides & interactive AI tutors.</p>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload Source Material",
        type=["jpg", "jpeg", "png", "webp"],
        help="Upload clear photos of notes or textbooks (JPG, PNG, WebP).",
        label_visibility="collapsed",
    )

    image = None
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
        except Exception as img_err:
            st.error(f"❌ Failed to read uploaded image: {str(img_err)}")
            st.stop()

    st.markdown("<p style='font-size: 0.82rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.4rem; margin-top: 0.6rem;'>🎯 Focus Mode</p>", unsafe_allow_html=True)
    study_mode = st.selectbox(
        "Focus Mode",
        options=[
            "Standard Comprehensive Guide (Summary + Vocab + Quiz)",
            "Quick Exam Crash Sheet (Key Formulas & Bullet Summary)",
            "Active Recall & Flashcards (Q&A Drill Mode)",
        ],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("<div style='height: 0.6rem;'></div>", unsafe_allow_html=True)
    generate_btn = st.button("Generate Study Guide ✨", use_container_width=True)

# =============================================================================
# RIGHT PANEL (Width 7): Dynamic Canvas Workspace & Bottom Sticky Chat Bar
# =============================================================================
with col_output:
    # Native fixed-height scrollable area — no custom HTML wrapper needed
    chat_area = st.container(height=520, border=False)
    with chat_area:
        # 1. Handle Study Guide Generation Logic
        if generate_btn:
            if uploaded_file is None or image is None:
                st.warning("⚠️ Please upload an image of your study notes on the left panel first.")
            else:
                with st.spinner("🧠 Analyzing source material & synthesizing study guide..."):
                    try:
                        model = genai.GenerativeModel("gemini-3.5-flash-lite")

                        system_prompt = f"""
                        You are an elite academic AI tutor with deep expertise in pedagogy and active recall learning.
                        Analyze this image of study material carefully.
                        
                        Selected Focus Mode: {study_mode}

                        Provide a high-yield, beautifully organized study guide using clean Markdown formatting:
                        
                        ## 📌 Core Summary & Key Concepts
                        - Break down the main themes, key formulas, or primary arguments into clean, digestible bullet points.
                        - Highlight foundational principles and big-picture takeaways.
                        
                        ## 🧠 Vocabulary & Technical Jargon Demystified
                        - Identify complex, technical, or confusing terms from the material.
                        - Provide simple, intuitive explanations and analogies.
                        
                        ## 📝 High-Yield Practice Quiz & Active Recall
                        - Provide 3 challenging practice questions to test deep comprehension.
                        - Include an answer key with brief explanations.
                        
                        ## 💡 Pro Study Tip & Memory Hook
                        > **Memory Accelerator**: Give 1 mnemonic or quick mental framework to remember this topic easily.
                        """

                        response = model.generate_content([system_prompt, image])

                        if not response or not response.text:
                            st.error("The model returned an empty response. Please try again with a clearer image.")
                            st.stop()

                        st.session_state.study_guide_result = response.text
                        st.session_state.study_mode_used = study_mode

                    except Exception as api_error:
                        st.error(f"❌ **Generation Error**: Unable to process notes. Details: {str(api_error)}")
                        st.stop()

        # 2. Main Dynamic Workspace States
        has_guide = st.session_state.study_guide_result is not None
        has_chat = len(st.session_state.chat_messages) > 0

        if not uploaded_file:
            # Default State: Breathtaking Empty State
            st.markdown(
                """
                <div class="empty-state-card">
                    <div class="empty-state-glyph">✨</div>
                    <div class="empty-state-heading">Turn Notes into Knowledge</div>
                    <div class="empty-state-copy">
                        Upload your handwritten scribbles or dense textbook pages on the left.
                        Generate a high-yield study guide or chat directly with your document.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif not has_guide and not has_chat:
            # On Upload: Prominently display source document preview
            st.markdown(
                f"""
                <div class="floating-action-bar">
                    <div class="action-bar-left">
                        <span class="action-pill">📄 Source Document</span>
                        <span class="action-meta">{uploaded_file.name}</span>
                    </div>
                    <div class="action-meta" style="font-weight: 600; color: #D8B4FE;">
                        Ready for Synthesis & Chat
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown('<div class="source-preview-card">', unsafe_allow_html=True)
            st.image(image, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Auto-Hide Image on Generation or Question: Collapse into small expander
            with st.expander("View Source Image", expanded=False):
                st.image(image, use_container_width=True)

            # On Generate: Replace with AI-generated Study Guide Trophy Card
            if has_guide:
                action_bar_html = f"""
            <div class="floating-action-bar">
                <div class="action-bar-left">
                    <span class="action-pill">⚡ Knowledge Artifact</span>
                    <span class="action-meta">{st.session_state.get('study_mode_used', 'Standard').split('(')[0].strip()}</span>
                </div>
                <div class="action-meta" style="font-weight: 600; color: #D8B4FE;">
                    Active Recall Enabled
                </div>
            </div>
            """
                st.markdown(action_bar_html, unsafe_allow_html=True)

                st.markdown('<div class="dopamine-card">', unsafe_allow_html=True)
                st.markdown(st.session_state.study_guide_result)
                st.markdown("</div>", unsafe_allow_html=True)

                # Export action button
                st.download_button(
                    label="📥 Export Study Guide (.md)",
                    data=st.session_state.study_guide_result,
                    file_name="Snap_and_Study_Guide.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

        # 3. Chat Discussion History
        if has_chat:
            st.markdown(
                """
                <div style="display:flex;align-items:center;gap:0.5rem;margin:0 !important;padding-bottom:0.3rem;border-bottom:1px solid rgba(255,255,255,0.08);">
                    <span style="font-size:1.1rem;font-weight:700;color:#FFFFFF;">💬 Document Q&A Discussion</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

    # 4. Chat Input — placed directly below the native fixed-height container
    chat_query = st.chat_input("Ask anything about this document...")

    if chat_query:
        if uploaded_file is None or image is None:
            st.warning("⚠️ Please upload an image of your notes before asking questions.")
        else:
            st.session_state.chat_messages.append({"role": "user", "content": chat_query})
            with st.spinner("🤖 Thinking..."):
                try:
                    model = genai.GenerativeModel("gemini-3.5-flash-lite")
                    chat_system_prompt = f"""
                    You are an elite academic AI tutor assisting a student with their uploaded study material.
                    Analyze the provided image carefully and answer the student's question accurately, clearly, and concisely.
                    Use formatting, bullet points, and code blocks where helpful to enhance readability.

                    Student Question: {chat_query}
                    """
                    # Stream the response for a real-time typewriter effect
                    stream = model.generate_content(
                        [chat_system_prompt, image],
                        stream=True,
                    )
                    with st.chat_message("assistant"):
                        def _chunk_generator(stream):
                            for chunk in stream:
                                if chunk.text:
                                    yield chunk.text
                        assistant_reply = st.write_stream(_chunk_generator(stream))
                    if not assistant_reply:
                        assistant_reply = "I could not analyze the image for this question. Please try again."
                    st.session_state.chat_messages.append({"role": "assistant", "content": assistant_reply})
                except Exception as chat_err:
                    st.session_state.chat_messages.append({"role": "assistant", "content": f"⚠️ Error answering question: {str(chat_err)}"})
            st.rerun()