# Reverse-engineered ChatGPT

ChatGPT web version in Python. Basically, you can use the ChatGPT API for free without any limitations, just as in the web version.

## How to use it in your projects

Clone the repo and just copy and paste the 're_chatgpt' directory into your projects where you want to use it.

## Example usage

```python
import sys, asyncio
from re_gpt import ChatGPT

# colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'

# it will not work on windows without this
if sys.version_info >= (3, 8) and sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def print_chat(chat):
    for key, message in chat.get("mapping", {}).items():
        if "message" in message and message["message"]["content"]["parts"][0]:
            role = message["message"]["author"]["role"]
            content = message["message"]["content"]["parts"][0]
            print(f"{GREEN if role == 'user' else YELLOW}{role}: {RESET}{content}\n")

async def main():
    async with ChatGPT(session_token="__Secure-next-auth.session-token here") as chatgpt:
        print_chat(await chatgpt.fetch_chat("random_string"))
        
        while True:
            user_input = input(f"{GREEN}user: {RESET}")
            reply = chatgpt.chat("random_string", user_input) # random string that will be assigned to the actual conversation id

            last_message = ""
            print()
            async for message in reply:
                message = f"{YELLOW}assistant: {RESET}" + message
                print(message[len(last_message) :], end="", flush=True)
                last_message = message
            print("\n")

        # await chatgpt.delete_conversation("random_string") # you can delete a convo with this

if __name__ == "__main__":
    asyncio.run(main())
```
Remember to replace session_token in `ChatGPT(session_token="__Secure-next-auth.session-token here")` with your token

## Obtaining the session token

1. Go to https://chat.openai.com/chat and log in or sign up.
2. Open the developer tools in your browser.
3. Go to the `Application` tab and open the `Cookies` section.
4. Copy the value for `__Secure-next-auth.session-token` and save it.

## Bugs report/contact me.
Join my discord server: https://discord.gg/ymcqxudVJG
