import json
from json import JSONDecodeError

import exceptions

class ConfigManager:
    config_path = "config.json"
    def __init__(self):
        try:
            with open(self.config_path, 'r') as config_file:
                self.config = json.load(config_file)
        except ValueError and JSONDecodeError:
            print("Invalid JSON file")
            exit(1)
        except FileNotFoundError:
            print("config.json not found")
            exit(1)

        # Constants
        self.TOKEN = self.config["token"]
        self.TWITCH_URL = self.config["twitch_links"]["twitch_url"]
        self.TWITCH_STREAMS_API = self.config["twitch_links"]["twitch_streams_api"]
        self.TWITCH_USERS_API = self.config["twitch_links"]["twitch_users_api"]


    def get_role(self, guild, role):
        return self.config_get(guild, "roles", role)

    def get_channel(self, guild, channel):
        return self.config_get(guild, "channels", channel)

    def config_get(self, guild, group, element):
        if guild in self.config["guilds"] and \
                group in self.config["guilds"][guild] and \
                element in self.config["guilds"][guild][group]:
            return self.config["guilds"][guild][group][element]
        else:
            try:
                return self.config["guilds"]["default"][group][element]
            except KeyError:
                # Handle not found in default
                raise

    def update_config_json(self):
        try:
            with open(self.config_path, 'w') as config_file:
                self.config = json.dump(self.config, config_file, indent=2)
        except ValueError and JSONDecodeError:
            print("Invalid JSON file")
            exit(1)
        except FileNotFoundError:
            print("config.json not found")
            exit(1)
