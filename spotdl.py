import discord
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice

from credentials import discord_token, guild_ids


client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the client.

@client.event
async def on_ready():
    print("Ready!")

@slash.slash(name="ping",
             description="Play a round of ping-pong",
             guild_ids=guild_ids)
async def _ping(ctx): 
    await ctx.send(f"Pong! ({client.latency*1000:.1f}ms)", hidden=True)

@slash.slash(name="zsh",
             description="Instructions for users with Zsh terminals",
             guild_ids=guild_ids)
async def _zsh(ctx):
    await ctx.send("aa")

@slash.slash(name="update",
             description="Various update instructions",
             guild_ids=guild_ids,
             options=[
                create_option(
                    name="location",
                    description="Where should the update come from?",
                    option_type=3,
                    required=True,
                    choices=[
                        create_choice(
                            name="pip",
                            value="pip"
                                ),
                        create_choice(
                            name="master",
                            value="master"
                                ),
                        create_choice(
                            name="dev",
                            value="dev"
                                )
                        ]
                        ),
               create_option(
                    name="clean",
                    description="Use pip-autoremove?",
                    option_type=5,
                    required=False
                )
             ]
        )
async def update(ctx, location: str, clean: bool = False):
    msg = ""
    if clean == True:
        msg += f"**Clean installation from `{location}`**\n - `pip install pip-autoremove`\n - `pip-autoremove spotdl -y`\n - `pip cache purge`"
    else:
        msg += f"**Update spotDL from `{location}`**\n - `pip uninstall spotdl`"
    
    if location == "pip":
        msg += "\n - `pip install -U spotdl`"
    elif location in ["dev", "master"]:
        msg += f"\n - `pip install https://codeload.github.com/spotDL/spotify-downloader/zip/{location}`"

    await ctx.send(content=msg)


# async def update(ctx, from: str):
#     await ctx.send("a")

# @slash.slash(name="Various install instructions",
#              description="",
#              guild_ids=guild_ids)
# async def _a(ctx):
#     await ctx.send("")

# @slash.slash(name="",
#              description="",
#              guild_ids=guild_ids)
# async def _a(ctx):
#     await ctx.send("")

client.run(discord_token)