from typing import Union
import disnake
from disnake.ext import commands, components
from disnake.channel import TextChannel, VoiceChannel
from disnake.threads import Thread
import logging
import traceback
import os

SUPPORT_FORUM_CHANNEL_ID = os.getenv("SUPPORT_FORUM_CHANNEL_ID", "0")
TEAM_ROLE_ID = os.getenv("TEAM_ROLE_ID", "0")


class AutoRepliesThread(commands.Cog):
    """This cog handles thread creation in the forum channel"""

    @commands.Cog.listener()
    async def on_thread_create(self, thread: disnake.Thread):

        logging.info("A thread was created.")

        # Check if thread owner is the bot.
        thread_owner = await self._get_thread_owner(thread)

        if thread_owner is None:
            return

        # Check if thread chanel is on the forum channel

        if int(thread.parent_id) == int(SUPPORT_FORUM_CHANNEL_ID):
            # Send thread reply

            # Build embed
            embed = (
                disnake.Embed(
                    description="Please continue adding more information into this thread.\nYou should include the following information:",
                    color=disnake.Color.brand_green(),
                )
                .set_author(
                    name="spotDL Support",
                    icon_url=thread.guild.icon.url if thread.guild.icon else None,
                )
                .add_field(name="spotDL Version", value="Eg. `4.0.0`")
                .add_field(name="Operating System", value="Eg. ***Windows***")
                .add_field(
                    name="The Command You Ran",
                    value="Please include Spotify links.",
                )
                .add_field(
                    name="Screenshots or Pasted Error Messages",
                    value="Only send these if they are relevant.\n\n To send pasted error messages use three backticks (```)\n[Here's](https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-) on how to use code blocks.",
                )
            )

            # Button archive component
            archive_btn = await self.archive_listener.build_component(
                style=disnake.ButtonStyle.green, label="Archive Thread as Resolved"
            )  # type: ignore

            await thread.send(embed=embed, components=archive_btn)
            owner = await self._get_thread_owner(thread)
            await thread.send(owner.mention)

            logging.info("Info messages were sent.")

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
        message_for_sending = None

        if "dll load failed" in message:
            message_for_sending = "On Windows? You need to install Visual C++ 2019 redistributable\nhttps://docs.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist"

        elif "unable to get audio stream" in message:
            message_for_sending = "On OSX? You need to install SSL certificates\nNavigate to `Applications/Python 3.10`, and double click `Install Certificates.command`\n(Change 3.10 to relevant version number)"

        elif "could not match any of the results on youtube" in message:
            message_for_sending = "**YouTube Music must be available in your country for spotDL to work. This is because we use YouTube Music to filter search results. You can check if YouTube Music is available in your country, by visiting YouTube Music.** <https://music.youtube.com/>"

        elif "&dl_branch=1" in message or "&utm_source" in message:
            message_for_sending = "**You must remove `&dl_branch=1`/`&utm_source` from URLs, since the `&` is a control operator in terminal**"

        elif "<@&798504444534587412>" in message:
            await msg.add_reaction("\U0001F6A8")  # 🚨
            await msg.add_reaction("ping:896186295771095040")  # Pinged emoji
            message_for_sending = STAFF_PING

        elif "'spotdl' is not recognized" in message:
            message_part = "You need to install Python from <https://www.python.org/downloads/>\n\nEnsure to add to PATH when installing:\nhttps://i.imgur.com/jWq5EnV.png"
            message_for_sending = f"**Python/(site packages) is not added to PATH correctly.**\n{message_part} "

        elif "error: http error 410: gone" in message:
            message_for_sending = "This error has been patched. Update spotDL - `pip install -U --force spotdl`"

        elif "requests>=2.25.0" in message:
            message_for_sending = "Outdated packages. `pip install -U --force requests urllib3 chardet`\nChange `pip` to `pip3` if running *UNIX"

        # * Send auto reply
        if message_for_sending is not None:
            # Check if the message is in a thread

            await msg.reply(message_for_sending)

    @components.button_listener()  # type: ignore
    async def archive_listener(self, inter: disnake.MessageCommandInteraction):
        await inter.response.defer()

        # Get Channel Object
        thread = inter.channel

        # Get thread owner
        thread_owner = None
        async for message in thread.history(oldest_first=True):

            # If the message author is not me
            if (
                isinstance(thread, Union[TextChannel, Thread, VoiceChannel])
                and message.author != thread.guild.me
            ):
                thread_owner = message.author
                break

        user_roles = [role.id for role in inter.author.roles]  # type: ignore
        if (
            thread_owner
            and thread_owner.id == inter.author.id
            or int(TEAM_ROLE_ID) in user_roles
        ):
            await inter.send(
                f"Thread archived by {inter.author.mention}.\nAnyone can send a message to unarchive it.",
            )

            await inter.edit_original_message(
                components=await self.archive_listener.build_button(
                    style=disnake.ButtonStyle.green,
                    label="Archive Thread as Resolved",
                    disabled=True,
                )
            )
            logging.info("Archive messages sent.")

            try:
                await thread.edit(archived=True)  # type: ignore

            except:
                logging.error(traceback.format_exc())

        else:
            logging.warn(
                f"{inter.author} does not have permissions to manage the thread."
            )

            # If they aren't author or team member, give silent error message.
            await inter.send(
                "You need to be the thread author to archive this thread.",
                ephemeral=True,
            )

    @commands.message_command(name="Create Support Thread", dm_permission=False)
    async def create_support_thread(
        self, inter: disnake.MessageCommandInteraction, message: disnake.Message
    ):
        await inter.response.defer(with_message=True, ephemeral=True)
        # Check if team role is in user's role

        logging.info(
            f"{inter.author} attempted to create a Support Thread on message: {message.jump_url}"
        )
        role_ids = [role.id for role in inter.author.roles]

        if not int(TEAM_ROLE_ID) in role_ids:
            logging.info(f"{inter.author} did not have enough perms.")
            await inter.send("Sorry, you can't do that.", ephemeral=True)
            return

        thread_channel = inter.bot.get_channel(int(SUPPORT_FORUM_CHANNEL_ID))
        content = f"{message.content}\n===========\n**Original message link:** {message.jump_url}"
        thread, open_message = await thread_channel.create_thread(
            name=f"{inter.author.display_name}'s Support Thread",
            content=content,
        )

        logging.info(f"Thread created")
        # Build embed
        embed = (
            disnake.Embed(
                description="Please continue adding more information into this thread.\nYou should include the following information:",
                color=disnake.Color.brand_green(),
            )
            .set_author(
                name="spotDL Support",
                icon_url=thread.guild.icon.url if thread.guild.icon else None,
            )
            .add_field(name="spotDL Version", value="Eg. `4.0.0`")
            .add_field(name="Operating System", value="Eg. ***Windows***")
            .add_field(
                name="The Command You Ran",
                value="Please include Spotify links.",
            )
            .add_field(
                name="Screenshots or Pasted Error Messages",
                value="Only send these if they are relevant.\n\n To send pasted error messages use three backticks (```)\n[Here's](https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-) on how to use code blocks.",
            )
        )

        # Button archive component
        archive_btn = await self.archive_listener.build_component(
            style=disnake.ButtonStyle.green, label="Archive Thread as Resolved"
        )  # type: ignore

        await thread.send(embed=embed, components=archive_btn)
        await thread.send(
            f"Hey, {message.author.mention}, a support thread was opened to you by {inter.author.mention}"
        )
        await inter.send(
            f"A support thread has been successfully created for this user at {thread.mention}.",
            ephemeral=True,
        )

        logging.info("Info messages were sent.")

    async def _get_thread_owner(
        self, thread: disnake.Thread
    ) -> Union[disnake.Member, disnake.User, None]:
        """Retrieves the owner object of the specified thread."""

        thread_owner = None
        async for message in thread.history(oldest_first=True):

            # If the message author is not me
            if (
                isinstance(thread, Union[TextChannel, Thread, VoiceChannel])
                and message.author != thread.guild.me
            ):
                thread_owner = message.author
                break

        return thread_owner


def setup(client: commands.InteractionBot):
    client.add_cog(AutoRepliesThread())
