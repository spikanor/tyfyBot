import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import requests
import asyncio
import bson
from bson import ObjectId
import string

import ConfigManager
import DBManager
import exceptions

# Objects
config = ConfigManager.ConfigManager()
db = DBManager.DBManager(config.MONGODB_TOKEN)
discord_client = commands.Bot(command_prefix='ty!')


# Events
@discord_client.event
async def on_ready():
    print("--Ready--")

@discord_client.event
async def check_twitch_live():
    await discord_client.wait_until_ready()
    while not discord_client.is_closed():
        streamers = db.get_all_streamers()
        for streamer in streamers:
            data = twitch_get(config.TWITCH_STREAMS_API, {"user_login" : streamer["twitch_name"]})
            try:
                if data["data"] and not streamer["is_live"]:
                    streamer_guild = discord_client.get_guild(int(streamer["guild_id"]))
                    streamer_member = streamer_guild.get_member_named(streamer["discord_name"])
                    streams_channel = discord.utils.get(streamer_guild.text_channels, name=db.get_guild_channel(streamer_guild, "live_streams"))
                    if streams_channel:
                        db.set_live(streamer["twitch_name"], streamer["guild_id"], True)
                        print(streamer_member.name + " from guild '" + streamer_guild.name + "' is now live")
                        await streams_channel.send(streamer_member.mention + " is now live at " + config.TWITCH_URL + streamer["twitch_name"]
                                                   + subscriber_mention(streamer_guild, streamer_member))
                    else:
                        print(db.get_guild_channel(streamer_guild, "live_streams" + " not found."))
                elif not data["data"] and streamer["is_live"]:
                        streamer_guild = discord_client.get_guild(int(streamer["guild_id"]))
                        print(streamer["twitch_name"] + " in guild " + streamer_guild.name + " just went offline.")
                        db.set_live(streamer["twitch_name"], streamer["guild_id"], False)
            except KeyError:
                continue
        await asyncio.sleep(20)


# Commands
@discord_client.command(pass_context=True)
async def twitchname(ctx, twitch_name=""):
    if is_private(ctx):
        await ctx.send("Use this command in a server.")
    elif not has_role(ctx.message.author, db.get_guild_role(ctx.guild, "twitch_streamer")):
        await ctx.send("Must have the '" + db.get_guild_role(ctx.guild, "twitch_streamer") + "' role to use this command.")
    else:
        if not is_clean_input(twitch_name):
            await ctx.send("Please enter ASCII characters only.")
            return
        guild_id = ctx.guild.id
        discord_name = str(ctx.message.author)

        # Set twitch name
        if twitch_name:
            data = twitch_get(config.TWITCH_USERS_API, {"login": twitch_name})
            if not data["data"]:
                await ctx.send("Invalid username.")
            else:
                if db.set_twitchname(discord_name, guild_id, twitch_name):
                    await ctx.send("Updated!")
                else:
                    await ctx.send("Twitch name is now " + twitch_name + ".")
        # Query twitch name
        else:
            twitch_name = db.get_twitchname(discord_name, guild_id)
            if twitch_name:
                await ctx.send("Your current Twitch username is " + twitch_name + ".")
            else:
                await ctx.send("Twitch name not set.")

# @discord_client.command(pass_context=True)
# async def set_role(ctx, role, role_name):
#     if is_private(ctx):
#         await ctx.send("Must use command in server.")
#     elif not (role):
#         await ctx.send("Please enter a role to set.")
#     elif

@discord_client.command(pass_context=True, rest_is_raw=True)
async def pasta(ctx, *, new_pasta):
    if is_private(ctx):
        await ctx.send("Must use command in server.")
    elif new_pasta:
        if not is_clean_input(new_pasta):
            await ctx.send("Please enter ASCII characters only.")
        elif not has_role(ctx.message.author, db.get_guild_role(ctx.guild, "pasta_master")):
            await ctx.send("Must have '" + db.get_guild_role(ctx.guild, "pasta_master") + "' role to use this command.")
        else:
            db.add_pasta(new_pasta, ctx.guild.id)
            await ctx.send("New pasta added.")
    else:
        random_pasta = db.get_random_pasta(ctx.guild.id)
        if random_pasta == -1:
            await ctx.send("Pasta DB empty.")
        else:
            await ctx.send(random_pasta["text"] + "\n" + block_text("ID: " + str(random_pasta["_id"])))

@discord_client.command(pass_context=True)
async def rm_pasta(ctx, pasta_id=""):
    if is_private(ctx):
        await ctx.send("Must use command in server.")
    elif not pasta_id:
        await ctx.send("Please provide a pasta ID.")
    elif not has_role(ctx.message.author, db.get_guild_role(ctx.guild, "pasta_master")):
        await ctx.send("Must have '" + db.get_guild_role(ctx.guild, "pasta_master") + "' role to use this command.")
    else:
        deleted = db.remove_pasta_by_id(pasta_id, ctx.guild.id)
        if deleted == -1:
            await ctx.send("Invalid ID.")
        elif deleted == 0:
            await ctx.send("Pasta ID not found.")
        else:
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
    elif not has_role(ctx.message.author, db.get_guild_role(ctx.guild, "admin")):
        await ctx.send("Must have '" + db.get_guild_role(ctx.guild, "admin") + "' role to use this command.")
    else:
        await ctx.send("**CY@**")
        config.update_guild_data()
        await discord_client.close()


# Helpers
def is_private(ctx):
    return ctx.message.channel.type == discord.ChannelType.private

def has_role(member, role_name):
    return get_role(member, role_name) in member.roles

def get_role(guild, role_name):
    return discord.utils.get(guild.roles, name=role_name)

def subscriber_mention(streamer_guild, streamer_member):
    if has_role(streamer_member, db.get_guild_role(streamer_guild, "guild_streamer")):
        twitch_sub_role = db.get_guild_role(streamer_guild, "twitch_subscriber")
        if twitch_sub_role == "everyone":
            twitch_sub_mention = "@everyone"
        elif has_role(streamer_guild, twitch_sub_role):
            twitch_sub_mention = get_role(streamer_guild, twitch_sub_role).mention
        else:
            return ""
        return "\n" + twitch_sub_mention
    return ""

def twitch_get(url, params):
    header = {"Authorization": "Bearer " + "config.TWITCH_OAUTH_TOKEN", "Client-ID": config.TWITCH_CLIENT_ID}
    request = requests.get(url=url, params=params, headers=header)
    return request.json()

def is_clean_input(input_string):
    return len(input_string) == len(input_string.encode('utf-8').decode('utf-8'))

def block_text(text):
    return "`" + text + "`"


discord_client.loop.create_task(check_twitch_live())
discord_client.run(config.DISCORD_TOKEN)