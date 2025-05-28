#!/usr/bin/env python
# coding: utf-8

# In[25]:


with open(".env", "w") as f: #automatically writes the API key to a .env file (store environment variables, like api keys)
    f.write("OPENAI_API_KEY=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\n")



# In[35]:


import os #returns current working directory
os.getcwd()


# In[27]:


import streamlit as st
import openai
import os
from dotenv import load_dotenv
from pathlib import Path

#debugging to fix file structure
print("Running labchat.py from:", os.path.abspath(__file__))

env_path = Path(__file__).resolve().parent / ".env"
print("Looking for .env file at:", env_path)

# ✅ Load from that specific path
loaded = load_dotenv(dotenv_path=env_path)
print("load_dotenv() success:", loaded)

# Load API key from .env

api_key = os.getenv("OPENAI_API_KEY")
print("API key from .env:", api_key)  # Debug line
openai.api_key = api_key

# Streamlit page setup
st.set_page_config(page_title="LabChat", layout="centered")
st.title("               🧿  🧿  LabChat 🧿  🧿 ")

# Chat history stored in session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant for our company."}]

# Show previous messages
for msg in st.session_state.messages[1:]:
    speaker = "🧑 You" if msg["role"] == "user" else "🤖 Bot"
    st.markdown(f"**{speaker}:** {msg['content']}")

# Input field
user_input = st.text_input("Type your message:", key="input")

# When user sends a message
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get response from OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.messages
    )

    reply = response.choices[0].message["content"]
    st.session_state.messages.append({"role": "assistant", "content": reply})

    # Refresh the UI to show updated conversation
    st.rerun()



# In[ ]:




