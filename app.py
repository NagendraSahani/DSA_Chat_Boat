from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.runnables.history import RunnableWithMessageHistory

from config import *
from prompt import SYSTEM_PROMPT
from memory import (
    get_session_history,
    save_history,
    clear_history,
    show_history,
    list_users,
    delete_account,
    admin_view_history
)
from logger import logger
from utils.helper import clean_input


# ===========================
# Load Environment Variables
# ===========================
load_dotenv()


# ===========================
# Create LLM
# ===========================
llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    temperature=TEMPERATURE,
    streaming=True,
)


# ===========================
# Create Prompt
# ===========================
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)


# ===========================
# Build Chain
# ===========================
chain = prompt | llm


# ===========================
# Add Memory
# ===========================
chatbot = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history",
)


# ===========================
# Start Application
# ===========================
print(WELCOME_MESSAGE)
current_user = None

logger.info("Application Started")


while True:

    # ===========================
    # LOGIN MENU
    # ===========================
    if current_user is None:
        print("\nCommands: login | admin | exit")
        command = input(">> ").strip().lower()

        if command == "exit":
            print("Goodbye!")
            break

        elif command == "login":
            username = input("Enter username: ").strip()

            if not username:
                username = "guest"

            current_user = username
            print(f"\nWelcome {current_user}!\n")
            logger.info(f"Session Started: {current_user}")

        elif command == "admin":
            password = input("Enter admin password: ").strip()

            if password == "admin123":
                print("\nWelcome Admin")

                while True:
                    print("""
Admin Commands:
1. show users
2. view history
3. delete user
4. logout
                    """)

                    admin_command = input("Admin >> ").strip().lower()

                    # SHOW USERS
                    if admin_command == "show users":
                        users = list_users()

                        if users:
                            print("\nRegistered Users:")
                            for user in users:
                                print("-", user)
                        else:
                            print("No users found.")

                    # VIEW HISTORY
                    elif admin_command == "view history":
                        username = input("Enter username: ").strip()
                        chats = admin_view_history(username)

                        if chats:
                            print(f"\nChat History of {username}:")
                            for i, chat in enumerate(chats, 1):
                                print(f"{i}. {chat}")
                        else:
                            print("No history found or user does not exist.")

                    # DELETE USER
                    elif admin_command == "delete user":
                        username = input("Enter username to delete: ").strip()

                        users = list_users()

                        if username in users:
                            delete_account(username)
                            print(f"{username} deleted successfully.")
                        else:
                            print("User not found.")

                    # LOGOUT
                    elif admin_command == "logout":
                        print("Admin logged out.\n")
                        break

                    else:
                        print("Invalid admin command.")

            else:
                print("Wrong password!")

        else:
            print("Invalid command.")
            continue

    # ===========================
    # CHAT MODE
    # ===========================
    else:
        question = clean_input(input(f"{current_user} : "))

        if not question:
            continue

        # HELP
        if question.lower() == "help":
            print("""
Commands:
help            -> Show commands
show history    -> Show chat history
logout          -> Logout current user
clear           -> Clear chat history
delete account  -> Delete account
exit            -> Close app
            """)
            continue

        # SHOW HISTORY
        if question.lower() == "show history":
            chats = show_history(current_user)

            if chats:
                print("\nChat History:")
                for i, chat in enumerate(chats, 1):
                    print(f"{i}. {chat}")
            else:
                print("No history found.")

            continue

        # DELETE ACCOUNT
        if question.lower() == "delete account":
            confirm = input("Are you sure? (yes/no): ").strip().lower()

            if confirm == "yes":
                delete_account(current_user)
                print("Account deleted successfully.\n")
                current_user = None
            else:
                print("Cancelled.")

            continue

        # LOGOUT
        if question.lower() == "logout":
            save_history(current_user)
            print(f"{current_user} logged out.\n")
            current_user = None
            continue

        # CLEAR HISTORY
        if question.lower() == "clear":
            clear_history(current_user)
            print("Chat history cleared.\n")
            continue

        # EXIT
        if question.lower() == "exit":
            save_history(current_user)
            print("Goodbye!")
            break

        logger.info(f"[{current_user}] Question: {question}")

        try:
            print("\nBot:\n", end="", flush=True)

            full_response = ""

            for chunk in chatbot.stream(
                {"question": question},
                config={
                    "configurable": {
                        "session_id": current_user
                    }
                },
            ):
                if hasattr(chunk, "content"):
                    token = chunk.content

                    if token:
                        print(token, end="", flush=True)
                        full_response += token

                elif isinstance(chunk, str):
                    print(chunk, end="", flush=True)
                    full_response += chunk

            print("\n")

            save_history(current_user)
            logger.info(f"[{current_user}] Response Generated Successfully")

        except Exception as e:
            logger.error(str(e))
            print("\nSomething went wrong.")
            print(e)