import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# ------------------------
# CONFIG
# ------------------------
MODEL_NAME = "gemini-1.5-flash"
TEMPERATURE = 0.3

st.set_page_config(
    page_title="LeetCode AI Mentor",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 LeetCode AI Mentor")
st.caption("Testing Deployment")

# ------------------------
# LOAD LLM
# ------------------------
@st.cache_resource
def load_llm():
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        st.error("GOOGLE_API_KEY not found!")
        st.stop()

    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        google_api_key=api_key
    )

try:
    llm = load_llm()
    st.success("Gemini Loaded Successfully")
except Exception as e:
    st.error(f"LLM Load Error: {str(e)}")
    st.stop()

# ------------------------
# CHAT HISTORY
# ------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------------
# INPUT
# ------------------------
question = st.chat_input("Ask DSA Question...")

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                response = llm.invoke(question)

            answer = response.content
            st.markdown(answer)

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

        except Exception as e:
            st.error(f"Response Error: {str(e)}")