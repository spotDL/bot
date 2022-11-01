import disnake
from disnake.ext import commands
import os
import logging
import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN: str = os.getenv("TOKEN", "")

logfile_name = datetime.datetime.now().strftime(
    "%Y-%m-%d %H-%M-%S"
)  # Setting the filename from current date and time

if not os.path.exists("logs"):
    os.mkdir("logs")  # Creating a folder for logs if it doesn't exist

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s %(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filemode="a",
    filename=f".\\logs\\{logfile_name}.log",
)


intents = disnake.Intents.default()
intents.message_content = True

# Set test guild so the bot instantly registers the commands for the spotdl server.
client = commands.InteractionBot(
    intents=intents,
    sync_commands=True,
)


@client.event
async def on_ready():
    # Set presence
    activity = disnake.Activity(name="over spotDL", type=disnake.ActivityType.watching)
    await client.change_presence(activity=activity)

    print("Ready!")


# Load all extensions
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

client.run(TOKEN)
