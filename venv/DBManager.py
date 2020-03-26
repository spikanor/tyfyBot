import pymongo
from pymongo import MongoClient
import random
import bson
from bson import ObjectId

import exceptions

class DBManager:
    def __init__(self, mongodb_token):
        self.mongo_client = MongoClient(mongodb_token)
        self.twitch_db = self.mongo_client["tyfyBot"]["Twitch"]
        self.pasta_db = self.mongo_client["tyfyBot"]["Pastas"]
        self.guilds_db = self.mongo_client["tyfyBot"]["Guilds"]


    # Twitch DB
    def set_twitchname(self, discord_name, guild_id, twitch_name):
        query = {"discord_name": discord_name, "guild_id": guild_id}
        if self.twitch_db.find(query).count() > 0:
            self.twitch_db.update_one(query, {"$set": {"twitch_name": twitch_name}})
            return 1
        else:
            self.twitch_db.insert_one({"discord_name": discord_name, "twitch_name": twitch_name,
                                  "guild_id": guild_id, "is_live": False})
            return 0

    def get_twitchname(self, discord_name, guild_id):
        query = {"discord_name": discord_name, "guild_id": guild_id}
        if self.twitch_db.find(query).count() > 0:
            return self.twitch_db.find_one(query)["twitch_name"]
        else:
            return ""

    def set_live(self, twitch_name, guild_id, is_live):
        query = {"twitch_name" : twitch_name, "guild_id" : guild_id}
        self.twitch_db.update_one(query, {"$set": {"is_live": is_live}})

    def get_all_streamers(self):
        return self.twitch_db.find({})


    # Pasta DB
    def get_random_pasta(self):
        return self.pasta_db.find()[random.randrange(self.pasta_db.count())]

    def remove_pasta_by_id(self, pasta_id):
        try:
            query = {"_id" : ObjectId(pasta_id)}
        except bson.errors.InvalidId:
            return -1

        if self.pasta_db.find(query).count() == 0:
            return 0
        else:
            self.pasta_db.delete_one(query)
            return 1

    def add_pasta(self, pasta_text):
        self.pasta_db.insert_one({"text": pasta_text})


    # Guilds DB
    def guild_data_get(self, guild_id, group, element):
        if self.guilds_db.find({"guild_id": guild_id}).count() > 0:
            guild_data = self.guilds_db.find_one({"guild_id": guild_id})
            if group in guild_data and element in guild_data[group]:
                return guild_data[group][element]
        try:
            return self.guilds_db.find_one({"guild_id": "default"})[group][element]
        except KeyError:
            # Handle not found in default
            raise

    def get_guild_role(self, guild, role):
        return self.guild_data_get(str(guild.id), "roles", role)

    def get_guild_channel(self, guild, channel):
        return self.guild_data_get(str(guild.id), "channels", channel)