import streamlit as st
import openai
import os
from dotenv import load_dotenv
from pathlib import Path
import difflib

# === Load API key from .env ===
load_dotenv()  # Looks for .env in the current working directory

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OPENAI_API_KEY not found. Please set it in a .env file.")
else:
    openai.api_key = api_key

# === Page setup ===
st.set_page_config(page_title="LabChat", layout="centered")
st.title("🧿  LabChat — Your Smart Lab Assistant 🧿")

# === Initialize chat state ===
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

# === Display chat history ===
for msg in st.session_state.messages[1:]:
    speaker = "🧑 You" if msg["role"] == "user" else "🤖 Bot"
    st.markdown(f"**{speaker}:** {msg['content']}")

# === Chat input field ===
prompt = st.chat_input("Ask me something")

# === Store prompt for next rerun ===
if prompt:
    st.session_state.pending_user_input = prompt
    st.rerun()

# === Handle stored prompt ===
if "pending_user_input" in st.session_state and api_key:
    user_message = st.session_state.pending_user_input
    st.session_state.messages.append({"role": "user", "content": user_message})

    # Basic greeting detection
    greetings = ["hello", "hi", "hey", "greetings", "yo"]
    user_input_clean = user_message.strip().lower()
    best_match = difflib.get_close_matches(user_input_clean, greetings, n=1, cutoff=0.7)

    if best_match:
        reply = "Welcome to LabChat — your smart assistant for all things work. How can I help today?"
    else:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages
            )
            reply = response.choices[0].message["content"]
        except openai.error.AuthenticationError:
            reply = "❌ OpenAI API authentication failed. Please check your key."
        except Exception as e:
            reply = f"⚠️ Error: {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    del st.session_state.pending_user_input
