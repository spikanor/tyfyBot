import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import requests
import asyncio
import random
import bson
from bson import ObjectId

import ConfigManager
import exceptions

# Objects
config = ConfigManager.ConfigManager()
mongo_client = MongoClient(config.MONGODB_TOKEN)
twitch_db = mongo_client["tyfyBot"]["Twitch"]
pasta_db = mongo_client["tyfyBot"]["Pastas"]
discord_client = commands.Bot(command_prefix='ty!')


# Events
@discord_client.event
async def on_ready():
    print("--Ready--")

@discord_client.event
async def check_twitch_live():
    await discord_client.wait_until_ready()
    while not discord_client.is_closed():
        streamers = twitch_db.find({})
        for streamer in streamers:
            data = twitch_get(config.TWITCH_STREAMS_API, {"user_login" : streamer["twitch_name"]})
            query = {"twitch_name" : streamer["twitch_name"], "guild_id" : streamer["guild_id"]}
            try:
                if data["data"] and not streamer["is_live"]:
                    streamer_guild = discord_client.get_guild(streamer["guild_id"])
                    streamer_member = streamer_guild.get_member_named(streamer["discord_name"])
                    streams_channel = discord.utils.get(streamer_guild.text_channels, name=config.get_channel(streamer_guild, "live_streams"))
                    if streams_channel:
                        twitch_db.update_one(query, {"$set": {"is_live": True}})
                        print(streamer_member.name + " from guild '" + streamer_guild.name + "' is now live")
                        await streams_channel.send(streamer_member.mention + " is now live at " + config.TWITCH_URL + streamer["twitch_name"])
                elif not data["data"] and streamer["is_live"]:
                    twitch_db.update_one(query, {"$set": {"is_live": False}})
            except KeyError:
                continue
        await asyncio.sleep(20)


# Commands
@discord_client.command(pass_context=True)
async def twitchname(ctx, twitch_name=""):
    if is_private(ctx):
        await ctx.send("Use this command in a server.")
    elif not has_role(ctx, config.get_role(ctx.guild, "twitch_streamer")):
        await ctx.send("Must have the '" + config.get_role(ctx.guild, "twitch_streamer") + "' role to use this command.")
    else:
        if not is_clean_input(twitch_name):
            await ctx.send("Please enter ASCII characters only.")
            return
        guild_id = ctx.message.channel.guild.id
        discord_name = str(ctx.message.author)
        query = {"discord_name": discord_name, "guild_id" : guild_id}

        # Set twitch name
        if twitch_name:
            data = twitch_get(config.TWITCH_USERS_API, {"login": twitch_name})
            if not data["data"]:
                await ctx.send("Invalid username.")
            else:
                if twitch_db.find(query).count() > 0:
                    twitch_db.update_one(query, {"$set": {"twitch_name": twitch_name}})
                    await ctx.send("Updated!")
                else:
                    twitch_db.insert_one({"discord_name" : discord_name, "twitch_name" : twitch_name,
                                          "guild_id" : guild_id, "is_live" : False})
                    await ctx.send("Twitch name is now " + twitch_name + ".")
        # Query twitch name
        else:
            if twitch_db.find(query).count() > 0:
                twitch_name = twitch_db.find_one(query)["twitch_name"]
                await ctx.send("Your current Twitch username is " + twitch_name + ".")
            else:
                await ctx.send("Twitch name not set.")

@discord_client.command(pass_context=True)
async def pasta(ctx, new_pasta=""):
    if new_pasta:
        if not is_clean_input(new_pasta):
            await ctx.send("Please enter ASCII characters only.")
        elif not has_role(ctx, config.get_role(ctx.guild, "admin")):
            await ctx.send("Must have '" + config.get_role(ctx.guild, "admin") + "' role to use this command.")
        else:
            pasta_db.insert_one({"text" : new_pasta})
            await ctx.send("New pasta added.")
    else:
        random_pasta = pasta_db.find()[random.randrange(pasta_db.count())]
        await ctx.send(random_pasta["text"] + block_text("ID: " + str(random_pasta["_id"])))

@discord_client.command(pass_context=True)
async def rm_pasta(ctx, pasta_id=""):
    if is_private(ctx):
        await ctx.send("Must use command in server.")
    elif not pasta_id:
        await ctx.send("Please provide a pasta ID.")
    elif not has_role(ctx, config.get_role(ctx.guild, "admin")):
        await ctx.send("Must have '" + config.get_role(ctx.guild, "admin") + "' role to use this command.")
    else:
        try:
            query = {"_id" : ObjectId(pasta_id)}
        except bson.errors.InvalidId:
            await ctx.send("Invalid ID.")
            return
        if pasta_db.find(query).count() == 0:
            await ctx.send("Pasta ID not found.")
        else:
            pasta_db.delete_one(query)
            await ctx.send("Deleted.")

@discord_client.command(pass_context=True)
async def purge(ctx, purge_num = ""):
    try:
        n = int(purge_num)
    except ValueError:
        await ctx.send("Please enter a number.")
        return
    if is_private(ctx):
        await ctx.send("Must use command in server.")
    elif not purge_num:
        await ctx.send("Enter a number to purge.")
    elif n < 0:
        await ctx.send("Please enter a positive number.")
    else:
        purge_list = await ctx.message.channel.purge(limit=int(purge_num) + 1)
        await ctx.send("Purged " + str(len(purge_list)) + " messages.")


@discord_client.command(pass_context=True)
async def nword(ctx):
    if is_private(ctx):
        await ctx.send("Try that shit in a server, I dare you.")
    else:
        try:
            await ctx.send("Later, " + ctx.message.author.name + ".")
            await ctx.message.author.kick(reason="get fucked idiot")
            await discord_client.send_message(ctx.message.author, "get fucked idiot")
        except discord.Forbidden:
            await ctx.send("You'll get away, this time.")

@discord_client.command(pass_context=True)
async def close(ctx):
    if is_private(ctx):
        await ctx.send("Must use command in server.")
    elif not has_role(ctx, config.get_role(ctx.guild, "admin")):
        await ctx.send("Must have '" + config.get_role(ctx.guild, "admin") + "' role to use this command.")
    else:
        await ctx.send("**CY@**")
        config.update_guild_data()
        await discord_client.close()


# Helpers
def is_private(ctx):
    return ctx.message.channel.type == discord.ChannelType.private

def has_role(ctx, role_name):
    return discord.utils.get(ctx.guild.roles, name=role_name) in ctx.message.author.roles

def twitch_get(url, params):
    header = {"Client-ID": config.TWITCH_CLIENT_ID}
    request = requests.get(url=url, params=params, headers=header)
    return request.json()

def is_clean_input(input_string):
    return len(input_string) == len(input_string.encode())

def block_text(text):
    return "`\n" + text + "\n`"


discord_client.loop.create_task(check_twitch_live())
discord_client.run(config.DISCORD_TOKEN)