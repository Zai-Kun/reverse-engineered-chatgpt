import asyncio
import ctypes
import inspect
import json
import uuid
import re
import websockets
import base64
from typing import AsyncGenerator, Callable, Optional

from curl_cffi.requests import AsyncSession
from .errors import (
    BackendError,
    InvalidSessionToken,
    RetryError,
    TokenNotProvided,
    UnexpectedResponseError,
    InvalidModelName,
)
from .utils import async_get_binary_path, get_model_slug

# Constants
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
CHATGPT_API = "https://chat.openai.com/backend-api/{}"
BACKUP_ARKOSE_TOKEN_GENERATOR = "https://arkose-token-generator.zaieem.repl.co/token"
WS_REGISTER_URL = CHATGPT_API.format("register-websocket")

MODELS = {
    "gpt-4": {"slug": "gpt-4", "needs_arkose_token": True},
    "gpt-3.5": {"slug": "text-davinci-002-render-sha", "needs_arkose_token": False},
}


class AsyncConversation:
    def __init__(self, chatgpt, conversation_id=None, model=None):
        self.chatgpt = chatgpt
        self.conversation_id = conversation_id
        self.parent_id = None
        self.model = model

    async def fetch_chat(self) -> dict:
        """
        Fetches the chat of the conversation from the API.

        Returns:
            dict: The JSON response from the API containing the chat if the conversation_id is not none, else returns an empty dict.

        Raises:
            UnexpectedResponseError: If the response is not a valid JSON object or if the response json is not in the expected format
        """
        if not self.conversation_id:
            return {}

        url = CHATGPT_API.format(f"conversation/{self.conversation_id}")
        response = await self.chatgpt.session.get(
            url=url, headers=self.chatgpt.build_request_headers()
        )

        error = None
        try:
            chat = response.json()
            self.parent_id = list(chat.get("mapping", {}))[-1]
            model_slug = get_model_slug(chat)
            self.model = [
                key for key, value in MODELS.items() if value["slug"] == model_slug
            ][0]
        except Exception as e:
            error = e
        if error is not None:
            raise UnexpectedResponseError(error, response.text)

        return chat

    async def chat(self, user_input: str) -> AsyncGenerator[dict, None]:
        """
        As the name implies, chat with ChatGPT.

        Args:
            user_input (str): The user's input message.

        Yields:
            dict: A dictionary representing assistant responses.

        Returns:
            AsyncGenerator[dict, None]: An asynchronous generator object that yields assistant responses.

        Raises:
            UnexpectedResponseError: If the response is not a valid JSON object or if the response json is not in the expected format
        """

        payload = await self.build_message_payload(user_input)

        server_response = (
            ""  # To store what the server returned for debugging in case of an error
        )
        error = None
        try:
            full_message = None
            while True:
                response = self.send_message(payload=payload) if not self.chatgpt.websocket_mode else self.send_websocket_message(payload=payload)
                async for chunk in response:
                    decoded_chunk = chunk.decode() if isinstance(chunk, bytes) else chunk
                    
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
                            processed_response = self.filter_response(decoded_json)
                            if full_message:
                                prev_resp_len = len(
                                    full_message["message"]["content"]["parts"][0]
                                )
                                processed_response["content"] = processed_response[
                                    "content"
                                ][prev_resp_len::]

                            yield processed_response
                            full_message = decoded_json
                self.conversation_id = full_message["conversation_id"]
                self.parent_id = full_message["message"]["id"]
                if (
                    full_message["message"]["metadata"]["finish_details"]["type"]
                    == "max_tokens"
                ):
                    payload = await self.build_message_continuation_payload()
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
            
            headers = self.chatgpt.build_request_headers()
            # Add Chat Requirements Token
            chat_requriments_token = await self.chatgpt.create_chat_requirements_token()
            if chat_requriments_token:
                headers["openai-sentinel-chat-requirements-token"] = chat_requriments_token

            await self.chatgpt.session.post(
                url=url,
                headers=headers,
                json=payload,
                content_callback=content_callback,
            )
            await response_queue.put(None)

        asyncio.create_task(perform_request())

        while True:
            chunk = await response_queue.get()
            if chunk is None:
                break
            yield chunk
    
    async def send_websocket_message(self, payload: dict) -> AsyncGenerator[str, None]:
        """
        Send a message payload via WebSocket and receive the response.

        Args:
            payload (dict): Payload containing message information.

        Yields:
            str: Chunk of data received as a response.
        """
        await self.chatgpt.ensure_websocket()

        response_queue = asyncio.Queue()
        websocket_request_id = None

        async def perform_request():
            nonlocal websocket_request_id
            
            url = CHATGPT_API.format("conversation")
            headers = self.chatgpt.build_request_headers()
            # Add Chat Requirements Token
            chat_requriments_token = await self.chatgpt.create_chat_requirements_token()
            if chat_requriments_token:
                headers["openai-sentinel-chat-requirements-token"] = chat_requriments_token

            response = (await self.chatgpt.session.post(
                url=url,
                headers=headers,
                json=payload,
            )).json()

            websocket_request_id = response.get("websocket_request_id")
            
            if websocket_request_id is None:
                raise UnexpectedResponseError("WebSocket request ID not found in response", response)
            
            if websocket_request_id not in self.chatgpt.ws_conversation_map:
                self.chatgpt.ws_conversation_map[websocket_request_id] = response_queue
            
        asyncio.create_task(perform_request())

        while True:
            chunk = await response_queue.get()
            if chunk is None:
                break
            yield chunk

        del self.chatgpt.ws_conversation_map[websocket_request_id]
    

    async def build_message_payload(self, user_input: str) -> dict:
        """
        Build a payload for sending a user message.

        Returns:
            dict: Payload containing message information.
        """
        if self.conversation_id and (self.parent_id is None or self.model is None):
            await self.fetch_chat()  # it will automatically fetch the chat and set the parent id

        payload = {
            "conversation_mode": {"conversation_mode": {"kind": "primary_assistant"}},
            "conversation_id": self.conversation_id,
            "action": "next",
            "arkose_token": await self.arkose_token_generator()
            if self.chatgpt.generate_arkose_token
            or MODELS[self.model]["needs_arkose_token"]
            else None,
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
            "model": MODELS[self.model]["slug"],
            "parent_message_id": str(uuid.uuid4())
            if not self.parent_id
            else self.parent_id,
            "websocket_request_id": str(uuid.uuid4())
            if self.chatgpt.websocket_mode
            else None,
        }

        return payload

    async def build_message_continuation_payload(self) -> dict:
        """
        Build a payload for continuing ChatGPT's cut off response.

        Returns:
            dict: Payload containing message information for continuation.
        """
        payload = {
            "conversation_mode": {"conversation_mode": {"kind": "primary_assistant"}},
            "action": "continue",
            "arkose_token": await self.arkose_token_generator()
            if self.chatgpt.generate_arkose_token
            or MODELS[self.model]["needs_arkose_token"]
            else None,
            "conversation_id": self.conversation_id,
            "force_paragen": False,
            "history_and_training_disabled": False,
            "model": MODELS[self.model]["slug"],
            "parent_message_id": self.parent_id,
            "timezone_offset_min": -300,
        }

        return payload

    async def arkose_token_generator(self) -> str:
        """
        Generate an Arkose token.

        Returns:
            str: Arkose token.
        """
        if not self.chatgpt.tried_downloading_binary:
            self.chatgpt.binary_path = await async_get_binary_path(self.chatgpt.session)

            if self.chatgpt.binary_path:
                self.chatgpt.arkose = ctypes.CDLL(self.chatgpt.binary_path)
                self.chatgpt.arkose.GetToken.restype = ctypes.c_char_p

            self.chatgpt.tried_downloading_binary = True

        if self.chatgpt.binary_path:
            try:
                result = self.chatgpt.arkose.GetToken()
                return ctypes.string_at(result).decode("utf-8")
            except:
                pass

        for _ in range(5):
            response = await self.chatgpt.session.get(BACKUP_ARKOSE_TOKEN_GENERATOR)
            if response.text == "null":
                raise BackendError(error_code=505)
            try:
                return response.json()["token"]
            except:
                await asyncio.sleep(0.7)

        raise RetryError(website=BACKUP_ARKOSE_TOKEN_GENERATOR)

    async def delete(self) -> None:
        """
        Deletes the conversation.
        """
        if self.conversation_id:
            await self.chatgpt.delete_conversation(self.conversation_id)

            self.conversation_id = None
            self.parent_id = None

    @staticmethod
    def decode_raw_json(raw_json_data: str) -> dict or bool:
        """
        Decode JSON.

        Args:
            raw_json_data (str): JSON as a string.

        Returns:
            dict: Decoded JSON.
        """
        try:
            decoded_json = json.loads(raw_json_data.strip())
            return decoded_json
        except:
            return False

    @staticmethod
    def filter_response(response):
        processed_response = {
            "content": response["message"]["content"]["parts"][0],
            "message_id": response["message"]["id"],
            "parent_id": response["message"]["metadata"]["parent_id"],
            "conversation_id": response["conversation_id"],
        }

        return processed_response


