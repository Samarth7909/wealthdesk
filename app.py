"""
WealthDesk -- Streamlit UI
Run from the wealthdesk/ directory:
    streamlit run app.py
"""
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent / "s01" / "starter"))

import streamlit as st
from wealthdesk.agent import graph

st.set_page_config(page_title="WealthDesk | BNB", page_icon="🏦", layout="centered")
st.title("🏦 WealthDesk")
st.caption("AI Banking Assistant · Bharat National Bank")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about loans, FD rates, or banking services..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = graph.invoke({
                "customer_message": prompt,
                "response": "",
                "history": st.session_state.history,
            })
            reply = result["response"]
            st.session_state.history = result.get("history", st.session_state.history)
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
