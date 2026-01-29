import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("Document Summarizer")
st.write("Upload a document below and get a summary!")

# Sidebar options
st.sidebar.header("Summary Options")

# Summary type selection
summary_type = st.sidebar.radio(
    "Choose summary format:",
    [
        "100 words",
        "2 connecting paragraphs",
        "5 bullet points"
    ]
)

# Model selection
use_advanced = st.sidebar.checkbox("Use advanced model")
model = "gpt-4o" if use_advanced else "gpt-4o-mini"
st.sidebar.caption(f"Current model: {model}")

# Get API key from secrets
openai_api_key = st.secrets.get("OPENAI_API_KEY")

if openai_api_key:
    client = OpenAI(api_key=openai_api_key)

    # Let the user upload a file
    uploaded_file = st.file_uploader(
        "Upload a document (.txt or .md)", type=("txt", "md")
    )

    # Generate summary button
    if uploaded_file:
        if st.button("Generate Summary"):
            document = uploaded_file.read().decode()
            
            # Build the prompt based on summary type
            if summary_type == "100 words":
                instruction = "Summarize the following document in exactly 100 words."
            elif summary_type == "2 connecting paragraphs":
                instruction = "Summarize the following document in 2 connecting paragraphs."
            else:
                instruction = "Summarize the following document in 5 bullet points."
            
            messages = [
                {
                    "role": "user",
                    "content": f"{instruction}\n\nDocument: {document}",
                }
            ]

            # Generate summary using OpenAI API
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
            )

            st.write_stream(stream)