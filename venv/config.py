import json
from json import JSONDecodeError

class config:
    config_path = "config.json"

    def __init__(self):
        try:
            with open(self.config_path, 'r') as config_file:
                self.config = json.load(config_file)
        except ValueError and JSONDecodeError:
            print("Invalid JSON file")
            exit(0)
        except FileNotFoundError:
            print("config.json not found")
            exit(0)

        print(json.dumps(self.config, indent=4, sort_keys=True))

        # Constants
        self.TOKEN = self.config["token"]
        self.TWITCH_URL = self.config["twitch_links"]["twitch_url"]
        self.TWITCH_STREAMS_API = self.config["twitch_links"]["twitch_streams_api"]
        self.TWITCH_USERS_API = self.config["twitch_links"]["twitch_users_api"]


        # from config.json
        self.LIVE_STREAMS_CHANNEL = "live-streams"
        self.TWITCH_STREAMER_ROLE = "Twitch Streamer"
        self.ADMIN_ROLE = "admin"