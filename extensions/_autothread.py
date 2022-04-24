import interactions

from credentials import help_channel

class AutoThread(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

    @interactions.extension_listener()
    async def on_message_create(self, msg):
        # Only AutoThread if message is in the help channel, and msg is not sent by a bot.
        if int(msg.channel_id) == int(help_channel) and not msg.author.bot:
            thread_start_msg = f"""\
{msg.author.mention} Please continue adding more information into this thread.
You should include the following information:
** 
- spotDL Version (e.g. 3.9.5)
- Operating System (e.g. Windows)**
- The actual command you ran, including any Spotify links
- Screenshots or pasted error messages if relevant
"""
            thread = await msg.create_thread(name=f"{msg.author.username}'s Help Thread")
            await thread.send(thread_start_msg)

def setup(client):
    AutoThread(client)
