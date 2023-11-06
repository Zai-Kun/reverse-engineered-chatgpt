import asyncio
import configparser
import sys

from re_gpt import ChatGPT

config = configparser.ConfigParser()
config.read("config.ini")
session = config["session"]

if sys.version_info >= (3, 8) and sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main(user_input):
    async with ChatGPT(
        session_token=session["token"], secure_data_path=session["data_path"]
    ) as chatgpt:
        raw_reply = chatgpt.chat("random_string", user_input)
        reply = ""

        async for message in raw_reply:
            reply = message

        return reply


if __name__ == "__main__":
    prompt = "Hello"  # Enter your prompt here

    reply = asyncio.run(main(prompt))
    print(reply)
