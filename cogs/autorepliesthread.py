import disnake
from disnake.ext import commands, components
from credentials import help_channel, team_role_id, support_forum_channel


class AutoRepliesThread(commands.Cog):
    def __init__(self, client):
        self.client: commands.InteractionBot = client

    @commands.Cog.listener()
    async def on_thread_create(self, thread: disnake.Thread):
        # Check if thread chanel is on the forum channel

        if int(thread.parent_id) == int(support_forum_channel):
            # Send thread reply
            thread_start_msg = f"""\
{thread.owner.mention} Please continue adding more information into this thread.
You should include the following information:
**
- spotDL Version (e.g. 3.9.5)
- Operating System (e.g. Windows)**
- The actual command you ran, including any Spotify links
- Screenshots or pasted error messages if relevant
"""

            # Button archive component
            archive_btn = await self.archive_listener.build_button(
                style=disnake.ButtonStyle.green, label="Archive Thread as Resolved"
            )

            await thread.send(thread_start_msg, components=archive_btn)

    @commands.Cog.listener()
    async def on_message(self, msg: disnake.Message):
        # Only process if message is not sent by a bot.
        if msg.author.bot:
            return

        # * AUTOREPLIES SECTION

        STAFF_PING = """I have detected that you pinged the Moderation team!
Please note that this is ONLY for moderation purposes, and should not be used for spotDL assistance.
The moderation team may not be able to assist you. Please refer to <#796939712828801074>, <#797661959037780019> and if you need to, <#796571887635267614>
**Remember our teams are human as well! Please wait patiently, we will reply as soon as we can.**"""

        message = msg.content.lower()

        if "dll load failed" in message:
            message_for_sending = "On Windows? You need to install Visual C++ 2019 redistributable\nhttps://docs.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist"

        elif "unable to get audio stream" in message:
            message_for_sending = "On OSX? You need to install SSL certificates\nNavigate to `Applications/Python 3.10`, and double click `Install Certificates.command`\n(Change 3.10 to relevant version number)"

        elif "could not match any of the results on youtube" in message:
            message_for_sending = "**YouTube Music must be available in your country for spotDL to work. This is because we use YouTube Music to filter search results. You can check if YouTube Music is available in your country, by visiting YouTube Music.** <https://music.youtube.com/>"

        elif "&dl_branch=1" in message or "&utm_source" in message:
            message_for_sending = "**You must remove `&dl_branch=1`/`&utm_source` from URLs, since the `&` is a control operator in terminal**"

        elif "<@&798504444534587412>" in message:
            await msg.create_reaction("\U0001F6A8")  # 🚨
            await msg.create_reaction("ping:896186295771095040")  # Pinged emoji
            message_for_sending = STAFF_PING

        elif "'spotdl' is not recognized" in message:
            message_part = "You need to install Python from <https://www.python.org/downloads/>\n\nEnsure to add to PATH when installing:\nhttps://i.imgur.com/jWq5EnV.png"
            message_for_sending = f"**Python/(site packages) is not added to PATH correctly.**\n{message_part} "

        elif "error: http error 410: gone" in message:
            message_for_sending = "This error has been patched. Update spotDL - `pip install -U --force spotdl`"

        elif "requests>=2.25.0" in message:
            message_for_sending = "Outdated packages. `pip install -U --force requests urllib3 chardet`\nChange `pip` to `pip3` if running *UNIX"

        else:
            message_for_sending = None

        """SENDING AUTOREPLY"""
        if message_for_sending is not None:
            # Check if the message is in a thread

            if msg.channel.type != disnake.ChannelType.public_thread:
                await msg.reply(message_for_sending)

            elif (
                msg.channel.type == disnake.ChannelType.public_thread
                and msg.channel.parent.id == support_forum_channel
            ):
                await msg.channel.send(
                    f"_ _\n\n**Automatic Prompt for {msg.author.username}:**\n{message_for_sending}"
                )

    @components.button_listener()
    async def archive_listener(self, inter: disnake.MessageCommandInteraction):
        await inter.response.defer()

        # Get Channel Object
        thread = inter.channel
        thread_owner = thread.owner

        user_roles = [role.id for role in inter.author.roles]
        if thread_owner.id == inter.author.id or team_role_id in user_roles:
            await inter.send(
                f"Thread archived by {inter.author.mention}.\nAnyone can send a message to unarchive it.",
            )

            await inter.response.edit_message(
                components=await self.archive_listener.build_button(
                    style=disnake.ButtonStyle.green,
                    label="Archive Thread as Resolved",
                    disabled=True,
                )
            )

            await thread.edit(archived=True)
        else:
            # If they aren't author or team member, give silent error message.
            await inter.send(
                "You need to be the thread author to archive this thread.",
                ephemeral=True,
            )


def setup(client: commands.InteractionBot):
    client.add_cog(AutoRepliesThread(client))
