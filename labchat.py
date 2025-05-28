import streamlit as st
import openai
import os
from dotenv import load_dotenv
from pathlib import Path

# Debug info (only visible in logs)
print("Running labchat.py from:", os.path.abspath(__file__))

# Load .env file securely
env_path = Path(__file__).resolve().parent / ".env"
print("Looking for .env file at:", env_path)
load_dotenv(dotenv_path=env_path)

# Set API key
openai.api_key = os.getenv("OPENAI_API_KEY")
print("API key loaded:", "Yes" if openai.api_key else "No")

# Streamlit app setup
st.set_page_config(page_title="LabChat", layout="centered")
st.title("🧿  LabChat — Your Smart Lab Assistant 🧿")

# Initialize chat session
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant for our company."}
    ]

# Display chat history
for msg in st.session_state.messages[1:]:
    speaker = "🧑 You" if msg["role"] == "user" else "🤖 Bot"
    st.markdown(f"**{speaker}:** {msg['content']}")

# Chat input box
if prompt := st.chat_input("Ask me something"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.messages
    )

    reply = response.choices[0].message["content"]
    st.session_state.messages.append({"role": "assistant", "content": reply})
