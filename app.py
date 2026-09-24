import urllib.parse
from PIL import Image
import google.generativeai as genai
from pypdf import PdfReader
import requests
import streamlit as st

st.set_page_config(page_title="Congratulatory Letter Agent", layout="wide")
st.title("Congratulatory Letter Agent")

# --- AI Provider Configuration ---
st.sidebar.header("AI Provider Access")
ai_choice = st.sidebar.radio(
    "Select AI Capabilities:",
    [
        "Gemini Paid Tier (gemini-3.1-pro-preview)",
        "Gemini Free Tier (gemini-1.5-flash)",
        "Free Open-Source AI (e.g., Mistral 7B via Hugging Face)",
    ],
)

api_key = st.sidebar.text_input(
    "Enter API Key (Gemini or Hugging Face token)", type="password"
)
st.sidebar.markdown(
    "*Note: If no key is entered here, the app will fall back to your"
    " configured Streamlit Secrets.*"
)

# --- Input Methods (Upload or Camera) ---
st.write("### Upload or Capture Document")
tab1, tab2 = st.tabs(["📁 Browse Files", "📷 Take a Photo"])

with tab1:
  uploaded_file = st.file_uploader(
      "Browse and upload any document or clipping (Images, PDF, TXT, DOCX, CSV,"
      " etc.)",
      type=None,
  )

with tab2:
  camera_photo = st.camera_input(
      "Take a photo of the newspaper clipping directly"
  )

# Determine which file to process (prioritize camera if taken)
active_file = camera_photo if camera_photo is not None else uploaded_file

# --- Template Selection ---
default_template = """माननीय {name} जी,

आपल्याला [Achievement/Election/Nomination: {achievement}] बद्दल मनःपूर्वक अभिनंदन आणि हार्दिक शुभकामना!

आपल्या पुढील वाटचालीस सदिच्छा.

आपला नम्र,
अ‍ॅड. योगेश जोशी
योगेश जोशी अँड असोसिएट्स, कोल्हापूर"""

letter_template = st.text_area(
    "Congratulatory Letter Template (Use placeholders like {name}, {title},"
    " {achievement})",
    value=default_template,
    height=250,
)


def extract_text_from_file(file):
  file_extension = file.name.split(".")[-1].lower() if file.name else "jpg"
  text = ""
  try:
    if file_extension == "pdf":
      reader = PdfReader(file)
      for page in reader.pages:
        text += page.extract_text() or ""
    elif file_extension in ["txt", "csv", "md"]:
      text = file.read().decode("utf-8")
    else:
      text = (
          "Unsupported text format. If this is an image, it will be processed"
          " visually."
      )
  except Exception as e:
    text = f"Error reading file: {e}"
  return text, file_extension


if active_file is not None and st.button("Generate Letter"):
  extracted_text, ext = extract_text_from_file(active_file)

  prompt = f"""
    Analyze the provided document details. Extract the following details:
    1. Recipient Name (name)
    2. Title/Post/Position (title)
    3. Specific Achievement or Election details (achievement)
    
    Fill in the following template with the extracted details in Marathi (or English as appropriate):
    Template:
    {letter_template}
    
    Provide ONLY the final generated letter.
    """

  generated_letter = None
  model_used = ""

  with st.spinner(f"Accessing {ai_choice} to process your file..."):
    try:
      if "Gemini" in ai_choice:
        # Secure API key retrieval via Secrets or Sidebar input
        if api_key:
          genai.configure(api_key=api_key)
        elif "GEMINI_API_KEY" in st.secrets:
          genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        else:
          st.error(
              "Please provide a Gemini API Key in the sidebar or Streamlit"
              " secrets."
          )
          st.stop()

        # Model selection based on user tier choice
        model_name = (
            "gemini-3.1-pro-preview"
            if "Paid" in ai_choice
            else "gemini-1.5-flash"
        )
        model = genai.GenerativeModel(model_name)
        model_used = model_name

        if ext in ["png", "jpg", "jpeg", "webp"]:
          image = Image.open(active_file)
          response = model.generate_content([prompt, image])
          st.image(image, caption="Captured/Uploaded Clipping", width=300)
        else:
          response = model.generate_content(
              f"{prompt}\n\nDocument Text:\n{extracted_text}"
          )

        generated_letter = response.text

      elif "Open-Source AI" in ai_choice:
        if not api_key:
          st.error(
              "Please provide a Hugging Face Access Token in the sidebar for"
              " Free Open-Source AI."
          )
          st.stop()

        if ext in ["png", "jpg", "jpeg", "webp"]:
          st.warning(
              "The current free open-source text model setup does not support"
              " image inputs. Please upload a PDF or TXT file, or switch to a"
              " Gemini vision model."
          )
          st.stop()

        headers = {"Authorization": f"Bearer {api_key}"}
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"

        full_prompt = (
            f"<s>[INST] {prompt}\n\nDocument Text:\n{extracted_text} [/INST]"
        )
        payload = {
            "inputs": full_prompt,
            "parameters": {"max_new_tokens": 500, "temperature": 0.3},
        }

        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
          output = response.json()[0]["generated_text"]
          generated_letter = output.split("[/INST]")[-1].strip()
          model_used = "Mistral-7B"
        else:
          st.error(
              f"Error from Open-Source API: {response.status_code} -"
              f" {response.text}"
          )

    except Exception as e:
      st.error(f"An error occurred during AI processing: {e}")

  # --- Display and Delivery Options ---
  if generated_letter:
    st.success(f"Letter generated successfully using {model_used}!")
    st.subheader("Generated Congratulatory Letter:")
    st.markdown(generated_letter)

    st.write("---")
    st.write("### Delivery Options")

    col1, col2 = st.columns(2)

    # Button 1: Download as Text File
    with col1:
      st.download_button(
          label="📄 Download as Text File",
          data=generated_letter,
          file_name="congratulatory_letter.txt",
          mime="text/plain",
      )

    # Button 2: Share directly to WhatsApp
    with col2:
      encoded_text = urllib.parse.quote(generated_letter)
      whatsapp_url = f"https://wa.me/?text={encoded_text}"
      st.link_button("📱 Share on WhatsApp", whatsapp_url)
