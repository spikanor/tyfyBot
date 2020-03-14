import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import requests


# Constants
token = 'Njg4MTQwMzU1NjQ3ODMyMDky.Xmv-tA.HdFiF2oc9HoARLe2dVIwBrR6dDw'
twitch_streams_url = "https://api.twitch.tv/helix/streams"
twitch_users_url = "https://api.twitch.tv/helix/users"

discord_client = commands.Bot(command_prefix='ty!')
mongo_client = MongoClient("mongodb+srv://justinxu:gunsnrosesomg123@cluster0-phv8p.mongodb.net/test?retryWrites=true&w=majority")


# Events
@discord_client.event
async def on_ready():
    print("Ready")

# Commands
@discord_client.command(pass_context=True)
async def twitch_name(ctx, twitch_name=""):
    if (isPrivate(ctx)):
        await ctx.send("Use this command in a server.")
    elif (discord.utils.get(ctx.guild.roles, name="Twitch") not in ctx.message.author.roles):
        await ctx.send("Must have the 'Twitch' role to use this command.")
    else:
        twitch_db = mongo_client[ctx.message.channel.guild.name]["Twitch"]
        discord_name = ctx.message.author.name
        query = {"discord_name": discord_name}
            
        # Set twitch name
        if (twitch_name):
            data = twitch_GET(twitch_users_url, {"login": twitch_name})
            if (not data["data"]):
                await ctx.send("Invalid username.")
            else:
                if (twitch_db.find(query).count() > 0):
                    twitch_db.update_one(query, {"$set": {"twitch_name": twitch_name}})
                    await ctx.send("Updated!")
                else:
                    twitch_db.insert_one({"discord_name" : discord_name, "twitch_name" : twitch_name})
                    await ctx.send("Twitch name is now " + twitch_name + ".")
        # Query twitch name
        else:
            if (twitch_db.find(query).count() > 0):
                twitch_name = twitch_db.find_one(query)["twitch_name"]
                await ctx.send("Your current Twitch username is " + twitch_name + ".")
            else:
                await ctx.send("Twitch name not set.")


# Helpers
def isPrivate(ctx):
    return ctx.message.channel.type == discord.ChannelType.private

def twitch_GET(url, params):
    header = {"Client-ID": 't0fw98983za1rmuv7pfqli0wrta1hd'}
    request = requests.get(url=url, params=params, headers=header)
    return request.json()


discord_client.run(token)