class AsyncChatGPT:
    def __init__(
        self,
        proxies: Optional[dict] = None,
        session_token: Optional[str] = None,
        exit_callback_function: Optional[Callable] = None,
        auth_token: Optional[str] = None,
        generate_arkose_token: Optional[bool] = False,
        websocket_mode: Optional[bool] = False,
    ):
        """
        Initializes an instance of the class.

        Args:
            proxies (Optional[dict]): A dictionary of proxy settings. Defaults to None.
            session_token (Optional[str]): A session token. Defaults to None.
            exit_callback_function (Optional[callable]): A function to be called on exit. Defaults to None.
            auth_token (Optional[str]): An authentication token. Defaults to None.
            generate_arkose_token (Optional[bool]): Toggle whether to generate and send arkose-token in the payload. Defaults to False.
            websocket_mode (Optional[bool]): Toggle whether to use WebSocket for chat. Defaults to False.
        """
        self.proxies = proxies
        self.exit_callback_function = exit_callback_function

        self.arkose = None
        self.binary_path = None
        self.tried_downloading_binary = False
        self.generate_arkose_token = generate_arkose_token

        self.session_token = session_token
        self.auth_token = auth_token
        self.session = None
        
        self.websocket_mode = websocket_mode
        self.ws_loop = None
        self.ws_conversation_map = {}

    async def __aenter__(self):
        self.session = AsyncSession(
            impersonate="chrome110", timeout=99999, proxies=self.proxies
        )
        if self.generate_arkose_token:
            self.binary_path = await async_get_binary_path(self.session)

            if self.binary_path:
                self.arkose = ctypes.CDLL(self.binary_path)
                self.arkose.GetToken.restype = ctypes.c_char_p

            self.tried_downloading_binary = True

        if not self.auth_token:
            if self.session_token is None:
                raise TokenNotProvided
            self.auth_token = await self.fetch_auth_token()

        if not self.websocket_mode:
           self.websocket_mode = await self.check_websocket_availability()

        if self.websocket_mode:
            await self.ensure_websocket()

        return self

    async def __aexit__(self, *_):
        try:
            if self.exit_callback_function and callable(self.exit_callback_function):
                if not inspect.iscoroutinefunction(self.exit_callback_function):
                    self.exit_callback_function(self)
        finally:
            await self.session.close()

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

    def get_conversation(self, conversation_id: str) -> AsyncConversation:
        """
        Makes an instance of class Conversation and return it.

        Args:
            conversation_id (str): The ID of the conversation to fetch.

        Returns:
            Conversation: Conversation object.
        """

        return AsyncConversation(self, conversation_id)

    def create_new_conversation(
        self, model: Optional[str] = "gpt-3.5"
    ) -> AsyncConversation:
        if model not in MODELS:
            raise InvalidModelName(model, MODELS)
        return AsyncConversation(self, model=model)

    async def delete_conversation(self, conversation_id: str) -> dict:
        """
        Delete a conversation.

        Args:
            conversation_id (str): Unique identifier for the conversation.

        Returns:
            dict: Server response json.
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

        Returns: authentication token.
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

    async def set_custom_instructions(
        self,
        about_user: Optional[str] = "",
        about_model: Optional[str] = "",
        enable_for_new_chats: Optional[bool] = True,
    ) -> dict:
        """
        Set cuteom instructions for ChatGPT.

        Args:
            about_user (str): What would you like ChatGPT to know about you to provide better responses?
            about_model (str): How would you like ChatGPT to respond?
            enable_for_new_chats (bool): Enable for new chats.
        Returns:
            dict: Server response json.
        """
        data = {
            "about_user_message": about_user,
            "about_model_message": about_model,
            "enabled": enable_for_new_chats,
        }
        url = CHATGPT_API.format("user_system_messages")
        response = await self.session.post(
            url=url, headers=self.build_request_headers(), json=data
        )

        return response.json()

    async def retrieve_chats(
        self, offset: Optional[int] = 0, limit: Optional[int] = 28
    ) -> dict:
        params = {
            "offset": offset,
            "limit": limit,
            "order": "updated",
        }
        url = CHATGPT_API.format("conversations")
        response = await self.session.get(
            url=url, params=params, headers=self.build_request_headers()
        )

        return response.json()

    async def check_websocket_availability(self) -> bool:
        """
        Check if WebSocket is available.

        Returns:
            bool: True if WebSocket is available, otherwise False.
        """
        url = CHATGPT_API.format("accounts/check/v4-2023-04-27")
        response = (await self.session.get(
            url=url, headers=self.build_request_headers()
        )).json()
        
        if 'account_ordering' in response and 'accounts' in response:
            account_id = response['account_ordering'][0]
            if account_id in response['accounts']:
                return 'shared_websocket' in response['accounts'][account_id]['features']

        return False
    
    async def ensure_websocket(self):
        if not self.ws_loop:
            ws_url_rsp = (await self.session.post(WS_REGISTER_URL, headers=self.build_request_headers())).json()
            ws_url = ws_url_rsp['wss_url']
            access_token = self.extract_access_token(ws_url)
            self.ws_loop = asyncio.create_task(self.listen_to_websocket(ws_url, access_token))

    def extract_access_token(self, url):
        match = re.search(r'access_token=([^&]*)', url)
        if match:
            return match.group(1)
        else:
            return None
        
    async def listen_to_websocket(self, ws_url: str, access_token: str):
        headers = {'Authorization': f'Bearer {access_token}'}
        async with websockets.connect(ws_url, extra_headers=headers) as websocket:
            while True:
                message = await websocket.recv()
                message_data = json.loads(message)
                body_encoded = message_data.get("body", "")
                ws_id = message_data.get("websocket_request_id", "")
                decoded_body = base64.b64decode(body_encoded).decode('utf-8')
                response_queue = self.ws_conversation_map.get(ws_id)
                if response_queue is None:
                    continue
                if 'title_generation' in decoded_body:
                    # skip
                    continue
                response_queue.put_nowait(decoded_body)
                if '[DONE]' in decoded_body or '[ERROR]' in decoded_body:
                    await response_queue.put(None)
                    continue

    async def create_chat_requirements_token(self):
        """
        Get a chat requirements token from chatgpt server

        Returns:
            str: chat requirements token
        """
        url = CHATGPT_API.format("sentinel/chat-requirements")
        response = await self.session.post(
            url=url, headers=self.build_request_headers()
        )
        body = response.json()
        token = body.get("token", None)
        return token