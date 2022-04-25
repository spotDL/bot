# right click, to create a thread. like https://discord.com/channels/789032594456576001/801461008865951784/967286976497737799

import interactions

from credentials import help_channel, guild_id


class ContextMenu(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

    @interactions.extension_message_command(
        name="Create Help Thread",
        scope=guild_id,
        # TODO add permissions
    )
    async def create_thread(self, ctx):
        """
        Create a new thread in the help_channel then direct the user to it.
        """

        # Create channel object, then create thread
        channel = interactions.Channel(**await self.client._http.get_channel(help_channel), _client=self.client._http)
        thread = await channel.create_thread(name=f"[AUTO] {ctx.target.author.username}'s Help Thread")

        # Add members to thread, send message, then direct user to thread and send confirmation
        await thread.add_member(int(ctx.target.author.id))
        await thread.add_member(int(ctx.author.id))
        await thread.send(
            f"This is a help thread created for {ctx.target.author.mention}. Question as follows\n```{ctx.target.content}```"
        )
        await ctx.send(f"{ctx.target.author.mention}, please redirect to thread {thread.mention}")
        await ctx.send(":white_check_mark: Successfully created thread!", ephemeral=True)


def setup(client):
    ContextMenu(client)
