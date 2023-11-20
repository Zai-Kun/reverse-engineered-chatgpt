## Parent ID

### What is a 'parent_id'?

The 'parent_id' is the ID of the last message in the chat. We use it to inform the server that we're replying to the previous message. This means that if we are creating a new chat, the 'parent_id' is not necessary.

### How to fetch 'parent_id' from an existing conversation

We can fetch the chat with the 'conversation_id,' and the ID of the last message in the chat will be our 'parent_id.'

Here is an example:

```python
import asyncio
import sys

from re_gpt import ChatGPT

conversation_id = "YOUR_CONVERSATION_ID"

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
    async with ChatGPT(
        session_token="__Secure-next-auth.session-token here"
    ) as chatgpt:
            fetched_chat = await chatgpt.fetch_chat(conversation_id)
            parent_id = get_last_msg_id(fetched_chat)

            print(f"'parent_id' of '{conversation_id}' is: {parent_id}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Conversation ID

### What is 'conversation_id'

The 'conversation_id' refers to the unique identifier assigned to a specific chat conversation.

### How to Obtain 'conversation_id'

There are two methods for obtaining the 'conversation_id':

1. Retrieve from the URL:

You can find the 'conversation_id' directly from the URL. For example:
```
https://chat.openai.com/c/534dcdc9-22ff-49e7-9bd1-8f77b7c51dd6
```
In this example, '534dcdc9-22ff-49e7-9bd1-8f77b7c51dd6' is the 'conversation_id'.

2. Create a New Chat and Fetch it:

Another way to obtain the 'conversation_id' is by creating a new chat and fetching it programmatically. Here is an example:
```python
import asyncio
import sys

from re_gpt import ChatGPT

# consts
session_token = "__Secure-next-auth.session-token here"

# If the Python version is 3.8 or higher and the platform is Windows, set the event loop policy
if sys.version_info >= (3, 8) and sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    # Create an asynchronous ChatGPT instance using the session token from the config file
    async with ChatGPT(session_token=session_token) as chatgpt:
        prompt = "hi"

        # Not passing the 'conversation_id' and 'parent_id' will create a new chat
        async_chat_stream = chatgpt.chat(prompt)

        async for message in async_chat_stream:
            conversation_id = message["conversation_id"]
            parent_id = message["message"]["id"]
            break

        print(f"New chat's convo ID: {conversation_id}")
        print(f"Reply message ID ('parent_id' for our next message): {parent_id}")


if __name__ == "__main__":
    # Run the asynchronous main function using asyncio.run()
    asyncio.run(main())
```