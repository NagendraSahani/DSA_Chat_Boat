from langchain_community.chat_message_histories import ChatMessageHistory

store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


def clear_history(session_id):
    if session_id in store:
        del store[session_id]


def show_history(session_id):
    history = get_session_history(session_id)

    chats = []
    for msg in history.messages:
        if msg.type == "human":
            chats.append(msg.content)

    return chats


def save_history(session_id):
    pass


def list_users():
    return list(store.keys())


def delete_account(session_id):
    if session_id in store:
        del store[session_id]


def admin_view_history(username):
    if username not in store:
        return []

    chats = []
    for msg in store[username].messages:
        if msg.type == "human":
            chats.append(msg.content)

    return chats