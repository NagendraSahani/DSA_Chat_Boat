import os
import json
from langchain_community.chat_message_histories import ChatMessageHistory

MEMORY_DIR = "data/chat_memory"
os.makedirs(MEMORY_DIR, exist_ok=True)

store = {}


def get_session_history(session_id: str):
    if session_id not in store:
        history = ChatMessageHistory()

        file_path = os.path.join(MEMORY_DIR, f"{session_id}.json")

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                messages = json.load(f)

                for msg in messages:
                    if msg["type"] == "human":
                        history.add_user_message(msg["content"])
                    else:
                        history.add_ai_message(msg["content"])

        store[session_id] = history

    return store[session_id]


def save_history(session_id):
    if session_id not in store:
        return

    history = store[session_id]

    data = []
    for msg in history.messages:
        msg_type = "human" if msg.type == "human" else "ai"

        data.append({
            "type": msg_type,
            "content": msg.content
        })

    file_path = os.path.join(MEMORY_DIR, f"{session_id}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def clear_history(session_id):
    if session_id in store:
        del store[session_id]

    file_path = os.path.join(MEMORY_DIR, f"{session_id}.json")

    if os.path.exists(file_path):
        os.remove(file_path)

def show_history(session_id):
    history = get_session_history(session_id)

    if not history.messages:
        return []

    chats = []
    for msg in history.messages:
        if msg.type == "human":
            chats.append(msg.content)

    return chats

def list_users():
    users = []

    for file in os.listdir(MEMORY_DIR):
        if file.endswith(".json"):
            users.append(file.replace(".json", ""))

    return users

def delete_account(session_id):
    if session_id in store:
        del store[session_id]

    file_path = os.path.join(MEMORY_DIR, f"{session_id}.json")

    if os.path.exists(file_path):
        os.remove(file_path)


def admin_view_history(username):
    file_path = os.path.join(MEMORY_DIR, f"{username}.json")

    if not os.path.exists(file_path):
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        messages = json.load(f)

    chats = []
    for msg in messages:
        if msg["type"] == "human":
            chats.append(msg["content"])

    return chats