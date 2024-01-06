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


class UnexpectedResponseError(Exception):
    def __init__(self, original_exception, server_response):
        self.original_exception = original_exception
        self.server_response = server_response
        self.message = f"An unexpected error occurred. Error message: {self.original_exception}.\nThis is what the server returned: {self.server_response}."
        super().__init__(self.message)


class InvalidModelName(Exception):
    def __init__(self, model, avalible_models):
        self.model = model
        self.avalible_models = avalible_models
        self.message = f'"{model}" is not a valid model. Avalible models: {[model for model in avalible_models]}'
        super().__init__(self.message)
