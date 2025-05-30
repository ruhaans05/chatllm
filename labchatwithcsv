import streamlit as st
import openai
import os
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import difflib
import re

# === Load API key from .env or Streamlit secrets ===
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Page config ===
st.set_page_config(page_title="LabChat", layout="centered")
st.title("🧿 LabChat — Your Smart Lab Assistant 🧿")

# === Upload dataset ===
uploaded_file = st.file_uploader("Upload a CSV for LabChat to reference", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state.df = df
    st.success("✅ Dataset uploaded successfully!")
    st.write("Preview of your dataset:", df.head())

# === Initialize chat state ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": (
            "You are LabChat — an intelligent, helpful assistant trained to support users with workplace tasks, questions, and ideas. "
            "You also have access to a dataset the user uploads. If they ask for a value from one column, return the corresponding value from another column in the same row. "
            "If you're not sure, respond normally using your LLM knowledge."
        )}
    ]

# === Display chat history ===
for msg in st.session_state.messages[1:]:
    speaker = "🧑 You" if msg["role"] == "user" else "🤖 Bot"
    st.markdown(f"**{speaker}:** {msg['content']}")

# === Chat input field ===
prompt = st.chat_input("Ask me something")

if prompt:
    st.session_state.pending_user_input = prompt
    st.rerun()

# === Helper: Try simple lookup if user is referencing the dataset ===
def try_dataset_lookup(user_input):
    df = st.session_state.get("df", None)
    if df is None:
        return None

    cols = df.columns.tolist()
    matches = re.findall(r'\b\w+\b', user_input.lower())

    for col in cols:
        for word in matches:
            if word in str(col).lower():
                # Try to extract a numeric or string value
                for val in matches:
                    filtered = df[df[col].astype(str).str.lower() == val.lower()]
                    if not filtered.empty:
                        row = filtered.iloc[0]
                        result = {c: row[c] for c in cols if c != col}
                        return f"Here’s what I found for {col} = {val}:\n" + ", ".join(f"{k}: {v}" for k, v in result.items())
    return None

# === Handle stored prompt ===
if "pending_user_input" in st.session_state:
    user_message = st.session_state.pending_user_input
    st.session_state.messages.append({"role": "user", "content": user_message})

    response_text = try_dataset_lookup(user_message)

    if not response_text:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.messages
        )
        response_text = response.choices[0].message["content"]

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    del st.session_state.pending_user_input
