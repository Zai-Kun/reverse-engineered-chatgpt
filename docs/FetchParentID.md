## Explanation of 'parent_id'

The 'parent_id' is the ID of the last message in the chat. We use it to inform the server that we're replying to the previous message. This means that if we are creating a new chat, the 'parent_id' is not necessary.

### How to fetch 'parent_id' from an existing conversation

We can fetch the chat with the 'conversation_id,' and the ID of the last message in the chat will be our 'parent_id.'

Here is an example:

```python
import asyncio
import sys

from re_gpt import ChatGPT

conversation_id = "YOUR_CONVERSATION_ID"  # The 'conversation_id' will be found in the chat's url: 'https://chat.openai.com/c/conversation_id'

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
