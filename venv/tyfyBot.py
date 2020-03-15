import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import requests
import asyncio


# Constants
TOKEN = 'REMOVED'
TWITCH_URL = "https://twitch.tv/"
TWITCH_STREAMS_URL = "https://api.twitch.tv/helix/streams"
TWITCH_USERS_URL = "https://api.twitch.tv/helix/users"

LIVE_STREAMS_CHANNEL = "live-streams"
TWITCH_STREAMER_ROLE = "Twitch Streamer"
ADMIN_ROLE = "admin"

mongo_client = MongoClient("mongodb+srv://justinxu:gunsnrosesomg123@cluster0-phv8p.mongodb.net/test?retryWrites=true&w=majority")
twitch_db = mongo_client["tyfyBot"]["Twitch"]
discord_client = commands.Bot(command_prefix='ty!')


# Events
@discord_client.event
async def on_ready():
    print("\tReady")

@discord_client.event
async def check_twitch_live():
    await discord_client.wait_until_ready()
    while not discord_client.is_closed():
        streamers = twitch_db.find({})
        for streamer in streamers:
            data = twitch_GET(TWITCH_STREAMS_URL, {"user_login" : streamer["twitch_name"]})
            query = {"twitch_name" : streamer["twitch_name"], "guild_id" : streamer["guild_id"]}
            print("Searching for " + streamer["twitch_name"] + " in guild " + discord_client.get_guild(streamer["guild_id"]).name + "...")
            if (data["data"] and not streamer["is_live"]):
                twitch_db.update_one(query, {"$set": {"is_live": True}})
                streamer_guild = discord_client.get_guild(streamer["guild_id"])
                streamer_member = streamer_guild.get_member_named(streamer["discord_name"])
                streams_channel = discord.utils.get(streamer_guild.text_channels, name=LIVE_STREAMS_CHANNEL)
                if (streams_channel):
                    await streams_channel.send(streamer_member.mention + " is now live at " + TWITCH_URL + streamer["twitch_name"])
            elif (not data["data"] and streamer["is_live"]):
                twitch_db.update_one(query, {"$set": {"is_live": False}})
        print("\t\tsleeping...")
        await asyncio.sleep(5)


# Commands
@discord_client.command(pass_context=True)
async def twitch_name(ctx, twitch_name=""):
    if (is_private(ctx)):
        await ctx.send("Use this command in a server.")
    elif (not has_role(ctx, TWITCH_STREAMER_ROLE)):
        await ctx.send("Must have the '" + TWITCH_STREAMER_ROLE + "' role to use this command.")
    else:
        if (not is_clean_input(twitch_name)):
            await ctx.send("Please enter ASCII characters only.")
            return
        guild_id = ctx.message.channel.guild.id
        discord_name = str(ctx.message.author)
        query = {"discord_name": discord_name, "guild_id" : guild_id}

        # Set twitch name
        if (twitch_name):
            data = twitch_GET(TWITCH_USERS_URL, {"login": twitch_name})
            if (not data["data"]):
                await ctx.send("Invalid username.")
            else:
                if (twitch_db.find(query).count() > 0):
                    twitch_db.update_one(query, {"$set": {"twitch_name": twitch_name}})
                    await ctx.send("Updated!")
                else:
                    twitch_db.insert_one({"discord_name" : discord_name, "twitch_name" : twitch_name,
                                          "guild_id" : guild_id, "is_live" : False})
                    await ctx.send("Twitch name is now " + twitch_name + ".")
        # Query twitch name
        else:
            if (twitch_db.find(query).count() > 0):
                twitch_name = twitch_db.find_one(query)["twitch_name"]
                await ctx.send("Your current Twitch username is " + twitch_name + ".")
            else:
                await ctx.send("Twitch name not set.")

@discord_client.command(pass_context=True)
async def close(ctx):
    if (is_private(ctx)):
        await ctx.send("Must use command in server.")
    elif (not has_role(ctx, ADMIN_ROLE)):
        await ctx.send("Must have '" + ADMIN_ROLE + "' to use this command.")
    else:
        await ctx.send("**CY@**")
        await discord_client.close()

# Helpers
def is_private(ctx):
    return ctx.message.channel.type == discord.ChannelType.private

def has_role(ctx, role_name):
    return discord.utils.get(ctx.guild.roles, name=role_name) in ctx.message.author.roles

def twitch_GET(url, params):
    header = {"Client-ID": 't0fw98983za1rmuv7pfqli0wrta1hd'}
    request = requests.get(url=url, params=params, headers=header)
    return request.json()

def is_clean_input(inputString):
    return len(inputString) == len(inputString.encode())


discord_client.loop.create_task(check_twitch_live())
discord_client.run(TOKEN)