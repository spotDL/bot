import disnake
from disnake.ext import commands, components
import logging
import traceback
import os
import datetime


SUPPORT_FORUM_CHANNEL_ID = os.getenv("SUPPORT_FORUM_CHANNEL_ID", "0")
TEAM_ROLE_ID = os.getenv("TEAM_ROLE_ID", "0")
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")
ICON_URL = "https://images-ext-2.discordapp.net/external/ClNXwHa0TgfUjlPtkrbhz2eOWEXGiDljja42v2yPFLA/%3Fsize%3D1024/https/cdn.discordapp.com/icons/771628785447337985/abe4aa2ac4b1884c2fd0675814216f8a.png"
STAFF_PING = """I have detected that you pinged the Moderation team!
Please note that this is ONLY for moderation purposes, and should not be used for spotDL assistance.
The moderation team may not be able to assist you. Please refer to <#796939712828801074>, <#797661959037780019> and if you need to, <#796571887635267614>
**Remember our teams are human as well! Please wait patiently, we will reply as soon as we can.**"""


class AutoRepliesThread(commands.Cog):
    """This cog handles thread creation in the forum channel"""

    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

        self.auto_embed = (
            disnake.Embed(
                description="Please continue adding more information into this thread.\nYou should include the following information:",
                color=disnake.Color.brand_green(),
            )
            .set_author(name="spotDL Support", icon_url=ICON_URL)
            .add_field(name="spotDL Version", value="Eg. `4.0.0`")
            .add_field(name="Operating System", value="Eg. ***Windows 22H2***")
            .add_field(
                name="The Command You Ran",
                value="Please include Spotify links.",
            )
            .add_field(
                name="Screenshots or Pasted Error Messages",
                value="Only send these if they are relevant.\n\n To send pasted error messages use three backticks (```)\n[Here's](https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-) info on how to use code blocks.",
            )
        )

        self.auto_replies = {
            "dll load failed": "On Windows? You need to install Visual C++ 2019 redistributable\nhttps://docs.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist",
            "unable to get audio stream": "On OSX? You need to install SSL certificates\nNavigate to `Applications/Python 3.10`, and double click `Install Certificates.command`\n(Change 3.10 to relevant version number)",
            "could not match any of the results on youtube": "**YouTube Music must be available in your country for spotDL to work. This is because we use YouTube Music to filter search results. You can check if YouTube Music is available in your country, by visiting YouTube Music.** <https://music.youtube.com/>",
            "&dl_branch=1": "**You must remove `&dl_branch=1`/`&utm_source` from URLs, since the `&` is a control operator in terminal**",
            "<@&798504444534587412>": STAFF_PING,
            "'spotdl' is not recognized": "**Python/(site packages) is not added to PATH correctly.**\nYou need to install Python from <https://www.python.org/downloads/>\n\nEnsure to add to PATH when installing:\nhttps://i.imgur.com/jWq5EnV.png",
            "error: http error 410: gone": "This error has been patched. Update spotDL - `pip install -U --force spotdl`",
            "requests>=2.25.0": "Outdated packages. `pip install -U --force requests urllib3 chardet`\nChange `pip` to `pip3` if running *UNIX",
            "zsh: no matches found": 'If you use Zsh terminal, put the URL in quotes, e.g.\n`spotdl download "https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b"`',
        }

    # * Utility functions
    def _log_thread_creation(self, thread: disnake.Thread) -> disnake.Embed:
        """Builds the log embed for the log channel when a thread is created."""

        log_embed = (
            disnake.Embed(
                title="Thread Created",
                description=f"{thread.mention} was created.",
                color=disnake.Color.gold(),
            )
            .add_field(
                name="Log Date",
                value=f"<t:{round(datetime.datetime.now().timestamp())}:f>",
            )
            .set_author(
                name=thread.owner,
                icon_url=thread.owner.avatar.url if thread.owner else None,
            )
        )

        return log_embed

    def _log_thread_archive(self, thread: disnake.Thread) -> disnake.Embed:
        """Builds the log embed for the log channel when a thread is archived."""

        log_embed = (
            disnake.Embed(
                title="Thread Archived",
                description=f"{thread.mention} was created.",
                color=disnake.Color.green(),
            )
            .add_field(
                name="Log Date",
                value=f"<t:{round(datetime.datetime.now().timestamp())}:f>",
            )
            .set_author(
                name=thread.owner,
                icon_url=thread.owner.avatar.url if thread.owner else None,
            )
        )

        return log_embed

    # * Event and Component Listeners
    @commands.Cog.listener()
    async def on_thread_create(self, thread: disnake.Thread):
        "Triggers when a thread is created."

        # Thread was not created in the Support Forum Channel
        if not (int(thread.parent_id) == int(SUPPORT_FORUM_CHANNEL_ID)):
            return

        # "Archive" button component
        archive_btn = await self.archive_listener.build_component(
            style=disnake.ButtonStyle.green, label="Archive Thread as Resolved"
        )  # type: ignore

        await thread.send(embed=self.auto_embed, components=archive_btn)

        # Mention the thread owner only if it is not the bot
        if thread.owner.id != thread.me.id:
            await thread.send(thread.owner.mention)

        logging.info(
            f"[THREAD] Thread created at: {datetime.datetime.now()}.\nAuthor: {thread.owner}"
        )

        # Send log to log channel
        log_embed = self._log_thread_creation(thread)
        logs_channel = self.bot.get_channel(int(LOG_CHANNEL_ID))
        await logs_channel.send(embed=log_embed)

    @components.button_listener()  # type: ignore
    async def archive_listener(self, inter: disnake.MessageCommandInteraction):
        "Function that builds the archive button component and handles the interaction."
        await inter.response.defer()

        # Get Channel Object
        thread = inter.channel
        owner = inter.channel.owner
        user_roles = [role.id for role in inter.author.roles]  # type: ignore

        if not (
            owner and owner.id == inter.author.id or int(TEAM_ROLE_ID) in user_roles
        ):
            # If they aren't author or team member, give silent error message.
            await inter.send(
                "You need to be the thread author to archive this thread.",
                ephemeral=True,
            )
            return

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

        log_embed = self._log_thread_archive(thread)
        logs_channel = self.bot.get_channel(int(LOG_CHANNEL_ID))
        await logs_channel.send(embed=log_embed)

        try:
            await thread.edit(archived=True)  # type: ignore

        except:
            logging.error(traceback.format_exc())
            await inter.send("There was an error archiving this thread.")

    @commands.message_command(name="Create Support Thread", dm_permission=False)
    async def create_support_thread(
        self, inter: disnake.MessageCommandInteraction, message: disnake.Message
    ):
        "Function that handles the right click menu for creating a thread"
        await inter.response.defer(with_message=True, ephemeral=True)

        logging.info(
            f"{inter.author} attempted to create a Support Thread on message: {message.jump_url}"
        )
        # Check if team role is in user's role

        role_ids = [role.id for role in inter.author.roles]
        if not int(TEAM_ROLE_ID) in role_ids:
            await inter.send("Sorry, you can't do that.", ephemeral=True)
            return

        thread_channel = inter.bot.get_channel(int(SUPPORT_FORUM_CHANNEL_ID))
        content = f"{message.content}\n===========\n**Original message link:** {message.jump_url}"
        thread, _ = await thread_channel.create_thread(
            name=f"{message.author.display_name}'s Support Thread",
            content=content,
        )

        await thread.send(
            f"Hey, {message.author.mention}, a support thread was opened to you by {inter.author.mention}"
        )

        # Send confirmation to the mod who opened the thread.
        await inter.send(
            f"A support thread has been successfully created for this user at {thread.mention}.",
            ephemeral=True,
        )

    @commands.Cog.listener()
    async def on_slash_command_error(
        self, inter: disnake.MessageCommandInteraction, error: commands.CommandError
    ):
        await inter.send("Sorry, an error occured.", ephemeral=True)
        logging.critical(error)

        embed = disnake.Embed(
            title="Error", description=error, color=disnake.Color.red()
        )

        logs_channel = self.bot.get_channel(int(LOG_CHANNEL_ID))
        await logs_channel.send(embed=embed)

    # * Slash Commands and autoreplies
    @commands.slash_command(
        name="autoreplies", description="Lists all automatic replies."
    )
    async def autoreplies(self, inter: disnake.MessageCommandInteraction):
        "Lists all automatic replies."
        embed = disnake.Embed(
            title="spotDL Bot Autoreplies",
            color=disnake.Color.green(),
        )

        for reply in self.auto_replies:
            embed.add_field(name=reply, value=self.auto_replies[reply], inline=False)
        await inter.send(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, msg: disnake.Message):
        "Triggers when a message is sent."

        # Only process if message is not sent by a bot.
        if msg.author.bot:
            return

        # * AUTOREPLIES SECTION

        message = msg.content.lower()

        if ".automsg" in message:
            await msg.channel.send(embed=self.auto_embed)
            await msg.delete()
            return

        for reply in self.auto_replies:
            if reply in message:
                await msg.reply(self.auto_replies[reply])


def setup(client: commands.InteractionBot):
    client.add_cog(AutoRepliesThread(client))
