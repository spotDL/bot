import interactions

from credentials import guild_id


class Commands(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

    @interactions.extension_command(
        name="ping",
        description="Ping spotDL's Bot!",
        scope=guild_id,
    )
    async def ping(self, ctx):
        await ctx.send(f"Pong! ({self.client.latency:.0f}ms)")

    # NOTE Admin command not yet enabled since interactions.py does not yet support commands for only some users, since discord has not yet released perms v2.
    # @interactions.extension_command(
    #     name="admin",
    #     description="Administration Commands",
    #     scope=guild_id,
    # )


def setup(client):
    Commands(client)
