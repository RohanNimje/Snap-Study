import streamlit as st
import google.generativeai as genai
from PIL import Image

# UI Setup
st.set_page_config(page_title="Snap & Study", page_icon="📚")
st.title("📚 Snap & Study - AI Tutor")
st.write("Upload a photo of your handwritten notes or textbook, and I will summarize it and give you practice questions!")

# API Key (Streamlit Secrets se lega)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.warning("Please add GEMINI_API_KEY to Streamlit Secrets.")

# Image Uploader
uploaded_file = st.file_uploader("Upload Notes (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Your Notes', use_container_width=True)
    
    if st.button("Generate Study Guide ✨"):
        with st.spinner("Reading your notes..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = """
            You are an expert AI tutor. Look at this image of study notes. 
            1. Give a very short summary of the main topics. 
            2. Explain any hard words simply. 
            3. Give me 3 short practice questions to test my knowledge.
            """
            response = model.generate_content([prompt, image])
            st.success("Study Guide Ready!")
            st.write(response.text)