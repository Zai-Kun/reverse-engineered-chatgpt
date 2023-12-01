#!/usr/bin/env python3

import asyncio
import sys

from re_gpt import ChatGPT

# --- consts ---
#session_token = "__Secure-next-auth.session-token here"
#conversation_id = "conversation ID here"
#parent_id = "parent ID here"
#
from cred import *
session_token = creds('session_token')
conversation_id = creds('conversation_id')
#parent_id = creds('parent_id')
from get_parent_id import *
parent_id = get_parent_id()
# --------------

class tColor:
    # "\033[38;2;181;76;210m" == rgb(181,76,210)
    reset = '\033[0m'
    red = '\033[91m'
    green = '\033[92m'
    yellow = '\033[93m'
    blue = '\033[94m'
    purple = '\033[38;2;181;76;210m'

# If the Python version is 3.8 or higher and the platform is Windows, set the event loop policy
if sys.version_info >= (3, 8) and sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    # Create an asynchronous ChatGPT instance using the session token from the config file
    async with ChatGPT(session_token=session_token) as chatgpt:
        # Get user input for the chat prompt
        #prompt = input("Enter your prompt: ")
        prompt = input(f"{tColor.purple}You: {tColor.reset}\n")

        # Continue the existing chat using conversation_id and parent_id
        async_chat_stream = chatgpt.chat(
            prompt, conversation_id=conversation_id, parent_id=parent_id
        )

        print(f"{tColor.green}ChatGPT: {tColor.reset}" ) 
        reply = ""

        # Iterate through the messages received from the chat and print it
        async for message in async_chat_stream:
            message = message["message"]["content"]["parts"][0]
            print(message[len(reply) :], end='', flush=True)
            reply = message
    
    print("")

if __name__ == "__main__":
    try:
        while True:
            # Run the asynchronous main function using asyncio.run()
            asyncio.run(main())
    except KeyboardInterrupt:
        exit("")

