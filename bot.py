from credentials import discord_token
import os
import interactions

import logging
logging.basicConfig(level=logging.WARNING)


client = interactions.Client(
    token=discord_token,
    intents=(
        interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT
    ),
    presence=interactions.ClientPresence(
        activities=[
            interactions.PresenceActivity(name="over spotDL", type=interactions.PresenceActivityType.WATCHING),
        ],
        status=interactions.StatusType.ONLINE,
    ),
)

# Load all extensions
extension_list = [filename.replace(".py", "") for filename in os.listdir("extensions") if not filename.startswith("_")]
[client.load(f"extensions.{ext}") for ext in extension_list]


@client.event
async def on_ready():
    print("Ready!")

client.start()
