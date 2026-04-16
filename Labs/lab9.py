import streamlit as st
from openai import OpenAI
import json
import os

# --- API Client ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Page Title ---
st.title("🧠 Chatbot with Long-Term Memory")

# =====================
# PART B: Memory System
# =====================

MEMORY_FILE = "memories.json"

def load_memories():
    """Load memories from JSON file. Returns empty list if file doesn't exist."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_memories(memories):
    """Save a list of memories to the JSON file."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(memories, f, indent=2)

# --- Sidebar: Display Memories ---
st.sidebar.header("🧠 Long-Term Memories")
memories = load_memories()

if memories:
    for i, memory in enumerate(memories, 1):
        st.sidebar.write(f"{i}. {memory}")
else:
    st.sidebar.write("No memories yet. Start chatting!")

if st.sidebar.button("🗑️ Clear All Memories"):
    save_memories([])
    st.rerun()

# =====================
# PART C: Build the Chatbot
# =====================

# --- Model Selection ---
model = st.sidebar.selectbox(
    "Choose a model",
    ["gpt-4o-mini", "gpt-4o"],
    index=0
)

# --- Initialize Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input ---
if user_input := st.chat_input("Say something..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # --- Build system prompt with memories injected ---
    memories = load_memories()
    system_prompt = "You are a friendly and helpful assistant with long-term memory."
    if memories:
        memory_text = "\n".join(f"- {m}" for m in memories)
        system_prompt += (
            "\n\nHere are things you remember about this user from past conversations:\n"
            + memory_text
            + "\n\nUse these memories to personalize your responses when relevant."
        )

    # --- Build messages for LLM ---
    llm_messages = [{"role": "system", "content": system_prompt}]
    llm_messages += st.session_state.messages

    # --- Get LLM Response ---
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=model,
            messages=llm_messages,
            stream=True,
        )
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})

    # --- Extract New Memories ---
    extraction_prompt = f"""Analyze the following conversation exchange and extract any new facts about the user worth remembering (e.g., name, preferences, interests, location, major, hobbies, etc.).

User said: "{user_input}"
Assistant replied: "{response}"

Here are the memories already saved (do NOT duplicate these):
{json.dumps(memories)}

Return ONLY a JSON list of new facts as strings. If there are no new facts, return an empty list [].
Example: ["User's name is Alice", "User likes hiking"]
Do not include any other text, just the JSON list."""

    try:
        extraction_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": extraction_prompt}],
        )
        new_facts_text = extraction_response.choices[0].message.content.strip()
        # Clean potential markdown code fences
        new_facts_text = new_facts_text.replace("```json", "").replace("```", "").strip()
        new_facts = json.loads(new_facts_text)

        if new_facts and isinstance(new_facts, list):
            memories.extend(new_facts)
            save_memories(memories)
            st.rerun()
    except (json.JSONDecodeError, Exception) as e:
        # Silently handle parsing errors — memory extraction is best-effort
        pass