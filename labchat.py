import streamlit as st
import openai
import os
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import difflib
import re

# === Load API Key ===
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Page Setup ===
st.set_page_config(page_title="LabChat", layout="centered")
st.title("🧿 LabChat — Your Smart Lab Assistant 🧿")

# === Load built-in dataset ===
DATASET_PATH = "data.csv"
try:
    df = pd.read_csv(DATASET_PATH)
    st.session_state.df = df
    st.success("✅ Internal dataset loaded successfully.")
    st.write("📊 Preview of data:", df.head())
except Exception as e:
    st.session_state.df = None
    st.error(f"⚠️ Could not load dataset: {e}")

# === Initialize chat memory ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": (
            "You are LabChat — a helpful assistant trained to answer questions and analyze workplace data. "
            "You also have access to a built-in dataset. "
            "If the user mentions any value or column from the dataset, return the rest of the row that matches. "
            "Otherwise, reply using general AI knowledge."
        )}
    ]

# === Display chat history ===
for msg in st.session_state.messages[1:]:
    speaker = "🧑 You" if msg["role"] == "user" else "🤖 Bot"
    st.markdown(f"**{speaker}:** {msg['content']}")

# === Chat history export ===
if len(st.session_state.messages) > 1:
    if st.button("📥 Download Chat History"):
        chat_text = "\n".join([
            f"You: {m['content']}" if m["role"] == "user" else f"Bot: {m['content']}"
            for m in st.session_state.messages[1:]
        ])
        st.download_button("Save as .txt", chat_text, file_name="chat_history.txt")

# === Chat input field ===
prompt = st.chat_input("Ask me something")
if prompt:
    st.session_state.pending_user_input = prompt
    st.rerun()

# === Dataset search function ===
def try_dataset_lookup(user_input):
    df = st.session_state.get("df", None)
    if df is None:
        return None

    matches = re.findall(r'\b[\w.-]+\b', user_input.lower())
    best_hits = []

    for col in df.columns:
        for word in matches:
            col_vals = df[col].astype(str).str.lower()
            if word in col.lower() or word in col_vals.values:
                matched_rows = df[df[col].astype(str).str.lower() == word]
                if not matched_rows.empty:
                    for _, row in matched_rows.iterrows():
                        best_hits.append(row.to_dict())

    if best_hits:
        results = [", ".join(f"{k}: {v}" for k, v in row.items()) for row in best_hits]
        return "\n\n".join(results)
    return None

# === Process message ===
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
