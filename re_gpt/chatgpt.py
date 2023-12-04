import asyncio
import ctypes
import inspect
import json
import os
import sys
import uuid
from typing import AsyncGenerator, Callable, Optional

from curl_cffi.requests import AsyncSession

from .errors import (
    BackendError,
    InvalidSessionToken,
    RetryError,
    TokenNotProvided,
    UnexpectedResponseError,
)
from .utils import get_binary_path

# Constants
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
CHATGPT_API = "https://chat.openai.com/backend-api/{}"
BACKUP_ARKOSE_TOKEN_GENERATOR = "https://arkose-token-generator.zaieem.repl.co/token"


class ChatGPT:
    def __init__(
        self,
        proxies: Optional[dict] = None,
        session_token: Optional[str] = None,
        exit_callback_function: Optional[Callable] = None,
        auth_token: Optional[str] = None,
    ):
        """
        Initializes an instance of the class.

        Args:
            proxies (Optional[dict]): A dictionary of proxy settings. Defaults to None.
            session_token (Optional[str]): A session token. Defaults to None.
            exit_callback_function (Optional[callable]): A function to be called on exit. Defaults to None.
            auth_token (Optional[str]): An authentication token. Defaults to None.
        """
        self.proxies = proxies
        self.exit_callback_function = exit_callback_function

        self.session_token = session_token
        self.auth_token = auth_token
        self.session = None

    async def __aenter__(self):
        self.session = AsyncSession(
            impersonate="chrome110", timeout=99999, proxies=self.proxies
        )
        self.binary_path = await get_binary_path(self.session)

        if self.binary_path:
            self.arkose = ctypes.CDLL(self.binary_path)
            self.arkose.GetToken.restype = ctypes.c_char_p

        if not self.auth_token:
            if self.session_token is None:
                raise TokenNotProvided
            self.auth_token = await self.fetch_auth_token()

        return self

    async def __aexit__(self, *args):
        try:
            if self.exit_callback_function and callable(self.exit_callback_function):
                if not inspect.iscoroutinefunction(self.exit_callback_function):
                    self.exit_callback_function(self)
        finally:
            self.session.close()

    async def fetch_chat(self, conversation_id: str) -> dict:
        """
        Fetches a chat conversation from the API.

        Args:
            conversation_id (str): The ID of the conversation to fetch.

        Returns:
            dict: The JSON response from the API containing the chat conversation.
        """
        url = CHATGPT_API.format(f"conversation/{conversation_id}")
        response = await self.session.get(url=url, headers=self.build_request_headers())

        return response.json()

    async def chat(
        self,
        user_input: str,
        parent_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> AsyncGenerator[dict, None]:
        """
        Asynchronously processes a chat message.

        Args:
            user_input (str): The user's input message.
            parent_id (str, optional): The ID of the parent message, if any. Defaults to None.
            conversation_id (str, optional): The ID of the conversation, if any. Defaults to None.

        Returns:
            Iterator[dict]: An iterator that yields JSON objects representing assistant responses.
        """
        if not conversation_id and not parent_id:
            payload = await self.build_message_payload(user_input, new_chat=True)
        else:
            payload = await self.build_message_payload(
                user_input,
                parent_id=parent_id,
                conversation_id=conversation_id,
                new_chat=False,
            )

        server_response = (
            ""  # To store what the server returned for debugging in case of an error
        )
        error = None
        try:
            full_message = None
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
                            yield decoded_json
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
            error = e

        # raising the error outside the 'except' block to prevent the 'During handling of the above exception, another exception occurred' error
        if error is not None:
            raise UnexpectedResponseError(error, server_response)

    async def send_message(self, payload: dict) -> AsyncGenerator[bytes, None]:
        """
        Send a message payload to the server and receive the response.

        Args:
            payload (dict): Payload containing message information.

        Yields:
            bytes: Chunk of data received as a response.
        """
        response_queue = asyncio.Queue()

        async def perform_request():
            def content_callback(chunk):
                response_queue.put_nowait(chunk)

            url = CHATGPT_API.format("conversation")
            response = await self.session.post(
                url=url,
                headers=self.build_request_headers(),
                json=payload,
                content_callback=content_callback,
            )
            await response_queue.put(None)

        stream_task = asyncio.create_task(perform_request())

        while True:
            chunk = await response_queue.get()
            if chunk is None:
                break
            yield chunk

    async def delete_conversation(self, conversation_id: str) -> dict:
        """
        Delete a conversation.

        Args:
            conversation_id (str): Unique identifier for the conversation.

        Returns:
            Response: HTTP response object.
        """
        url = CHATGPT_API.format(f"conversation/{conversation_id}")
        response = await self.session.patch(
            url=url, headers=self.build_request_headers(), json={"is_visible": False}
        )

        return response.json()

    async def fetch_auth_token(self) -> str:
        """
        Fetch the authentication token for the session.

        Raises:
            InvalidSessionToken: If the session token is invalid.
        """
        url = "https://chat.openai.com/api/auth/session"
        cookies = {"__Secure-next-auth.session-token": self.session_token}

        headers = {
            "User-Agent": USER_AGENT,
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
        response_json = response.json()

        if "accessToken" in response_json:
            return response_json["accessToken"]

        raise InvalidSessionToken

    async def build_message_payload(
        self,
        user_input: str,
        parent_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        new_chat: Optional[bool] = True,
    ) -> dict:
        """
        Build a payload for sending a user message.

        Args:
            user_input (str): User's input message.
            parent_id (str): ID of the parent message if it's a follow-up message.
            conversation_id (str): Unique identifier for the conversation.
            new_chat (bool): Flag indicating whether it's a new chat or continuation.

        Returns:
            dict: Payload containing message information.
        """
        payload = {
            "conversation_mode": {"conversation_mode": {"kind": "primary_assistant"}},
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

    async def build_message_continuation_payload(
        self, conversation_id: str, parent_id: str
    ) -> dict:
        """
        Build a payload for continuing a conversation.

        Args:
            conversation_id (str): Unique identifier for the conversation.
            parent_id (str): ID of the parent message.

        Returns:
            dict: Payload containing message information for continuation.
        """
        payload = {
            "conversation_mode": {"conversation_mode": {"kind": "primary_assistant"}},
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

    async def arkose_token_generator(self) -> str:
        """
        Generate an Arkose token for authentication.

        Returns:
            str: Arkose token.
        """
        if self.binary_path:
            try:
                result = self.arkose.GetToken()
                return ctypes.string_at(result).decode("utf-8")
            except:
                pass

        for _ in range(5):
            response = await self.session.get(BACKUP_ARKOSE_TOKEN_GENERATOR)
            if response.text == "null":
                raise BackendError(error_code=505)
            try:
                return response.json()["token"]
            except:
                await asyncio.sleep(0.7)

        raise RetryError(website=BACKUP_ARKOSE_TOKEN_GENERATOR)

    def build_request_headers(self) -> dict:
        """
        Build headers for HTTP requests.

        Returns:
            dict: Request headers.
        """
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/event-stream",
            "Accept-Language": "en-US",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}",
            "Origin": "https://chat.openai.com",
            "Alt-Used": "chat.openai.com",
            "Connection": "keep-alive",
        }

        return headers

    @staticmethod
    def decode_raw_json(raw_json_data: str) -> dict or bool:
        """
        Decode raw JSON data.

        Args:
            raw_json_data (str): Raw JSON data as a string.

        Returns:
            dict: Decoded JSON data.
        """
        try:
            decoded_json = json.loads(raw_json_data.strip())
            return decoded_json
        except:
            return False
