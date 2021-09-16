import discord
from discord_slash import SlashCommand

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
    await ctx.send(f"Pong! ({client.latency*1000:.1f}ms)")

@slash.slash(name="",
             description="",
             guild_ids=guild_ids)
async def _test(ctx):
    await ctx.send()

client.run(discord_token)