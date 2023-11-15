import asyncio
import configparser
import sys

from re_gpt import ChatGPT

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read("config.ini")
chat_session = config["session"]

# If the Python version is 3.8 or higher and the platform is Windows, set the event loop policy
if sys.version_info >= (3, 8) and sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    # Create an asynchronous ChatGPT instance using the session token from the config file
    async with ChatGPT(session_token=chat_session["token"]) as chatgpt:
        # Get user input for the chat prompt
        prompt = input("Enter your prompt: ")

        # Check if a conversation_id exists in the config file
        if chat_session["conversation_id"]:
            # Continue the existing chat using conversation_id and parent_id if available
            raw_reply = chatgpt.chat(
                prompt,
                conversation_id=chat_session["conversation_id"],
                parent_id=chat_session["parent_id"],
            )
        else:
            # Start a new chat if conversation_id is not available
            raw_reply = chatgpt.chat(prompt)

        reply = ""

        # Iterate through the messages received from the chat
        async for message in raw_reply:
            # If it's a new chat, update the conversation_id in the config file
            if not chat_session["conversation_id"]:
                chat_session["conversation_id"] = message["conversation_id"]

            # Update the parent_id in the config file with the ID of the last message in the chat
            if chat_session["parent_id"] != message["message"]["id"]:
                chat_session["parent_id"] = message["message"]["id"]

            # Get the content of the message and update the reply variable
            reply = message["message"]["content"]["parts"][0]

        # Write the updated configuration back to the config file
        with open("config.ini", "w") as file:
            config.write(file)

        # Print the final reply
        print(reply)


if __name__ == "__main__":
    # Run the asynchronous main function using asyncio.run()
    asyncio.run(main())
