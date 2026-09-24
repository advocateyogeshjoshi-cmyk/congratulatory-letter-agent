import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from PIL import Image
import io

# ------------------------------------------------------------------------------
# 1. Page Configuration
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Congratulatory Letter Agent",
    page_icon="✉️",
    layout="wide"
)

# ------------------------------------------------------------------------------
# 2. Sidebar: AI Provider Settings
# ------------------------------------------------------------------------------
st.sidebar.title("AI Provider Access")

ai_choice = st.sidebar.radio(
    "Select AI Capabilities:",
    options=[
        "Gemini Paid Tier (gemini-3.1-pro-preview)",
        "Gemini Free Tier (gemini-1.5-flash)",
        "Free Open-Source AI (e.g., Mistral 7B via Hugging Face)"
    ]
)

user_api_key = st.sidebar.text_input(
    "Enter API Key (Gemini or Hugging Face token)",
    type="password"
)

st.sidebar.caption("Note: If no key is entered here, the app will fall back to your configured Streamlit Secrets.")

# Resolve API Key setup
api_key = user_api_key or st.secrets.get("GEMINI_API_KEY", "")

if api_key and ("Gemini" in ai_choice):
    genai.configure(api_key=api_key)

# ------------------------------------------------------------------------------
# 3. Input Document Section (Source Clipping / Photo)
# ------------------------------------------------------------------------------
st.title("Congratulatory Letter Agent")

st.subheader("Upload or Capture Source Document")

tab1, tab2 = st.tabs(["📁 Upload or Snap Photo", "📷 Web Camera Feed"])

uploaded_file = None
camera_file = None

with tab1:
    # This uploader triggers the native phone camera selection menu on mobile/tablets
    uploaded_file = st.file_uploader(
        "Browse files or open native camera to snap clipping",
        type=["pdf", "png", "jpg", "jpeg", "txt"],
        key="file_uploader"
    )

with tab2:
    camera_file = st.camera_input("Capture using live web camera feed", key="camera_input")

active_document = uploaded_file or camera_file

if active_document:
    st.success(f"Source Document received: {active_document.name if hasattr(active_document, 'name') else 'Captured Photo'}")

st.write("---")

# ------------------------------------------------------------------------------
# 4. Template & Format Selection (Text or File Upload)
# ------------------------------------------------------------------------------
st.subheader("Congratulatory Letter Template & Format")

tmpl_tab1, tmpl_tab2 = st.tabs(["📝 Text Template", "📁 Upload Template / Letterhead File"])

default_template = """माननीय {name} जी,

आपल्याला [Achievement/Election/Nomination: {achievement}] बद्दल मन:पूर्वक अभिनंदन आणि हार्दिक शुभेच्छा!

आपल्या पुढील वाटचालीस सदिच्छा.

आपला नम्र,
ॲड. योगेश जोशी
जोशी अँड असोसिएट्स, कोल्हापूर"""

with tmpl_tab1:
    st.caption("Use placeholders like {name}, {title}, {achievement}")
    template_text = st.text_area(
        label="Template Text",
        value=default_template,
        height=200,
        label_visibility="collapsed"
    )

template_file = None
with tmpl_tab2:
    st.caption("Upload a custom letterhead image, background template, or reference draft file (PNG, JPG, PDF, DOCX, TXT)")
    template_file = st.file_uploader(
        "Upload Template File / Format",
        type=["png", "jpg", "jpeg", "pdf", "docx", "txt"],
        key="template_file_uploader"
    )
    
    if template_file:
        st.success(f"Template file loaded: {template_file.name}")
        # Preview template image if applicable
        if template_file.type.startswith("image/"):
            image = Image.open(template_file)
            st.image(image, caption="Template / Letterhead Preview", use_container_width=True)

st.write("---")

# ------------------------------------------------------------------------------
# 5. Letter Generation Execution
# ------------------------------------------------------------------------------
if st.button("Generate Letter", type="primary"):
    if not api_key and ("Gemini" in ai_choice):
        st.error("Please enter an API Key in the sidebar or configure it in Streamlit Secrets.")
    elif not active_document:
        st.warning("Please upload a source document or capture a photo first.")
    else:
        st.info("Processing document, applying template format, and generating letter...")
        
        if template_file:
            st.write(f"📌 Using custom template file: **{template_file.name}**")
        else:
            st.write("📌 Using standard text template layout.")
