from credentials import discord_token, guild_id
import psutil
import os
import sys
import interactions

# import logging
# logging.basicConfig(level=logging.CRITICAL)

# Set Bot presence
interactions.ClientPresence(
    activities=[
        interactions.PresenceActivity(
            name="over spotDL",
            type=interactions.PresenceActivityType.WATCHING,
        ),
    ],
    status=interactions.StatusType.ONLINE,
)


client = interactions.Client(
    token=discord_token,
    intents=(
        interactions.Intents.ALL),
)

# Load all extensions
extension_list = [filename.replace(".py", "") for filename in os.listdir("extensions") if not filename.startswith("_")]
[client.load(f"extensions.{ext}") for ext in extension_list]


@client.event
async def on_ready():
    # await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="over spotDL"))
    print("Ready!")

client.start()
