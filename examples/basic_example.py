from re_gpt import SyncChatGPT

# consts
session_token = "__Secure-next-auth.session-token here"
conversation_id = None # Set it to the conversation ID if you want to continue an existing chat or None to create a new chat


def main():
    # Create an asynchronous ChatGPT instance using the session token from the config file
    with SyncChatGPT(session_token=session_token) as chatgpt:
        # Get user input for the chat prompt
        prompt = input("Enter your prompt: ")

        # Continue the existing chat using conversation_id or create a new chat if conversation_id is none
        if conversation_id:
            conversation = chatgpt.get_conversation(conversation_id)
        else:
            conversation = chatgpt.create_new_conversation()

        last_message = ""
        # Iterate through the messages received from the chatgpt and print it
        for message in conversation.chat(prompt):
            message = message["message"]["content"]["parts"][0]
            print(message[len(last_message) :], flush=True)
            last_message = message


if __name__ == "__main__":
    main()
