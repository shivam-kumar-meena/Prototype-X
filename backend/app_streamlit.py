import streamlit as st
import requests
import json

st.set_page_config(page_title="Prototype-X Chatbot", page_icon="🤖", layout="wide")

st.title("💬 Prototype-X AI Assistant")
st.markdown("Built by **Shivam Meena** with ❤️ using Flask + Groq")

st.sidebar.header("Settings")
tone = st.sidebar.selectbox("Select Tone", ["Professional", "Friendly", "Hinglish"])
lang = st.sidebar.selectbox("Language", ["Auto Detect", "English", "Hindi"])

# Chat UI
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

user_input = st.text_input("You:", placeholder="Type your message here...")

if st.button("Send") and user_input.strip():
    # Send to backend (if deployed later on Render/localhost)
    try:
        response = requests.post("https://prototype-x.onrender.com", json={"query": user_input})
        bot_reply = response.json().get("response", "No response from backend.")
    except Exception:
        bot_reply = "⚠️ Backend not reachable. (Will work once deployed!)"

    st.session_state.chat_history.append(("You", user_input))
    st.session_state.chat_history.append(("Bot", bot_reply))

# Show chat history
for role, msg in st.session_state.chat_history:
    if role == "You":
        st.markdown(f"🧑‍💻 **{role}:** {msg}")
    else:
        st.markdown(f"🤖 **{role}:** {msg}")