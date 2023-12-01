#!/usr/bin/env python3

import asyncio
import sys

from re_gpt import ChatGPT

from cred import *

conversation_id = creds('conversation_id')

# Required for Windows compatibility with asyncio
if sys.version_info >= (3, 8) and sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def get_last_msg_id(chat):
    """
    Get the ID of the last message in the chat.

    Args:
        chat (dict): The chat data.

    Returns:
        str: The ID of the last message.
    """
    mapping = chat.get("mapping", {})
    if not mapping:
        return
    last_msg_key = list(mapping)[-1]  # The key is the message ID
    return last_msg_key


async def main():
    async with ChatGPT( session_token=creds('session_token') ) as chatgpt:
            fetched_chat = await chatgpt.fetch_chat(conversation_id)
            parent_id = get_last_msg_id(fetched_chat)
            #print(f"'parent_id' of '{conversation_id}' is: {parent_id}")
            #print(f"{parent_id}")
            return parent_id

if __name__ == "__main__":
    asyncio.run(main())

def get_parent_id():
    return asyncio.run(main())
