import configparser

from re_gpt import SyncChatGPT

# Load configuration from 'config.ini'
config = configparser.ConfigParser()
config.read("config.ini")
chat_session = config["session"]

# ANSI color codes for console text formatting
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def print_chat(chat):
    """
    Print formatted chat messages to the console.

    Args:
        chat (dict): The chat data.
    """
    for _, message in chat.get("mapping", {}).items():
        if "message" in message and message["message"]["content"]["parts"][0]:
            role = message["message"]["author"]["role"]
            content = message["message"]["content"]["parts"][0]
            print(f"{GREEN if role == 'user' else YELLOW}{role}: {RESET}{content}\n")


def main():
    with SyncChatGPT(
        # proxies=None,  # Optional proxies for network requests
        session_token=chat_session["token"],  # Use the session token for authentication
    ) as chatgpt:
        if chat_session["conversation_id"]:
            conversation = chatgpt.get_conversation(chat_session["conversation_id"])
        else:
            conversation = chatgpt.create_new_conversation()

        # Fetch and print the existing chat
        fetched_chat = conversation.fetch_chat()
        print_chat(fetched_chat)

        while True:
            user_input = input(f"{GREEN}user: {RESET}")
            chat_stream = conversation.chat(user_input)

            print_header = True
            for message in chat_stream:
                # The 'conversation_id' will be empty if it's a new chat, so we assign the new chat's ID
                if not chat_session["conversation_id"]:
                    chat_session["conversation_id"] = message["conversation_id"]

                # print header for the response
                if print_header:
                    print(f"\n{YELLOW}assistant: {RESET}", end="", flush=True)
                    print_header = False

                # Print the ChatGPT's reply
                print(message["content"], end="", flush=True)

            print("\n")

            # Write the new changes back to the config file
            with open("config.ini", "w") as file:
                config.write(file)


if __name__ == "__main__":
    main()

# Note: The 'conversation_id' will be found in the chat's url: 'https://chat.openai.com/c/conversation_id'
