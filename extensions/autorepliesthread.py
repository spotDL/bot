import interactions
from credentials import help_channel, team_role_id


class NoOwnerError(Exception):
    """A custom exception class for when there is no owner."""
    pass


class AutoRepliesThread(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

    @interactions.extension_listener()
    async def on_message_create(self, msg):
        # Only process if message is not sent by a bot.
        if not msg.author.bot:

            """AUTOTHREAD SECTION"""
            # Only AutoThread if message is in the help channel
            if int(msg.channel_id) == int(help_channel):
                thread_start_msg = f"""\
{msg.author.mention} Please continue adding more information into this thread.
You should include the following information:
**
- spotDL Version (e.g. 3.9.5)
- Operating System (e.g. Windows)**
- The actual command you ran, including any Spotify links
- Screenshots or pasted error messages if relevant
"""
                # Create Button component for archiving thread
                archive_button = interactions.Button(
                    style=interactions.ButtonStyle.SUCCESS,
                    label="Archive Thread as Resolved",
                    custom_id="archive"
                )

                # Create the thread and send the start message (as above)
                thread = await msg.create_thread(name=f"{msg.author.username}'s Help Thread")
                await thread.send(thread_start_msg, components=archive_button)

            """AUTOREPLIES SECTION"""
            STAFF_PING = """I have detected that you pinged the Moderation team!
Please note that this is ONLY for moderation purposes, and should not be used for spotDL assistance.
The moderation team may not be able to assist you. Please refer to <#796939712828801074>, <#797661959037780019> and if you need to, <#796571887635267614>
**Remember our teams are human as well! Please wait patiently, we will reply as soon as we can.**"""

            message = msg.content.lower()

            if "dll load failed" in message:
                message_for_sending = ("On Windows? You need to install Visual C++ 2019 redistributable\nhttps://docs.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist")
            elif "unable to get audio stream" in message:
                message_for_sending = ("On OSX? You need to install SSL certificates\nNavigate to `Applications/Python 3.10`, and double click `Install Certificates.command`\n(Change 3.10 to relevant version number)")
            elif "could not match any of the results on youtube" in message:
                message_for_sending = ("**YouTube Music must be available in your country for spotDL to work. This is because we use YouTube Music to filter search results. You can check if YouTube Music is available in your country, by visiting YouTube Music.** <https://music.youtube.com/>")
            elif "&dl_branch=1" in message or "&utm_source" in message:
                message_for_sending = ("**You must remove `&dl_branch=1`/`&utm_source` from URLs, since the `&` is a control operator in terminal**")
            elif "<@&798504444534587412>" in message:
                await msg.create_reaction("\U0001F6A8")  # 🚨
                await msg.create_reaction("ping:896186295771095040")  # Pinged emoji
                message_for_sending = (STAFF_PING)
            elif "'spotdl' is not recognized" in message:
                message_part = "You need to install Python from <https://www.python.org/downloads/>\n\nEnsure to add to PATH when installing:\nhttps://i.imgur.com/jWq5EnV.png"
                message_for_sending = (f"**Python/(site packages) is not added to PATH correctly.**\n{message_part} ")
            elif "error: http error 410: gone" in message:
                message_for_sending = ("This error has been patched. Update spotDL - `pip install -U --force spotdl`")
            elif "requests>=2.25.0" in message:
                message_for_sending = ("Outdated packages. `pip install -U --force requests urllib3 chardet`\nChange `pip` to `pip3` if running *UNIX")
            else:
                message_for_sending = None

            """SENDING AUTOREPLY"""
            if message_for_sending is not None:
                if int(msg.channel_id) != int(help_channel):
                    # Reply to msgs in every channel EXCEPT help channel (due to autothread)
                    await msg.reply(message_for_sending)
                else:
                    # If message in help channel, send the prompt in the created thread.
                    await thread.send(f"_ _\n\n**Automatic Prompt for {msg.author.username}:**\n{message_for_sending}")

    @interactions.extension_component("archive")
    async def archive(self, ctx):
        # await ctx.defer()

        # Get Channel Object
        thread_object = interactions.Channel(**await self.client._http.get_channel(ctx.channel_id), _client=self.client._http)

        try:
            # Get first messages_in_channel list variable
            messages_in_channel = await self.client._http.get_channel_messages(ctx.channel_id, limit=100)

            # Continue getting messages in channel until [-1]/last object has 'referenced_message' key.
            while "referenced_message" not in messages_in_channel[-1]:
                messages_in_channel.extend(await self.client._http.get_channel_messages(ctx.channel_id, before=messages_in_channel[-1].get("id"), limit=100))

                # If the message is type 21, it is a deleted message but of type "added to thread". This prevents infinite loops if the owner has deleted their msg.
                if messages_in_channel[-1].get("type") == 21:
                    raise NoOwnerError

            thread_author = messages_in_channel[-1].get("referenced_message").get("author").get("id")

            invoker = interactions.Member(**await self.client._http.get_member(int((await ctx.get_guild()).id), int(ctx.author.id)), _client=self.client._http)
            # If the invoker has no roles, set to an empty list so can be iterated through
            if invoker.roles is None:
                invoker.roles = []

            # Check if invoker is author/team member. If so, send message, disable button then archive thread.
            if int(thread_author) == int(ctx.author.id) or team_role_id in invoker.roles:
                await ctx.send(f"Thread archived by {ctx.author.mention}.\nAnyone can send a message to unarchive it.")
                await ctx.edit(components=interactions.Button(
                    style=interactions.ButtonStyle.SUCCESS,
                    label="Archive Thread as Resolved",
                    custom_id="archive",
                    disabled=True))
                await thread_object.archive()
            else:
                # If they aren't author or team member, give silent error message.
                await ctx.send("You need to be the thread author to archive this thread.", ephemeral=True)

        except NoOwnerError:
            # If we can't detect owner, send a warning messages and disable the button.
            await ctx.send(":warning: Error: No known owner found. Please contact the moderation team if you need the thread removed, else wait for it to auto-archive.")
            await ctx.edit(components=interactions.Button(
                style=interactions.ButtonStyle.SUCCESS,
                label="Archive Thread as Resolved",
                custom_id="archive",
                disabled=True))


def setup(client):
    AutoRepliesThread(client)
