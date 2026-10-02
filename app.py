import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# -----------------------------------------------------------------------------
# 1. Page Configuration & SaaS Theme Setup
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Snap & Study — AI Note Synthesizer & Tutor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# 2. Premium Custom CSS Styling (Dark/Modern SaaS UI)
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* Hide Streamlit default chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
div[data-testid="stDecoration"] {display: none;}
div[data-testid="stToolbar"] {display: none;}

/* Global Typography & Palette */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* App Background & Container Spacing */
.main .block-container {
    padding-top: 1.8rem;
    padding-bottom: 3rem;
    max-width: 1300px;
}

/* Header & Hero Section */
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(168, 85, 247, 0.15));
    border: 1px solid rgba(99, 102, 241, 0.35);
    color: #a5b4fc;
    padding: 0.35rem 0.9rem;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}

.hero-title {
    font-size: 2.3rem;
    font-weight: 800;
    line-height: 1.2;
    background: linear-gradient(135deg, #ffffff 30%, #a5b4fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 1rem;
    font-weight: 400;
    margin-bottom: 1.8rem;
    max-width: 700px;
}

/* Glassmorphism Card Style */
.saas-card {
    background: rgba(15, 23, 42, 0.65);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.4rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    transition: border-color 0.2s ease;
}

.saas-card:hover {
    border-color: rgba(99, 102, 241, 0.3);
}

.card-title {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 1.1rem;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 0.75rem;
}

/* Empty State Box */
.empty-state {
    text-align: center;
    padding: 3.5rem 1.5rem;
    border: 2px dashed rgba(255, 255, 255, 0.12);
    border-radius: 16px;
    background: rgba(15, 23, 42, 0.3);
}

.empty-state-icon {
    font-size: 2.8rem;
    margin-bottom: 0.8rem;
    opacity: 0.7;
}

.empty-state-text {
    color: #94a3b8;
    font-size: 0.95rem;
    line-height: 1.5;
}

/* Primary Button Styling */
div.stButton > button:first-child {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 0.65rem 1.4rem;
    font-weight: 600;
    font-size: 0.95rem;
    letter-spacing: 0.01em;
    box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.39);
    transition: all 0.2s ease-in-out;
    width: 100%;
}

div.stButton > button:first-child:hover {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.6);
    transform: translateY(-1px);
}

/* Output Card & Highlight Badges */
.badge-pill {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    background: rgba(99, 102, 241, 0.2);
    color: #818cf8;
    border: 1px solid rgba(99, 102, 241, 0.3);
    margin-right: 0.4rem;
}

/* Expander custom styling */
.streamlit-expanderHeader {
    font-weight: 600 !important;
    border-radius: 8px !important;
    background-color: rgba(30, 41, 59, 0.5) !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. API Key & Gemini Client Initialization
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
# 4. Header & Hero Section
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div>
        <div class="hero-badge">⚡ Powered by Gemini 3.5 Flash Lite</div>
        <h1 class="hero-title">Snap & Study</h1>
        <p class="hero-subtitle">Transform handwritten notes, textbook pages, and lecture slides into structured summaries, key vocabulary breakdowns, and instant practice quizzes.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 5. Side-by-Side Main Workspace Layout
# -----------------------------------------------------------------------------
col_left, col_right = st.columns([1, 1.15], gap="large")

# ---------------------------------
# Left Column: Upload & Input Panel
# ---------------------------------
with col_left:
    st.markdown('<div class="card-title">📷 <span>Source Document</span></div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload a photo of your notes or textbook",
        type=["jpg", "jpeg", "png", "webp"],
        help="Supports JPG, PNG, and WebP formats.",
        label_visibility="collapsed",
    )

    study_mode = st.selectbox(
        "🎯 Study Focus Mode",
        options=[
            "Standard Comprehensive Guide (Summary + Vocab + Quiz)",
            "Quick Exam Crash Sheet (Key Formulas & Bullet Summary)",
            "Active Recall & Flashcards (Q&A Drill Mode)",
        ],
        index=0,
    )

    generate_btn = st.button("Generate Study Guide ✨", use_container_width=True)

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.markdown("<br>", unsafe_allow_html=True)
            st.image(image, caption="📸 Uploaded Source Image", use_container_width=True)
        except Exception as img_err:
            st.error(f"❌ Failed to load image: {str(img_err)}")
            st.stop()

# ---------------------------------
# Right Column: AI Output & Study Hub
# ---------------------------------
with col_right:
    st.markdown('<div class="card-title">📖 <span>Generated Study Guide</span></div>', unsafe_allow_html=True)

    if generate_btn:
        if uploaded_file is None:
            st.warning("⚠️ Please upload an image of your notes first.")
        else:
            with st.spinner("🧠 Analyzing notes & synthesizing key concepts with Gemini 3.5 Flash Lite..."):
                try:
                    # Initialize the Gemini 3.5 Flash Lite model
                    model = genai.GenerativeModel("gemini-3.5-flash-lite")
                    
                    # Prompt tailored to selected mode
                    system_prompt = f"""
                    You are an elite academic AI tutor with deep expertise in pedagogy and active recall learning.
                    Analyze this image of study material carefully.
                    
                    Selected Focus Mode: {study_mode}

                    Provide a high-yield, beautifully organized study guide using clear Markdown formatting:
                    
                    ### 📌 1. Core Summary & Key Concepts
                    - Break down the main themes, key formulas, or primary arguments into clean, digestible bullet points.
                    - Highlight foundational principles and big-picture takeaways.
                    
                    ### 🧠 2. Vocabulary & Technical Jargon Demystified
                    - Identify complex, technical, or confusing terms from the material.
                    - Provide simple, intuitive explanations and analogies.
                    
                    ### 📝 3. High-Yield Practice Quiz & Active Recall
                    - Provide 3 challenging multiple-choice or short-answer practice questions to test deep comprehension.
                    - Include a hidden/separated answer key with brief explanations.
                    
                    ### 💡 4. Pro Study Tip & Memory Hook
                    - Give 1 mnemonic or quick mental framework to remember this topic easily.
                    
                    Ensure the response is structured, encouraging, and clear.
                    """

                    response = model.generate_content([system_prompt, image])
                    
                    if not response or not response.text:
                        st.error("⚠️ The model returned an empty response. Please try again with a clearer image.")
                        st.stop()
                        
                    study_guide_text = response.text
                    
                    # Cache output in session state for persistence across interactions
                    st.session_state["study_guide_result"] = study_guide_text
                    
                except Exception as api_error:
                    st.error(f"❌ **Generation Error**: Unable to process notes. Details: {str(api_error)}")
                    st.stop()

    # Display results if available in session state
    if "study_guide_result" in st.session_state:
        st.success("✅ Study guide generated successfully!")
        
        # Display the formatted content inside a clean container
        st.markdown(st.session_state["study_guide_result"])
        
        st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 1.5rem 0;'>", unsafe_allow_html=True)
        
        # Download button for easy offline export
        st.download_button(
            label="📥 Download Study Guide (Markdown)",
            data=st.session_state["study_guide_result"],
            file_name="snap_study_guide.md",
            mime="text/markdown",
            use_container_width=True,
        )
    elif not generate_btn:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">📝</div>
                <div style="font-weight: 600; color: #f1f5f9; margin-bottom: 0.3rem;">No Study Guide Generated Yet</div>
                <div class="empty-state-text">Upload a picture of your handwritten notes, blackboard, or book on the left, then click <b>Generate Study Guide</b> to get an instant AI breakdown.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )