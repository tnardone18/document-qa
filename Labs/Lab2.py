import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("My Document Summarizer")
st.write(
    "Upload a document below and get a summary – GPT will generate it for you!")

# Sidebar options
st.sidebar.header("Summary Options")

# Summary type selection
summary_type = st.sidebar.radio(
    "Choose summary format:",
    options=[
        "100 words",
        "2 connecting paragraphs",
        "5 bullet points"
    ]
)

# Model selection
use_advanced = st.sidebar.checkbox("Use advanced model (GPT-4o)")
model = "gpt-4o" if use_advanced else "gpt-4o-mini"
st.sidebar.caption(f"Current model: {model}")

# Define summary instructions based on selection
summary_instructions = {
    "100 words": "Summarize the following document in exactly 100 words. Be concise and capture the main points.",
    "2 connecting paragraphs": "Summarize the following document in exactly 2 connecting paragraphs. The paragraphs should flow naturally from one to the other.",
    "5 bullet points": "Summarize the following document in exactly 5 bullet points. Each bullet point should capture a key idea from the document."
}

# Get API key from secrets
openai_api_key = st.secrets.get("OPENAI_API_KEY")

if not openai_api_key:
    st.error("OpenAI API key not found in secrets.", icon="❌")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader(
        "Upload a document (.txt or .md)", type=("txt", "md")
    )

    if uploaded_file:
        # Add a button to generate summary
        if st.button("Generate Summary", type="primary"):
            # Process the uploaded file
            document = uploaded_file.read().decode()
            
            # Get the appropriate instruction
            instruction = summary_instructions[summary_type]
            
            messages = [
                {
                    "role": "user",
                    "content": f"{instruction}\n\n---\n\nDocument:\n{document}",
                }
            ]

            # Generate summary using the OpenAI API.
            with st.spinner("Generating summary..."):
                stream = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True,
                )

                # Stream the response to the app using `st.write_stream`.
                st.write_stream(stream)