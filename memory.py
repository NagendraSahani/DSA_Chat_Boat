import sqlite3
from langchain_community.chat_message_histories import ChatMessageHistory

DB_NAME = "chat_memory.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT,
            content TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()

store = {}


def get_session_history(session_id: str):
    if session_id not in store:
        history = ChatMessageHistory()

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT role, content FROM chat_history WHERE username=?",
            (session_id,)
        )

        rows = cursor.fetchall()
        conn.close()

        for role, content in rows:
            if role == "human":
                history.add_user_message(content)
            else:
                history.add_ai_message(content)

        store[session_id] = history

    return store[session_id]


def save_message(username, role, content):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO chat_history (username, role, content) VALUES (?, ?, ?)",
        (username, role, content)
    )

    conn.commit()
    conn.close()


def clear_history(username):
    if username in store:
        del store[username]

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM chat_history WHERE username=?",
        (username,)
    )

    conn.commit()
    conn.close()


def show_history(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT role, content FROM chat_history WHERE username=?",
        (username,)
    )

    rows = cursor.fetchall()
    conn.close()

    return rows


def list_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT DISTINCT username FROM chat_history"
    )

    users = [row[0] for row in cursor.fetchall()]
    conn.close()

    return users


def delete_account(username):
    if username in store:
        del store[username]

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM chat_history WHERE username=?",
        (username,)
    )

    conn.commit()
    conn.close()


def admin_view_history(username):
    return show_history(username)


def save_history(session_id):
    pass