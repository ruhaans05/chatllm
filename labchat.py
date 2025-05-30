import streamlit as st
import openai
import os
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import re

# === Load API Key ===
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Page Setup ===
st.set_page_config(page_title="LabChat", layout="centered")
st.title("🧿 LabChat — Your Smart Lab Assistant 🧿")

# === Load dataset from file ===
DATASET_PATH = "testingtable.csv"
try:
    df = pd.read_csv(DATASET_PATH)
    st.session_state.df = df
    st.success("✅ Dataset loaded successfully from testingtable.csv.")
    st.write("📊 Preview of data:", df.head())
except Exception as e:
    st.session_state.df = None
    st.error(f"⚠️ Could not load dataset: {e}")

# === Initialize chat memory ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": (
            "You are LabChat — a helpful assistant with access to a built-in dataset. "
            "If the user asks for information involving values in the dataset, "
            "search the dataset and return the full matching rows. "
            "If nothing matches, respond normally using general knowledge."
        )}
    ]

# === Display chat history ===
for msg in st.session_state.messages[1:]:
    speaker = "🧑 You" if msg["role"] == "user" else "🤖 Bot"
    st.markdown(f"**{speaker}:** {msg['content']}")

# === Download chat history ===
if len(st.session_state.messages) > 1:
    chat_text = "\n".join([
        f"You: {m['content']}" if m["role"] == "user" else f"Bot: {m['content']}"
        for m in st.session_state.messages[1:]
    ])
    st.download_button("📥 Download Chat History", chat_text, file_name="chat_history.txt", mime="text/plain")

# === Chat input field ===
prompt = st.chat_input("Ask me something")
if prompt:
    st.session_state.pending_user_input = prompt
    st.rerun()

# === Dataset lookup logic ===
def try_dataset_lookup(user_input):
    df = st.session_state.get("df", None)
    if df is None:
        return None

    user_words = set(word.strip().lower() for word in re.findall(r'\b\w+\b', user_input))
    best_hits = []

    for _, row in df.iterrows():
        row_vals = set(str(v).strip().lower() for v in row.values)
        if user_words & row_vals:
            best_hits.append(row.to_dict())

    if best_hits:
        results = [", ".join(f"{k}: {v}" for k, v in row.items()) for row in best_hits]
        return "\n\n".join(results)

    return None

# === Process user message ===
if "pending_user_input" in st.session_state:
    user_message = st.session_state.pending_user_input
    st.session_state.messages.append({"role": "user", "content": user_message})

    dataset_response = try_dataset_lookup(user_message)

    if dataset_response:
        reply = dataset_response
    else:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.messages
        )
        reply = response.choices[0].message["content"]

    st.session_state.messages.append({"role": "assistant", "content": reply})
    del st.session_state.pending_user_input
