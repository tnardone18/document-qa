import streamlit as st
from openai import OpenAI

# show title and description
st.title("My Lab3 Question Answering Chatbot")

openAI_model = st.sidebar.selectbox("Which Model?", ("mini", "regular"))
if openAI_model == "mini":
    model_to_use = "gpt-4o-mini"
else:
    model_to_use = "gpt-4o"

# define the system prompt
SYSTEM_PROMPT = {
    "role": "system",
    "content": """You are a helpful question answering assistant. Your job is to get the user's question and answer it clearly and accurately.

IMPORTANT: Explain everything in simple terms that a 10 year old child can understand. Use easy words, short sentences, and fun examples when possible. Avoid jargon or complicated language.

After answering any question, always ask: "Do you want more info?"

If the user responds with "Yes", "yes", "yeah", "sure", "please", or any affirmative response:
- Provide additional details, examples, or related information about the previous topic
- Keep the explanation simple enough for a 10 year old
- Then ask again: "Do you want more info?"

If the user says "No", "no", "nope", or any negative response:
- Say something friendly like "Okay, no problem!"
- Then ask: "What else can I help you with?" to go back to the start"""
}

# create an OpenAI client
if 'client' not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I help you?"}
    ]

# display all messages in the chat history
for msg in st.session_state.messages:
    chat_msg = st.chat_message(msg["role"])
    chat_msg.write(msg["content"])

if prompt := st.chat_input("What is your question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # create buffered messages for API call
    # ALWAYS start with system prompt (never buffered out)
    buffered_messages = [SYSTEM_PROMPT]
    
    # add initial greeting
    buffered_messages.append(st.session_state.messages[0])
    
    # get the last 4 messages (2 user + 2 assistant exchanges)
    recent_messages = st.session_state.messages[1:]
    if len(recent_messages) > 4:
        recent_messages = recent_messages[-4:]
    
    buffered_messages.extend(recent_messages)
    
    client = st.session_state.client
    stream = client.chat.completions.create(
        model=model_to_use,
        messages=buffered_messages,
        stream=True
    )
    
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    
    st.session_state.messages.append({"role": "assistant", "content": response})