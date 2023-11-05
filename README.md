
<div align="center">
  <a href="https://github.com/Zai-Kun/reverse-engineered-chatgpt">  </a>

<h1 align="center">Reverse Engineered <a href="https://openai.com/blog/chatgpt">ChatGPT</a> API</h1>

  <p align="center">
    Use OpenAI ChatGPT in your Python code without an API key

[![Stargazers][stars-badge]][stars-url]
[![Forks][forks-badge]][forks-url]
[![Discussions][discussions-badge]][discussions-url]
[![Issues][issues-badge]][issues-url]
[![MIT License][license-badge]][license-url]

  </p>
    <p align="center">
    <a href="https://github.com/Zai-Kun/reverse-engineered-chatgpt"></a>
    <a href="https://github.com/Zai-Kun/reverse-engineered-chatgpt/issues">Report Bug</a>
    |
    <a href="https://github.com/Zai-Kun/reverse-engineered-chatgpt/discussions">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#inspiration">Inspiration</a></li>
        <li><a href="#how-it-works">How it works</a></li>
        <li><a href="#built-using">Built using</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#obtaining-session-token">Obtaining Session Token</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a>
        <ul>
        <li><a href="#example-usage">Example Usage</a></li>
        </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

## About The Project

This project can be used to integrate OpenAI's ChatGPT services into your python code. You can use this project to prompt ChatGPT for responses directly from python, without using an official API key.

This can be useful if you want to use ChatGPT API without a [ChatGPT Plus](https://openai.com/blog/chatgpt-plus) account.

### Inspiration

ChatGPT has an official API which can be used to interface your Python code to it, but it needs to be used with an API key. This API key can only be obtained if you have a [ChatGPT Plus](https://openai.com/blog/chatgpt-plus) account, which requires $20/month (as of 05/11/2023). But you can use ChatGPT for free, using the [ChatGPT web interface](https://chat.openai.com/). This project aims to interface your code to ChatGPT web version so you can use ChatGPT in your Python code without using an API key.

### How it works

[ChatGPT](https://chat.openai.com/) web interface's requests have been reverse engineered, and directly integrated into Python requests. Hence, any requests made using this script is a simulated as a request made by a user directly on the website. Hence, it is free and needs no API key.

### Built Using

* [![Python][python-badge]][python-url]
* [![curl_cffi][curl-cffi-badge]][curl-cffi-url]

## Getting Started

### Prerequisites

* Python >= 3.9

### Installation

1. Clone the repo

   ```sh
   git clone https://github.com/Zai-Kun/reverse-engineered-chatgpt.git
   ```

2. Copy the `re_chatgpt` directory into into your project directory.

   ```sh
   cp -r reverse-engineered-chatgpt/re_chatgpt <your_project_directory>
   ```

3. Create a Python virtual environment in your project's directory

    ```sh
    cd <your_project_directory>
    python -m venv .venv
    ```

4. Activate the virtual environment

    ```sh
    source .venv/bin/activate
    ```

5. Install the pip packages from `requirements.txt` of `reverse-engineered-chatgpt` directory in your project directory's environment

    ```sh
    pip install -r ../reverse-engineered-chatgpt/requirements.txt
    ```

### Obtaining Session Token

1. Go to <https://chat.openai.com/chat> and log in or sign up.
2. Open the developer tools in your browser.
3. Go to the `Application` tab and open the `Cookies` section.
4. Copy the value for `__Secure-next-auth.session-token` and save it.

## Usage

Refer [example_usage.py](https://github.com/Zai-Kun/reverse-engineered-chatgpt/blob/dev/example_usage.py) for the guide on using the library.

### Example usage

```python
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


async def main():
    async with ChatGPT(
        session_token=session["token"],
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
```

## Roadmap

* [ ] Add better error handling.
* [ ] Implement a function to retrieve all ChatGPT chats.
* [ ] Improve documentation.

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request.
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the Apache License 2.0. See [`LICENSE`](https://github.com/Zai-Kun/reverse-engineered-chatgpt/blob/main/LICENSE
) for more information.

## Contact

Zai-Kun - [Discord Server](https://discord.gg/ymcqxudVJG)

Repo Link: <https://github.com/Zai-Kun/reverse-engineered-chatgpt>

## Acknowledgments

* [sudoAlphaX](https://github.com/sudoAlphaX)

* [yifeikong (curl-cffi module)](https://github.com/yifeikong/curl_cffi)

* [acheong08 (implementation to obtain arkose_token)](ht tps://github.com/acheong08/funcaptcha)

* [pyca (cryptography module)](https://github.com/pyca/cryptography/)

* [hajimes (mmh3 module)](https://github.com/hajimes/mmh3)

* [Legrandin (pycryptodome module)](https://github.com/Legrandin/pycryptodome/)

* [othneildrew (README Template)](https://github.com/othneildrew)

<!-- MARKDOWN LINKS & IMAGES -->
[forks-badge]: https://img.shields.io/github/forks/Zai-Kun/reverse-engineered-chatgpt
[forks-url]: https://github.com/Zai-Kun/reverse-engineered-chatgpt/network/members
[stars-badge]: https://img.shields.io/github/stars/Zai-Kun/reverse-engineered-chatgpt
[stars-url]: https://github.com/Zai-Kun/reverse-engineered-chatgpt/stargazers
[issues-badge]: https://img.shields.io/github/issues/Zai-Kun/reverse-engineered-chatgpt
[issues-url]: https://github.com/Zai-Kun/reverse-engineered-chatgpt/issues
[discussions-badge]: https://img.shields.io/github/discussions/Zai-Kun/reverse-engineered-chatgpt
[discussions-url]: https://github.com/Zai-Kun/reverse-engineered-chatgpt/discussions
[python-badge]: https://img.shields.io/badge/Python-blue?logo=python&logoColor=yellow
[python-url]: https://www.python.org/
[curl-cffi-url]: https://github.com/aio-libs/curl-cffi
[curl-cffi-badge]: https://img.shields.io/badge/curl__cffi-green
[license-badge]: https://img.shields.io/github/license/Zai-Kun/reverse-engineered-chatgpt
[license-url]: https://github.com/Zai-Kun/reverse-engineered-chatgpt/blob/main/LICENSE
