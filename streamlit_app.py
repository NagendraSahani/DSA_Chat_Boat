import streamlit as st
from dotenv import load_dotenv
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI

from config import *
from prompt import SYSTEM_PROMPT
from memory import (
    get_session_history,
    clear_history,
    show_history,
    save_history,
    list_users,
    delete_account,
    admin_view_history
)

load_dotenv()

# ------------------------
# Page Config
# ------------------------
st.set_page_config(
    page_title="LeetCode AI Mentor",
    page_icon="🤖",
    layout="wide"
)

# ------------------------
# Custom CSS
# ------------------------
st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: bold;
    color: #4CAF50;
}
.subtitle {
    font-size: 18px;
    color: gray;
}
</style>
""", unsafe_allow_html=True)

# ------------------------
# Session State
# ------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "admin" not in st.session_state:
    st.session_state.admin = False

if "username" not in st.session_state:
    st.session_state.username = None

# ------------------------
# LLM
# ------------------------
import os

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    temperature=TEMPERATURE,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

chain = prompt | llm

chatbot = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history",
)

# ------------------------
# Login Page
# ------------------------
if not st.session_state.logged_in and not st.session_state.admin:
    st.markdown('<p class="main-title">🤖 LeetCode AI Mentor</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Master DSA with AI Guidance</p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["User Login", "Admin Login"])

    with tab1:
        username = st.text_input("Username")
        if st.button("Login"):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()

    with tab2:
        password = st.text_input("Admin Password", type="password")
        if st.button("Admin Login"):
            if password == "admin123":
                st.session_state.admin = True
                st.rerun()
            else:
                st.error("Wrong password")

# ------------------------
# Admin Panel
# ------------------------
elif st.session_state.admin:
    st.title("🛠 Admin Panel")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Show Users"):
            users = list_users()
            st.write(users)

    with col2:
        user_to_view = st.text_input("Enter username")
        if st.button("View History"):
            chats = admin_view_history(user_to_view)
            st.write(chats)

    with col3:
        delete_user = st.text_input("Delete User")
        if st.button("Delete"):
            delete_account(delete_user)
            st.success("Deleted Successfully")

    if st.button("Logout Admin"):
        st.session_state.admin = False
        st.rerun()

# ------------------------
# User Chat UI
# ------------------------
elif st.session_state.logged_in:

    username = st.session_state.username

    st.title("🤖 LeetCode AI Mentor")
    st.caption(f"Welcome {username}")

    # Sidebar
    with st.sidebar:
        st.header("⚙ Options")

        if st.button("Show History"):
            chats = show_history(username)
            st.write(chats)

        if st.button("Clear History"):
            clear_history(username)
            st.success("History Cleared")

        if st.button("Delete Account"):
            delete_account(username)
            st.session_state.logged_in = False
            st.rerun()

        if st.button("Logout"):
            save_history(username)
            st.session_state.logged_in = False
            st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask any DSA question...")

    if question:
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chatbot.invoke(
                    {"question": question},
                    config={
                        "configurable": {
                            "session_id": username
                        }
                    },
                )

                st.markdown(response.content)

        st.session_state.messages.append(
            {"role": "assistant", "content": response.content}
        )