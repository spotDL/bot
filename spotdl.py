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
    await ctx.send('If you use Zsh terminal, **put the URL in quotes**, e.g.\n`spotdl "https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b?si=TNiemvONQviXQpWPSiR2Gw"`')

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
                        create_choice(name="pip", value="pip"),
                        create_choice(name="master", value="master"),
                        create_choice(name="dev",value="dev")
                        ]),
               create_option(
                    name="clean",
                    description="Use pip-autoremove?",
                    option_type=5,
                    required=False
                ),
                create_option(
                    name="force",
                    description="Use --force-reinstall flag?",
                    option_type=5,
                    required=False
                ),
                create_option(
                    name="v3",
                    description="Show pip3 intead of pip?",
                    option_type=5,
                    required=False
                )
             ]
        )

async def update(ctx, location: str, clean: bool = False, force: bool = False, v3: bool = False):
    msg = ""
    if clean == True:
        msg += f"**Clean installation from `{location}`**\n - `pip install pip-autoremove`\n - `pip-autoremove spotdl -y`\n - `pip cache purge`"
    else:
        msg += f"**Update spotDL from `{location}`**\n - `pip uninstall spotdl`"
    
    if location == "pip" and clean == True:
        msg += "\n - `pip install -U spotdl`"
    elif location == "pip":
        msg = "`pip install -U spotdl`"
    elif location in ["dev", "master"]:
        msg += f"\n - `pip install -U https://codeload.github.com/spotDL/spotify-downloader/zip/{location}`"

    if force == True:
        msg = "`pip install -U --force-reinstall spotdl`"

    if v3 == True:
        msg = msg.replace("pip ", "pip3 ")

    await ctx.send(content=msg)

@slash.slash(name="ffmpeg",
             description="",
             guild_ids=guild_ids,
             options=[
                 create_option(
                    name="",
                    description="",
                    option_type=0,
                    required=False,
                    choices=[
                        create_choice(name="", value=""),
                        create_choice(name="", value="")
                    ]
                 )
             ]
             )
async def ffmpeg(ctx, # TODO):
    pass

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