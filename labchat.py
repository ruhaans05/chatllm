import streamlit as st
import openai
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env for local testing
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Load API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Page config
st.set_page_config(page_title="LabChat", layout="centered")
st.title("🧿  LabChat — Your Smart Lab Assistant 🧿")

# Initialize chat state
if "messages" not in st.session_state:
    st.session_state.messages = [
    {"role": "system", "content": (
        "You are LabChat — an intelligent, helpful assistant trained to support users with workplace tasks, questions, and ideas. "
        "Stay friendly and professional, but speak naturally — like a sharp coworker, not a robot. "
        "Aim to make every reply feel useful, productive, and tied to work context — even if subtly. "
        "Avoid repeating the same phrases or format across replies. Be helpful without over-explaining or sounding scripted. "
        "Do not constantly say your name unless asked; instead, weave in your purpose and role naturally."
    )}


]


# Display chat history
for msg in st.session_state.messages[1:]:
    speaker = "🧑 You" if msg["role"] == "user" else "🤖 Bot"
    st.markdown(f"**{speaker}:** {msg['content']}")

# Chat input field
prompt = st.chat_input("Ask me something")

# Store prompt for next rerun
if prompt:
    st.session_state.pending_user_input = prompt
    st.rerun()

# Handle stored prompt
if "pending_user_input" in st.session_state:
    user_message = st.session_state.pending_user_input
    st.session_state.messages.append({"role": "user", "content": user_message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.messages
        
    )

    reply = response.choices[0].message["content"]
    st.session_state.messages.append({"role": "assistant", "content": reply})

    del st.session_state.pending_user_input
