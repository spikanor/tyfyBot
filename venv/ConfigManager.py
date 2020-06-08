import os

import exceptions

class ConfigManager:
    def __init__(self):
        # Constants
        self.TWITCH_URL = "https://twitch.tv/"
        self.TWITCH_OAUTH_API = "https://id.twitch.tv/oauth2/token"
        self.TWITCH_OAUTH_VALIDATE = "https://id.twitch.tv/oauth2/validate"
        self.TWITCH_STREAMS_API = "https://api.twitch.tv/helix/streams"
        self.TWITCH_USERS_API = "https://api.twitch.tv/helix/users"

        # Environment variables
        self.MONGODB_TOKEN = os.environ["MONGODB_TOKEN"]
        self.DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
        self.TWITCH_CLIENT_ID = os.environ["TWITCH_CLIENT_ID"]
        self.TWITCH_CLIENT_SECRET = os.environ["TWITCH_CLIENT_SECRET"]
        self.TWITCH_OAUTH_TOKEN = "unset"

    def set_oauth(self, new_token):
        self.TWITCH_OAUTH_TOKEN = new_token
