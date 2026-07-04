import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.runnables.history import RunnableWithMessageHistory

from memory import (
    get_session_history,
    clear_history,
    show_history,
    save_history,
    list_users,
    delete_account,
    admin_view_history,
    save_message
)

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"
TEMPERATURE = 0.3
ADMIN_PASSWORD = "admin1317"

st.set_page_config(
    page_title="LeetCode AI Mentor",
    page_icon="🤖",
    layout="wide"
)

# ------------------------
# Session State
# ------------------------
defaults = {
    "logged_in": False,
    "admin": False,
    "username": None,
    "messages": []
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ------------------------
# Load LLM
# ------------------------
@st.cache_resource
def load_llm():
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        st.error("GOOGLE_API_KEY missing")
        st.stop()

    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        google_api_key=api_key
    )

llm = load_llm()

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert DSA mentor. Explain simply with examples."),
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
    st.title("🤖 LeetCode AI Mentor")
    st.caption("Multi User DSA Chatbot")

    tab1, tab2 = st.tabs(["User Login", "Admin Login"])

    with tab1:
        username = st.text_input("Enter Username")

        if st.button("Login"):
            if username.strip():
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.messages = []

                old_chats = show_history(username)
                for role, content in old_chats:
                    role_name = "user" if role == "human" else "assistant"
                    st.session_state.messages.append(
                        {"role": role_name, "content": content}
                    )

                st.rerun()
            else:
                st.warning("Please enter username")

    with tab2:
        password = st.text_input("Admin Password", type="password")

        if st.button("Admin Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin = True
                st.rerun()
            else:
                st.error("Wrong Password")

# ------------------------
# Admin Panel
# ------------------------
elif st.session_state.admin:
    st.title("🛠 Admin Panel")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Show Users"):
            users = list_users()
            st.write(users)

        user_to_view = st.text_input("Enter Username to View History")

        if st.button("View History"):
            chats = admin_view_history(user_to_view)
            st.write(chats)

    with col2:
        delete_user = st.text_input("Delete User")

        if st.button("Delete Account"):
            delete_account(delete_user)
            st.success("Deleted Successfully")

    if st.button("Logout Admin"):
        st.session_state.admin = False
        st.rerun()

# ------------------------
# User Chat
# ------------------------
elif st.session_state.logged_in:
    username = st.session_state.username

    st.title("🤖 LeetCode AI Mentor")
    st.caption(f"Welcome {username}")

    with st.sidebar:
        st.header("⚙ Options")

        if st.button("Show History"):
            st.write(show_history(username))

        if st.button("Clear History"):
            clear_history(username)
            st.session_state.messages = []
            st.success("History Cleared")

        if st.button("Delete Account"):
            delete_account(username)
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.messages = []
            st.rerun()

        if st.button("Logout"):
            save_history(username)
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.messages = []
            st.rerun()

    # Show Chat Messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

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
                    response = chatbot.invoke(
                        {"question": question},
                        config={
                            "configurable": {
                                "session_id": username
                            }
                        }
                    )

                answer = response.content
                st.markdown(answer)

                # Save in SQLite DB
                save_message(username, "human", question)
                save_message(username, "ai", answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as e:
                st.error(f"Error: {str(e)}")