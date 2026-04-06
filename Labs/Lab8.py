import streamlit as st
from openai import OpenAI
import requests
import base64

# --- OpenAI Client ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Shared prompt ---
CAPTION_PROMPT = (
    "Describe the image in at least 3 sentences. "
    "Write five different captions for this image. "
    "Captions must vary in length, minimum one word but be no longer than 2 sentences. "
    "Captions should vary in tone, such as, but not limited to funny, intellectual, and aesthetic."
)

st.title("📸 Image Captioning Bot")
st.write("Upload an image or paste a URL to get a description and creative captions.")

# --- Model Selector (sidebar) ---
MODEL = st.sidebar.selectbox(
    "Choose a model",
    ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1"],
    index=0
)
st.sidebar.caption(f"Currently using: **{MODEL}**")

# =====================
# PART A: Image URL
# =====================
st.header("Option 1: Image URL")
st.caption("URL must link directly to an image (e.g. ending in .jpg, .png).")

if "url_response" not in st.session_state:
    st.session_state.url_response = None

url = st.text_input("Paste an image URL:")

if st.button("Generate Captions from URL") and url:
    with st.spinner("Analyzing image from URL..."):
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": url, "detail": "auto"}},
                    {"type": "text", "text": CAPTION_PROMPT}
                ]
            }]
        )
        st.session_state.url_response = response.choices[0].message.content

if st.session_state.url_response:
    st.image(url, caption="Submitted Image", use_container_width=True)
    st.write(st.session_state.url_response)

st.divider()

# =====================
# PART B: File Upload
# =====================
st.header("Option 2: Upload an Image")

if "upload_response" not in st.session_state:
    st.session_state.upload_response = None

uploaded = st.file_uploader(
    "Choose an image file",
    type=["jpg", "jpeg", "png", "webp", "gif"]
)

if st.button("Generate Captions from Upload") and uploaded:
    with st.spinner("Analyzing uploaded image..."):
        b64 = base64.b64encode(uploaded.read()).decode("utf-8")
        mime = uploaded.type
        data_uri = f"data:{mime};base64,{b64}"

        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_uri, "detail": "low"}},
                    {"type": "text", "text": CAPTION_PROMPT}
                ]
            }]
        )
        st.session_state.upload_response = response.choices[0].message.content

if st.session_state.upload_response:
    if uploaded:
        st.image(uploaded, caption="Uploaded Image", use_container_width=True)
    st.write(st.session_state.upload_response)