import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

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
# 3. Main Interface
# ------------------------------------------------------------------------------
st.title("Congratulatory Letter Agent")

st.subheader("Upload or Capture Document")

# Dual tabs for File Upload and Live Camera Capture
tab1, tab2 = st.tabs(["📁 Browse Files", "📷 Take a Photo"])

uploaded_file = None
camera_file = None

with tab1:
    uploaded_file = st.file_uploader(
        "Browse and upload any document or clipping (Images, PDF, TXT, DOCX, CSV, etc.)",
        type=["pdf", "png", "jpg", "jpeg", "txt"],
        key="file_uploader"
    )

with tab2:
    # st.camera_input triggers browser permission for camera feed
    camera_file = st.camera_input("Capture document using camera", key="camera_input")

# Use whichever input the user provided
active_document = uploaded_file or camera_file

if active_document:
    st.success(f"Document received: {active_document.name if hasattr(active_document, 'name') else 'Captured Photo'}")

st.write("---")

# ------------------------------------------------------------------------------
# 4. Template Area
# ------------------------------------------------------------------------------
default_template = """माननीय {name} जी,

आपल्याला [Achievement/Election/Nomination: {achievement}] बद्दल मन:पूर्वक अभिनंदन आणि हार्दिक शुभेच्छा!

आपल्या पुढील वाटचालीस सदिच्छा.

आपला नम्र,
ॲड. योगेश जोशी
जोशी अँड असोसिएट्स, कोल्हापूर"""

st.subheader("Congratulatory Letter Template")
st.caption("Use placeholders like {name}, {title}, {achievement}")

template_text = st.text_area(
    label="Template Text",
    value=default_template,
    height=220,
    label_visibility="collapsed"
)

# Process Button
if st.button("Generate Letter", type="primary"):
    if not api_key and ("Gemini" in ai_choice):
        st.error("Please enter an API Key in the sidebar or configure it in Streamlit Secrets.")
    elif not active_document:
        st.warning("Please upload a document or capture a photo first.")
    else:
        st.info("Processing document and generating congratulatory letter...")
        # Add your document parsing & Gemini generation code here
