class TokenNotProvided(Exception):
    def __init__(self):
        super().__init__(
            "Token not provided. Please pass your '__Secure-next-auth.session-token' as an argument (e.g., ChatGPT.init(session_token=YOUR_TOKEN))."
        )


class MissingArkoseTokenError(Exception):
    def __init__(self, response):
        super().__init__(
            f"No 'token' found in the server's response. Here is the response received: {response}"
        )


class InvalidSessionToken(Exception):
    def __init__(self):
        super().__init__("Invalid session token provided.")
