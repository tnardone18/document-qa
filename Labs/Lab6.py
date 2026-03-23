import streamlit as st
from openai import OpenAI
from pydantic import BaseModel

# --- Page Config ---
st.set_page_config(page_title="Research Agent", page_icon="🔍", layout="centered")

# --- OpenAI Client Setup (Part A, Step 2) ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Session State Initialization ---
if "last_response_id" not in st.session_state:
    st.session_state.last_response_id = None
if "conversation" not in st.session_state:
    st.session_state.conversation = []


# =============================================
# Part D: Structured Output Model (Slide 23-24)
# =============================================
# Pydantic model — SDK handles schema + parsing,
# no manual JSON parsing needed (Slide 23)
class ResearchSummary(BaseModel):
    main_answer: str
    key_facts: list[str]
    source_hint: str


# --- Sidebar Controls ---
st.sidebar.header("Agent Settings")
use_structured = st.sidebar.checkbox("Return structured summary")
use_streaming = st.sidebar.checkbox("Enable streaming")

# --- Main UI ---
st.title("🔍 Research Agent")
st.caption("Powered by the OpenAI Responses API · Web search enabled")

# Display conversation history
for entry in st.session_state.conversation:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])

# --- Chat Input ---
user_question = st.chat_input("Ask a question...")

if user_question:
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_question)
    st.session_state.conversation.append({"role": "user", "content": user_question})

    with st.chat_message("assistant"):

        # ==============================================
        # Part D: Structured Output Mode (Slides 23-24)
        # ==============================================
        # Uses client.responses.parse() instead of .create()
        # Passing text_format=ResearchSummary ensures output shape
        # Pydantic SDK handles schema and parsing — no JSON parsing needed
        if use_structured:
            with st.spinner("Generating structured summary..."):
                response = client.responses.parse(
                    model="gpt-4o",
                    # Slide 19: instructions param sets high-level behavior
                    # It sits above input in the computational hierarchy
                    instructions="You are a helpful research assistant. Cite your sources when using web search.",
                    input=user_question,
                    # Slide 23-24: text_format ensures output matches our Pydantic model
                    text_format=ResearchSummary,
                    # Part C (Slide 7): built-in web search tool
                    tools=[{"type": "web_search_preview"}],
                    # Slide 20: chain via ID — server loads full context
                    previous_response_id=st.session_state.last_response_id,
                )

            # Store ID for next turn (Slide 20)
            st.session_state.last_response_id = response.id

            # Access parsed output directly — no JSON parsing (Slide 23)
            parsed = response.output_parsed
            if parsed:
                st.markdown(parsed.main_answer)
                st.markdown("**Key Facts:**")
                for fact in parsed.key_facts:
                    st.markdown(f"- {fact}")
                st.caption(f"Source hint: {parsed.source_hint}")

                display_text = (
                    f"{parsed.main_answer}\n\n"
                    f"**Key Facts:**\n"
                    + "\n".join(f"- {f}" for f in parsed.key_facts)
                    + f"\n\n*Source hint: {parsed.source_hint}*"
                )
            else:
                fallback = response.output_text
                st.markdown(fallback)
                display_text = fallback

            st.session_state.conversation.append({"role": "assistant", "content": display_text})

        # =======================================
        # Streaming Mode (Slide 21)
        # =======================================
        # Each event is typed and structured
        # Key events: response.output_text.delta, response.completed
        elif use_streaming:
            stream = client.responses.create(
                model="gpt-4o",
                # Slide 19: instructions parameter — above input on hierarchy
                instructions="You are a helpful research assistant. Cite your sources when using web search.",
                input=user_question,
                # Part C: web search built-in tool
                tools=[{"type": "web_search_preview"}],
                # Slide 20: chain to previous response
                previous_response_id=st.session_state.last_response_id,
                stream=True,
            )

            collected_text = ""
            placeholder = st.empty()

            # Slide 21: listen for typed events
            for event in stream:
                # response.output_text.delta — text chunks as they arrive
                if event.type == "response.output_text.delta":
                    collected_text += event.delta
                    placeholder.markdown(collected_text + "▌")
                # response.completed — final event, grab the ID
                elif event.type == "response.completed":
                    st.session_state.last_response_id = event.response.id

            placeholder.markdown(collected_text)
            st.session_state.conversation.append({"role": "assistant", "content": collected_text})

        # ============================================
        # Standard Mode (Parts A + B + C)
        # ============================================
        else:
            with st.spinner("Thinking..."):
                response = client.responses.create(
                    model="gpt-4o",
                    # ---- Slide 19: Instructions Parameter ----
                    # Two ways to set developer instructions:
                    #   1. Via top-level instructions param (used here — takes priority)
                    #   2. Via {"role": "developer", "content": "..."} in the input array
                    # instructions sit above input on the computational hierarchy
                    instructions="You are a helpful research assistant. Cite your sources when using web search.",

                    # ---- Slide 18: Basic Generation ----
                    # Responses API accepts input (string or message array)
                    # instead of the messages array used in Chat Completions
                    input=user_question,

                    # ---- Slide 22: Tools ----
                    # Declare tools in the tools array
                    # Built-in tools (web_search) execute automatically
                    # The model decides whether to call them
                    tools=[{"type": "web_search_preview"}],

                    # ---- Slide 20: Memory / Multi-Turn Chaining ----
                    # Sends an ID instead of full chat history
                    # Server loads full context from all prior turns
                    # None on first turn, then chains automatically
                    previous_response_id=st.session_state.last_response_id,
                )

            # Store the response ID for the next turn (Slide 20)
            # Next call just passes this ID — server already has the rest
            st.session_state.last_response_id = response.id

            # Slide 18: output is direct — response.output_text
            # (vs Chat Completions: response.choices[0].message.content)
            st.markdown(response.output_text)
            st.session_state.conversation.append({"role": "assistant", "content": response.output_text})