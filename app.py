import streamlit as st
import google.generativeai as genai
from PIL import Image

# -----------------------------------------------------------------------------
# 1. Page Configuration (Centered, Distraction-Free Layout)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Snap & Study",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# 2. Tier-1 SaaS Custom CSS (Notion / ChatGPT Minimalist Aesthetic)
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Completely remove default Streamlit chrome */
#MainMenu {visibility: hidden; display: none !important;}
footer {visibility: hidden; display: none !important;}
header {visibility: hidden; display: none !important;}
div[data-testid="stDecoration"] {display: none !important;}
div[data-testid="stToolbar"] {display: none !important;}

/* Global Typography & Font Smoothing */
html, body, [class*="css"], .stMarkdown {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    letter-spacing: -0.011em;
    -webkit-font-smoothing: antialiased;
}

/* Distraction-free container sizing */
.main .block-container {
    max-width: 780px !important;
    padding-top: 2.5rem !important;
    padding-bottom: 5rem !important;
}

/* Minimalist App Header */
.app-header {
    margin-bottom: 2rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid rgba(128, 128, 128, 0.15);
}

.app-title {
    font-size: 1.85rem;
    font-weight: 700;
    line-height: 1.25;
    margin-bottom: 0.35rem;
    color: var(--text-color);
}

.app-description {
    font-size: 0.95rem;
    line-height: 1.5;
    opacity: 0.75;
    margin-bottom: 0;
    color: var(--text-color);
}

/* Modern File Uploader & Controls */
div[data-testid="stFileUploader"] {
    margin-bottom: 1.2rem;
}

div[data-testid="stFileUploader"] section {
    border-radius: 10px;
    border: 1px dashed rgba(128, 128, 128, 0.25);
    background-color: var(--secondary-background-color);
    transition: border-color 0.2s ease, background-color 0.2s ease;
}

div[data-testid="stFileUploader"] section:hover {
    border-color: rgba(99, 102, 241, 0.6);
}

/* Primary Action Button (Refined SaaS style) */
div.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.95rem;
    padding: 0.6rem 1.2rem;
    transition: all 0.15s ease-in-out;
    border: 1px solid transparent;
}

/* Clean Document Container for AI Study Guide */
.document-container {
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.15);
    border-radius: 12px;
    padding: 2.25rem 2rem;
    margin-top: 1.75rem;
    margin-bottom: 1.75rem;
    line-height: 1.75;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

/* Reader Typography within Document */
.document-container h2 {
    font-size: 1.35rem;
    font-weight: 700;
    margin-top: 1.6rem;
    margin-bottom: 0.75rem;
    padding-bottom: 0.3rem;
    border-bottom: 1px solid rgba(128, 128, 128, 0.12);
    color: var(--text-color);
}

.document-container h3 {
    font-size: 1.15rem;
    font-weight: 600;
    margin-top: 1.4rem;
    margin-bottom: 0.6rem;
    color: var(--text-color);
}

.document-container p, .document-container li {
    font-size: 0.975rem;
    line-height: 1.75;
    color: var(--text-color);
}

.document-container ul, .document-container ol {
    padding-left: 1.4rem;
    margin-bottom: 1rem;
}

.document-container li {
    margin-bottom: 0.4rem;
}

.document-container blockquote {
    border-left: 3px solid rgba(99, 102, 241, 0.6);
    padding-left: 1rem;
    margin: 1rem 0;
    opacity: 0.85;
}

/* Sleek Expander Styling */
div[data-testid="stExpander"] {
    border-radius: 10px;
    border: 1px solid rgba(128, 128, 128, 0.18);
    background-color: var(--secondary-background-color);
    margin-top: 0.75rem;
    margin-bottom: 1rem;
    overflow: hidden;
}

/* Download button subtle styling */
div[data-testid="stDownloadButton"] > button {
    border-radius: 8px;
    font-weight: 500;
    font-size: 0.9rem;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. API Key & Gemini Client Setup (Preserved Backend Logic)
# -----------------------------------------------------------------------------
try:
    if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        st.error("🔑 **GEMINI_API_KEY Missing**: Please configure your API key in Streamlit secrets (`.streamlit/secrets.toml`).")
        st.stop()
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"⚠️ **Authentication Error**: Failed to configure Gemini API client. Details: {str(e)}")
    st.stop()

# -----------------------------------------------------------------------------
# 4. Minimalist Header
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="app-header">
        <h1 class="app-title">Snap & Study</h1>
        <p class="app-description">Upload notes, diagrams, or textbook pages to generate a clean, distraction-free study guide.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 5. Smart Uploader & Controls
# -----------------------------------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload Source Notes",
    type=["jpg", "jpeg", "png", "webp"],
    help="Accepts JPG, PNG, and WebP images of notes or textbook pages.",
    label_visibility="collapsed",
)

image = None
if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        # Distraction-Free State: Source image collapsed by default inside a sleek expander
        with st.expander("🖼️ View Source Document", expanded=False):
            st.image(image, use_container_width=True)
    except Exception as img_err:
        st.error(f"❌ Failed to read the uploaded image: {str(img_err)}")
        st.stop()

study_mode = st.selectbox(
    "Study Focus",
    options=[
        "Standard Comprehensive Guide (Summary + Vocab + Quiz)",
        "Quick Exam Crash Sheet (Key Formulas & Bullet Summary)",
        "Active Recall & Flashcards (Q&A Drill Mode)",
    ],
    index=0,
    label_visibility="collapsed",
)

generate_btn = st.button("Generate Study Guide", use_container_width=True, type="primary")

# -----------------------------------------------------------------------------
# 6. Processing & Generation (Strictly Preserved Backend & Model)
# -----------------------------------------------------------------------------
if generate_btn:
    if uploaded_file is None or image is None:
        st.warning("Please upload an image of your study notes first.")
    else:
        with st.spinner("Synthesizing notes and generating study guide..."):
            try:
                # Retained model name: gemini-3.5-flash-lite
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
                - Give 1 mnemonic or quick mental framework to remember this topic easily.
                """

                response = model.generate_content([system_prompt, image])

                if not response or not response.text:
                    st.error("The model returned an empty response. Please try again with a clearer image.")
                    st.stop()

                st.session_state["study_guide_result"] = response.text

            except Exception as api_error:
                st.error(f"❌ **Generation Error**: Unable to process notes. Details: {str(api_error)}")
                st.stop()

# -----------------------------------------------------------------------------
# 7. Professional Document Output Area
# -----------------------------------------------------------------------------
if "study_guide_result" in st.session_state:
    st.markdown('<div class="document-container">', unsafe_allow_html=True)
    st.markdown(st.session_state["study_guide_result"])
    st.markdown("</div>", unsafe_allow_html=True)

    # Action bar below the document
    st.download_button(
        label="📥 Download Study Guide (.md)",
        data=st.session_state["study_guide_result"],
        file_name="study_guide.md",
        mime="text/markdown",
        use_container_width=True,
    )