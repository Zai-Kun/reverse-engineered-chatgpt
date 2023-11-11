import asyncio
import configparser
import sys

from re_gpt import ChatGPT

config = configparser.ConfigParser()
config.read("config.ini")
session = config["session"]

# colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# it will not work on windows without this
if sys.version_info >= (3, 8) and sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def print_chat(chat):
    for key, message in chat.get("mapping", {}).items():
        if "message" in message and message["message"]["content"]["parts"][0]:
            role = message["message"]["author"]["role"]
            content = message["message"]["content"]["parts"][0]
            print(f"{GREEN if role == 'user' else YELLOW}{role}: {RESET}{content}\n")


def exit_callback(self):
    pass  # do something here on exit


async def main():
    async with ChatGPT(
        proxies=None,  # optional
        exit_callback_function=exit_callback,  # optional
        session_token=session["token"],  # your '__Secure-next-auth.session-token' token
        secure_data_path=session[
            "data_path"
        ],  # file path for storing essential information (e.g., cookies, auth token)
    ) as chatgpt:
        print_chat(await chatgpt.fetch_chat("random_string"))

        while True:
            user_input = input(f"{GREEN}user: {RESET}")
            reply = chatgpt.chat(
                "random_string", user_input
            )  # random string that will be assigned to the actual conversation id

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
