import os
import json
from json import JSONDecodeError

import exceptions

class ConfigManager:
    guild_data_path = "venv/guilds.json"
    def __init__(self):
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        while os.path.basename(self.ROOT_DIR) != "tyfyBot":
            self.ROOT_DIR = os.path.dirname(self.ROOT_DIR)
        try:
            with open(os.path.join(self.ROOT_DIR, self.guild_data_path), 'r') as guild_file:
                self.guild_data = json.load(guild_file)
        except ValueError and JSONDecodeError:
            print("Invalid JSON file")
            exit(1)
        except FileNotFoundError:
            print("guilds.json not found")
            exit(1)

        # Constants
        self.TWITCH_URL = "https://twitch.tv/"
        self.TWITCH_STREAMS_API = "https://api.twitch.tv/helix/streams"
        self.TWITCH_USERS_API = "https://api.twitch.tv/helix/users"

        # Environment variables
        self.MONGODB_TOKEN = os.environ["MONGODB_TOKEN"]
        self.DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
        self.TWITCH_CLIENT_ID = os.environ["TWITCH_CLIENT_ID"]


    def get_role(self, guild, role):
        return self.guild_data_get(str(guild.id), "roles", role)

    def get_channel(self, guild, channel):
        return self.guild_data_get(str(guild.id), "channels", channel)

    def guild_data_get(self, guild_id, group, element):
        if guild_id in self.guild_data and \
                group in self.guild_data[guild_id] and \
                element in self.guild_data[guild_id][group]:
            return self.guild_data[guild_id][group][element]
        else:
            try:
                return self.guild_data["default"][group][element]
            except KeyError:
                # Handle not found in default
                raise

    def update_guild_data(self):
        try:
            with open(self.guild_data_path, 'w') as config_file:
                self.guild_data = json.dump(self.guild_data, config_file, indent=2)
        except ValueError and JSONDecodeError:
            print("Invalid JSON file")
            exit(1)
        except FileNotFoundError:
            print("guilds.json not found")
            exit(1)
