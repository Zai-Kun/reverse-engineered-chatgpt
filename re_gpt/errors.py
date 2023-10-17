class TokenNotProvided(Exception):
    def __init__(self):
        super().__init__("Token not provided. Please pass your '__Secure-next-auth.session-token' as an argument (e.g., ChatGPT.init(session_token=YOUR_TOKEN)).")

