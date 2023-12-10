from re_gpt import SyncChatGPT

# consts
session_token = "__Secure-next-auth.session-token here"
conversation_id = None  # Set it to the conversation ID if you want to continue an existing chat or None to create a new chat

# Create ChatGPT instance using the session token
with SyncChatGPT(session_token=session_token) as chatgpt:
    prompt = input("Enter your prompt: ")

    # Continue the existing chat using conversation_id or create a new chat if conversation_id is none
    if conversation_id:
        conversation = chatgpt.get_conversation(conversation_id)
    else:
        conversation = chatgpt.create_new_conversation()

    # Iterate through the messages received from the chatgpt and print it
    for message_chunk in conversation.chat(prompt):
        print(message_chunk["content"], flush=True, end="")
