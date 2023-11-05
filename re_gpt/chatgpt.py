import asyncio
import ctypes
import json
import os
import sys
import uuid

from curl_cffi.requests import AsyncSession

from .encryption_manager import EncryptionManager
from .errors import BackendError, InvalidSessionToken, RetryError, TokenNotProvided
from .utils import get_binary_path


class ChatGPT:
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    CHATGPT_API = "https://chat.openai.com/backend-api/{}"
    BACKUP_ARKOSE_TOKEN_GENERATOR = "https://arkose-token-generator.zaieem.repl.co/token"  # This Repl generates Arkose tokens using 'github.com/acheong08/funcaptcha'

    def __init__(
        self, session_token=None, secure_data_key=None, secure_data_path="./data"
    ):
        self.encryption_manager = EncryptionManager(
            secure_data_key=secure_data_key, secure_data_path=secure_data_path
        )
        self.conversations = self.get_conversations()
        self.session_token = session_token
        self.session = None

    async def __aenter__(self):
        self.session = AsyncSession(impersonate="chrome110", timeout=99999)
        self.binary_path = await get_binary_path(self.session)

        if self.binary_path:
            self.arkose = ctypes.CDLL(self.binary_path)
            self.arkose.GetToken.restype = ctypes.c_char_p

        if "auth_token" not in self.encryption_manager.read_and_decrypt():
            if self.session_token is None:
                raise TokenNotProvided
            await self.update_auth_token(self.session_token)

        return self

    async def __aexit__(self, *args):
        self.session.close()

    async def fetch_chat(
        self, user_id=None, conversation_id=None
    ):  # needs error handeling
        if user_id and not conversation_id:
            if user_id in self.conversations:
                conversation_id = self.conversations[user_id]["conversation_id"]
            else:
                return {}

        url = self.CHATGPT_API.format(f"conversation/{conversation_id}")
        response = await self.session.get(url=url, headers=self.build_request_headers())

        return response.json()

    async def chat(self, user_id, user_input):  # needs error handeling
        if user_id not in self.conversations:
            payload = await self.build_message_payload(user_input, new_chat=True)
            self.conversations[user_id] = {}
        else:
            if (
                "free" in self.conversations[user_id]
                and not self.conversations[user_id]["free"]
            ):
                yield False

            parent_id = self.conversations[user_id]["parent_id"]
            conversation_id = self.conversations[user_id]["conversation_id"]
            payload = await self.build_message_payload(
                user_input,
                parent_id=parent_id,
                conversation_id=conversation_id,
                new_chat=False,
            )
        try:
            self.conversations[user_id]["free"] = False
            full_message = ""
            server_response = ""  # To store what the server returned for debugging in case of an error

            while True:
                response = self.send_message(payload=payload)
                async for chunk in response:
                    decoded_chunk = chunk.decode()

                    server_response += decoded_chunk
                    for line in decoded_chunk.splitlines():
                        if not line.startswith("data: "):
                            continue

                        raw_json_data = line[6:]
                        if not (decoded_json := self.decode_raw_json(raw_json_data)):
                            continue

                        if (
                            "message" in decoded_json
                            and decoded_json["message"]["author"]["role"] == "assistant"
                        ):
                            yield decoded_json["message"]["content"]["parts"][0]
                            full_message = decoded_json
                if (
                    full_message["message"]["metadata"]["finish_details"]["type"]
                    == "max_tokens"
                ):
                    conversation_id = full_message["conversation_id"]
                    parent_id = full_message["message"]["id"]

                    payload = await self.build_message_continuation_payload(
                        conversation_id, parent_id
                    )
                else:
                    break
        except Exception as e:
            print("An unexpected error occurred.")
            print(f"Error message: {e}")
            print(f"This is what the server returned: {server_response}")

            sys.exit(1)

        self.conversations[user_id]["free"] = True
        self.conversations[user_id]["conversation_id"] = full_message["conversation_id"]
        self.conversations[user_id]["parent_id"] = full_message["message"]["id"]
        self.save_conversations()

    async def send_message(self, payload):
        response_queue = asyncio.Queue()

        async def perform_request():
            def content_callback(chunk):
                response_queue.put_nowait(chunk)

            url = self.CHATGPT_API.format("conversation")
            response = await self.session.post(
                url=url,
                headers=self.build_request_headers(),
                json=payload,
                content_callback=content_callback,
            )
            await response_queue.put(None)

            if "Set-Cookie" in response.headers:
                new_cookies = {key: value for key, value in response.cookies.items()}
                self.update_cookies(new_cookies)

        stream_task = asyncio.create_task(perform_request())

        while True:
            chunk = await response_queue.get()
            if chunk is None:
                break
            yield chunk

    async def delete_conversation(self, user_id):  # needs error handeling
        if user_id not in self.conversations:
            return

        conversation_id = self.conversations[user_id]["conversation_id"]
        url = self.CHATGPT_API.format(f"conversation/{conversation_id}")

        response = await self.session.patch(
            url=url, headers=self.build_request_headers(), json={"is_visible": False}
        )

        if "Set-Cookie" in response.headers:
            new_cookies = {key: value for key, value in response.cookies.items()}
            self.update_cookies(new_cookies)

        del self.conversations[user_id]
        self.save_conversations()

    async def update_auth_token(self, session_token):
        url = "https://chat.openai.com/api/auth/session"
        cookies = {"__Secure-next-auth.session-token": session_token}

        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Alt-Used": "chat.openai.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-GPC": "1",
            "Cookie": "; ".join(
                [
                    f"{cookie_key}={cookie_value}"
                    for cookie_key, cookie_value in cookies.items()
                ]
            ),
        }

        response = await self.session.get(url=url, headers=headers)
        if "Set-Cookie" in response.headers:
            new_cookies = {key: value for key, value in response.cookies.items()}
            self.update_cookies(new_cookies)
        response_json = response.json()

        if "accessToken" in response_json:
            self.save_auth_token(response_json["accessToken"])
            return

        raise InvalidSessionToken

    async def build_message_payload(
        self, user_input, parent_id=None, conversation_id=None, new_chat=True
    ):
        payload = {
            "conversation_id": None if new_chat else conversation_id,
            "action": "next",
            "arkose_token": await self.arkose_token_generator(),
            "force_paragen": False,
            "history_and_training_disabled": False,
            "messages": [
                {
                    "author": {"role": "user"},
                    "content": {"content_type": "text", "parts": [user_input]},
                    "id": str(uuid.uuid4()),
                    "metadata": {},
                }
            ],
            "model": "text-davinci-002-render-sha",
            "parent_message_id": str(uuid.uuid4()) if not parent_id else parent_id,
        }

        return payload

    async def build_message_continuation_payload(self, conversation_id, parent_id):
        payload = {
            "action": "continue",
            "arkose_token": await self.arkose_token_generator(),
            "conversation_id": conversation_id,
            "force_paragen": False,
            "history_and_training_disabled": False,
            "model": "text-davinci-002-render-sha",
            "parent_message_id": parent_id,
            "timezone_offset_min": -300,
        }

        return payload

    async def arkose_token_generator(self):  # needs error handeling
        if self.binary_path:
            result = self.arkose.GetToken()
            return ctypes.string_at(result).decode("utf-8")

        for _ in range(5):
            response = await self.session.get(self.BACKUP_ARKOSE_TOKEN_GENERATOR)
            if response.text == "null":
                raise BackendError(error_code=505)
            try:
                return response.json()["token"]
            except:
                await asyncio.sleep(0.7)

        raise RetryError(website=self.BACKUP_ARKOSE_TOKEN_GENERATOR)

    def update_cookies(self, new_cookies):
        data = self.encryption_manager.read_and_decrypt()
        if "cookies" not in data:
            data["cookies"] = new_cookies
        else:
            data["cookies"].update(new_cookies)
        self.encryption_manager.encrypt_and_save(data)

    def save_conversations(self):
        data = self.encryption_manager.read_and_decrypt()
        data["conversations"] = self.conversations

        self.encryption_manager.encrypt_and_save(data)

    def save_auth_token(self, token):
        data = self.encryption_manager.read_and_decrypt()
        data["auth_token"] = token

        self.encryption_manager.encrypt_and_save(data)

    def get_conversations(self):
        data = self.encryption_manager.read_and_decrypt()
        if "conversations" in data:
            return data["conversations"]

        return {}

    def get_auth_token(self):
        return self.encryption_manager.read_and_decrypt()["auth_token"]

    def get_cookies(self):
        return self.encryption_manager.read_and_decrypt()["cookies"]

    def build_request_headers(self):
        cookies = self.get_cookies()

        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "text/event-stream",
            "Accept-Language": "en-US",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.get_auth_token()}",
            "Origin": "https://chat.openai.com",
            "Alt-Used": "chat.openai.com",
            "Connection": "keep-alive",
            "Cookie": "; ".join(
                [
                    f"{cookie_key}={cookie_value}"
                    for cookie_key, cookie_value in cookies.items()
                ]
            ),
        }

        return headers

    @staticmethod
    def decode_raw_json(raw_json_data):
        try:
            decoded_json = json.loads(raw_json_data.strip())
            return decoded_json
        except:
            return False
