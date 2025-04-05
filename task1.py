import google.generativeai as genai
import time
from datetime import datetime, timedelta
import streamlit as st

# ========== Configuration ==========
genai.configure(api_key="AIzaSyBs0tJumqCnwjowFa2oWN7b3Y6SVOzSGGY")

# ========== ChatBot Class ==========
class ChatBot:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-pro-latest")
        self.chat = None
        self.last_request_time = datetime.now()
        self.request_delay = timedelta(seconds=3)
        self.initialize_chat()

    def initialize_chat(self):
        if "chat" not in st.session_state:
            st.session_state.chat = self.model.start_chat(history=[])
        self.chat = st.session_state.chat

    def enforce_rate_limit(self):
        elapsed = datetime.now() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep((self.request_delay - elapsed).total_seconds())
        self.last_request_time = datetime.now()

    def get_response(self, user_input):
        try:
            self.enforce_rate_limit()
            response = self.chat.send_message(
                user_input,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=500
                )
            )
            return response.text
        except Exception as e:
            if "quota" in str(e).lower() or "429" in str(e):
                return "⚠️ I've reached my usage limit. Please try again later."
            return f"❌ Error: {str(e)[:100]}..."

# ========== UI Layout ==========
def main():
    st.set_page_config(page_title="💬 AI ChatBot", page_icon="🤖", layout="centered")
    st.markdown("<h2 style='text-align:center;'>🤖 Multilingual ChatBot</h2>", unsafe_allow_html=True)
    st.caption("🗣️ Talk in English or Hindi. Say 'quit' to exit.")

    # Initialize chatbot
    bot = ChatBot()

    # Initialize conversation
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "👋 Hello! How can I assist you today?"}]

    # Display message history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input area
    if user_input := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Exit command
        if user_input.strip().lower() in ["exit", "quit", "bye"]:
            farewell = "👋 Goodbye! Have a wonderful day!"
            st.session_state.messages.append({"role": "assistant", "content": farewell})
            with st.chat_message("assistant"):
                st.markdown(farewell)
            st.stop()

        # Bot response
        with st.spinner("🤔 Thinking..."):
            bot_reply = bot.get_response(user_input)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        with st.chat_message("assistant"):
            st.markdown(bot_reply)

        st.rerun()

# ========== Run ==========
if __name__ == "__main__":
    main()
