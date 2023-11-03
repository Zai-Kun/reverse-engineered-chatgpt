class TokenNotProvided(Exception):
    def __init__(self):
        self.message = "Token not provided. Please pass your '__Secure-next-auth.session-token' as an argument (e.g., ChatGPT.init(session_token=YOUR_TOKEN))."
        super().__init__(self.message)


class InvalidSessionToken(Exception):
    def __init__(self):
        self.message = "Invalid session token provided."
        super().__init__(self.message)


class RetryError(Exception):
    def __init__(self, website, message="Exceeded maximum retries"):
        self.website = website
        self.message = f"{message} for website: {website}"
        super().__init__(self.message)


class BackendError(Exception):
    def __init__(self, error_code):
        self.error_code = error_code
        self.message = (
            f"An error occurred on the backend. Error code: {self.error_code}"
        )
        super().__init__(self.message)
