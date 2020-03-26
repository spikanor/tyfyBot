import os
import json
from json import JSONDecodeError

import exceptions

class ConfigManager:
    def __init__(self):
        # Constants
        self.TWITCH_URL = "https://twitch.tv/"
        self.TWITCH_STREAMS_API = "https://api.twitch.tv/helix/streams"
        self.TWITCH_USERS_API = "https://api.twitch.tv/helix/users"

        # Environment variables
        self.MONGODB_TOKEN = os.environ["MONGODB_TOKEN"]
        self.DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
        self.TWITCH_CLIENT_ID = os.environ["TWITCH_CLIENT_ID"]
