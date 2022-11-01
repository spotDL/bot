import datetime
import logging
import os
import platform
import signal
import sys
import subprocess

import disnake
from disnake.ext import commands, components
import psutil


class Commands(commands.Cog):
    @commands.slash_command(
        name="ping",
        description="Ping spotDL's Bot!",
    )
    async def ping(self, inter: disnake.MessageCommandInteraction):
        await inter.send(f"Pong! ({round(inter.bot.latency * 1000)}ms)", ephemeral=True)

    @commands.slash_command(
        name="ffmpeg",
        description="FFmpeg Commands",
        options=[
            disnake.Option(
                name="install",
                description="",
                type=disnake.OptionType.sub_command,
            ),
            disnake.Option(
                name="info",
                description="",
                type=disnake.OptionType.sub_command,
            ),
        ],
    )
    async def ffmpeg(self, inter: disnake.MessageCommandInteraction):
        pass

    @ffmpeg.sub_command(name="install", description="Instructions to install FFmpeg")
    async def ffmpeg_install(self, inter: disnake.MessageCommandInteraction):
        await inter.send(
            "Windows: [Download Binaries](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z) then [follow tutorial](https://windowsloop.com/install-ffmpeg-windows-10/)\nOSX: `brew install ffmpeg`\nUbuntu:`sudo apt install ffmpeg -y`"
        )

    @ffmpeg.sub_command(
        name="info", description="Info about using FFmpeg with spotDL v4"
    )
    async def ffmpeg_info(self, inter: disnake.MessageCommandInteraction):
        embed = disnake.Embed(
            title="FFmpeg and spotDL v4",
            description="spotDL requires FFmpeg v4.2 or above",
            color=0x0000FF,
        ).add_field(
            name="Specify path to FFmpeg",
            value="If you don't want to add FFmpeg to your PATH, you can specify the path to the FFmpeg binary:\nAdd the `-f` or `--ffmpeg` flag to your command. e.g.\n`spotdl -f /path/to/ffmpeg.exe [trackUrl]`",
            inline=False,
        )

        await inter.send(embed=embed)

    @commands.slash_command(
        name="update",
        description="Various update instructions for spotDL",
    )
    async def update_spotdl(
        self,
        inter: disnake.MessageCommandInteraction,
        location: str = commands.Param(
            name="location",
            description="Where should the update come from?",
            choices=[
                disnake.OptionChoice(name="pip/PyPi", value="pip"),
                disnake.OptionChoice("Master Branch on Github", value="master"),
                disnake.OptionChoice(name="Dev Branch on Github", value="dev"),
            ],
        ),
        force: bool = commands.Param(
            default=False, name="force", description="Use --force-reinstall flag?"
        ),
    ):
        if location == "pip":
            message = "To update spotDL, run `pip install -U spotdl`"
        else:
            message = f"To update spotDL, run `pip install -U https://codeload.github.com/spotDL/spotify-downloader/zip/{location}`"

        if force:
            split_message = message.split()
            split_message.insert(split_message.index("-U"), "--force")
            message = " ".join(split_message)

        await inter.send(message)

    @commands.slash_command(name="path", description="How to add things to PATH")
    async def path(
        self,
        inter: disnake.MessageCommandInteraction,
        shell: str = commands.Param(
            name="shell",
            description="What shell is the user running? Or Windows?",
            choices=[
                disnake.OptionChoice(name="Windows", value="Windows"),
                disnake.OptionChoice(name="zshrc", value="zshrc"),
                disnake.OptionChoice(name="bashrc", value="bashrc"),
            ],
        ),
    ):
        if shell == "Windows":
            await inter.send(
                "**Adding to PATH on Windows**\nIn Start Menu, Search `env` then click `Edit the system environment variables`, then click `Environment Variables` in the bottom right.\nIn System variables, scroll down to `Path` and double Click. You can now view or edit the PATH variable."
            )

        if shell == "zshrc":
            await inter.send(
                "**Adding to PATH for Zsh terminal**\nAdd `export PATH=~/.local/bin:$PATH` at the bottom of `~/.zshrc`\nThen run `source ~/.zshrc`"
            )

        if shell == "bashrc":
            await inter.send(
                "**Adding to PATH for Bash terminal**\nAdd `export PATH=~/.local/bin:$PATH` at the bottom of `~/.bashrc`\nThen run `source ~/.bashrc`"
            )

    @commands.slash_command(
        name="outputformat", description="How to change output format? Options?"
    )
    async def outputformat(self, inter: disnake.MessageCommandInteraction):
        await inter.send(
            "**How to change output format?**\nUse the `--format` flag.\nPossible formats are `mp3, ogg, flac, opus, m4a`\nE.g. `spotdl [trackUrl] --format opus`"
        )

    @commands.slash_command(
        name="download",
        description="Where did my files download?",
    )
    async def download(self, inter: disnake.MessageCommandInteraction):
        embed = (
            disnake.Embed(
                title="Where are my files downloaded / How can I change download location?",
                color=0xFFFFFF,
            )
            .add_field(
                name="By default, spotDL downloads to the working directory aka Where you ran spotDL from",
                value="You can change the working directory with `cd`. On Windows, the default working directory is `C:\\Users\\YOURNAME\\`",
                inline=False,
            )
            .add_field(
                name="Changing Output Directory",
                value="Use the `--output` flag to change ouput directory, e.g. `spotdl [songUrl] --output /home/music/`\n\nYou can use flags to specify a custom path template. For example, your music could be sorted into nested folders per album. (`spotdl [songUrl] --output '{artist}/{album}/{title} - {artist}.{ext}'`\
                        \nYou can use the following variables in your path template: `{title}, {artists}, {artist}, {album}, {album-artist}, {genre}, {disc-number}, {disc-count}, {duration}, {year}, {original-date}, {track-number}, {tracks-count}, {isrc}, {track-id}, {publisher}, {list-length}, {list-position}, {list-name}, {output-ext}`.",
                inline=False,
            )
        )
        await inter.send(embed=embed)

    @commands.slash_command(
        name="testsong",
        description="Download command for the spotDL test song - for troubleshooting purposes",
    )
    async def testsong(self, inter: disnake.MessageCommandInteraction):
        await inter.send(
            "**Test Song:**\n`spotdl download https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b`"
        )

    @commands.slash_command(
        name="github", description="Links to different spotDL documentation"
    )
    async def github(
        self,
        inter: disnake.MessageCommandInteraction,
        destination: str = commands.Param(
            name="file",
            description="What file you want to link to?",
            choices=[
                disnake.OptionChoice(name="README", value="readme"),
                disnake.OptionChoice(
                    name="Installation Guide", value="installationguide"
                ),
                disnake.OptionChoice(
                    name="Contributing Guidelines", value="contributing"
                ),
                disnake.OptionChoice(name="Core Values", value="corevalues"),
                disnake.OptionChoice(name="License", value="license"),
                disnake.OptionChoice(name="Issues", value="issues"),
            ],
        ),
    ):
        answers = {
            "readme": "Detailed information in our README.md\n<https://github.com/spotDL/spotify-downloader/blob/master/README.md>",
            "installationguide": "You can find our Installation Guide at <https://github.com/spotDL/spotify-downloader/blob/master/docs/INSTALLATION.md>",
            "contributing": "You can find our Contributing Guidelines at <https://github.com/spotDL/spotify-downloader/blob/master/docs/CONTRIBUTING.md>",
            "corevalues": "You can find our Core Values at <https://github.com/spotDL/spotify-downloader/blob/master/docs/CORE_VALUES.md>",
            "license": "You can find our Project License at <https://github.com/spotDL/spotify-downloader/blob/master/LICENSE>",
            "issues": "You can find our Issues Page at <https://github.com/spotDL/spotify-downloader/issues>",
        }

        await inter.send(answers.get(destination, "An error has occured."))

    @commands.slash_command(
        name="youtube",
        description="YouTube Music & spotDL",
    )
    async def youtube(self, inter: disnake.MessageCommandInteraction):
        embed = (
            disnake.Embed(
                title="spotDL and YouTube",
                color=0xC4302B,
            )
            .set_image(url="https://i.imgur.com/tCaTBTt.png")
            .add_field(
                name="Quality",
                value="spotDL automatically gets the highest quality audio from YouTube",
                inline=False,
            )
            .add_field(
                name="YouTube Music Required",
                value="YouTube Music must be available in your country for spotDL to work. This is because we use YouTube Music to filter search results. You can check if YouTube Music is available in your country, by visiting YouTube Music. <https://music.youtube.com/>",
                inline=False,
            )
            .add_field(
                name="spotDL Downloads From YouTube",
                value="spotDL downloads from YouTube if a track is found.",
                inline=False,
            )
        )

        await inter.send(embed=embed)

    @commands.slash_command(
        name="pickyoutube",
        description="How do I download a specific YouTube video with Spotify Metadata?",
    )
    async def pickyoutube(self, inter: disnake.MessageCommandInteraction):
        await inter.send(
            """You can specify specific YouTube videos to download with Spotify metadata, or vice versa.\nTo do this, use the notation **`spotdl download "YouTubeURL|SpotifyURL"`**\nNote that the quote marks (") are essential."""
        )

    @commands.slash_command(
        name="zsh",
        description="Special instructions for users using Zsh (Z Shell) terminal",
    )
    async def zsh(self, inter):
        await inter.send(
            'If you use Zsh terminal, **put the URL in quotes**, e.g.\n`spotdl "https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b"`'
        )

    @commands.slash_command(
        name="podcast",
        description="spotDL cannot download podcasts/episodes from Spotify",
    )
    async def podcast(self, inter):
        await inter.send(
            "spotDL does not support downloading podcasts/episodes from Spotify"
        )

    @commands.slash_command(
        name="rules",
        description="Prompts for users to follow our rules",
    )
    async def rules(
        self,
        inter,
        rule: str = commands.Param(
            name="rule",
            description="Which prompt?",
            choices=[
                disnake.OptionChoice(name="Disabling Reply Pings", value="reply"),
                disnake.OptionChoice(name="Not Mentioning", value="mention"),
                disnake.OptionChoice(
                    name="Don't spam issues across channels", value="channel"
                ),
            ],
        ),
    ):
        answers = {
            "reply": "**Please disable reply pings**\n\nOur devs are human as well! Please wait patiently, we will reply as soon as we can.\nhttps://i.imgur.com/yIxI1RW.png",
            "mention": "**Please don't ping devs**\n\nOur devs are human as well! Please wait patiently, we will reply as soon as we can.",
            "channel": "**Please don't spam your issue across channels**\n\nOur devs are human as well! Please wait patiently, we will reply as soon as we can.",
        }

        await inter.send(answers.get(rule, "An error has occured."))

    @commands.slash_command(
        name="admin",
        description="Administration Commands",
    )
    async def admin(self, inter: disnake.MessageCommandInteraction):
        message_components = [
            await self.admin_listener.build_component(
                style=disnake.ButtonStyle.red, label="Shutdown Bot", step="shutdown" # type: ignore
            ),
            await self.admin_listener.build_component(
                style=disnake.ButtonStyle.green, label="Restart Bot", step="restart" # type: ignore
            ),
            await self.admin_listener.build_component(
                style=disnake.ButtonStyle.blurple, label="Update Bot", step="update" # type: ignore
            ),
            await self.admin_listener.build_component(
                style=disnake.ButtonStyle.gray, label="VPS Info", step="vps"  # type: ignore
            ),
        ]

        if inter.bot.owner and inter.author.id == inter.bot.owner.id:
            await inter.send("Administration Controls", components=message_components)
        else:
            await inter.send(
                "You do not have permission to use this command.", ephemeral=True
            )

    @components.button_listener() # type: ignore
    async def admin_listener(
        self, inter: disnake.MessageCommandInteraction, *, step: str
    ):

        await inter.response.defer(with_message=True)
        if not inter.bot.owner or inter.author.id != inter.bot.owner.id:
            await inter.edit_original_response(
                "You do not have permission to use this command."
            )
            return

        if step == "shutdown":
            os_name = platform.system()
            print(f"Shutting down as per request from {inter.author.name}")
            logging.critical(f"Shutting down as per request from {inter.author.name}")

            if os_name == "Windows":
                await inter.edit_original_message(
                    "Encountered an unknown error...", components=None
                )

            else:
                await inter.edit_original_message("Shutting down...", components=None)
                os.kill(os.getpid(), signal.SIGINT)

        if step == "restart":
            print(f"Restarting as per request from {inter.author.name}")
            logging.critical(f"Restarting as per request from {inter.author.name}")
            await inter.edit_original_message("Restarting...", components=None)
            os.execv(sys.executable, ["python"] + sys.argv)

        if step == "update":
            print(f"Updating as per request from {inter.author.name}")
            logging.critical(f"Updating as per request from {inter.author.name}")

            await inter.edit_original_message("Updating...", components=None)
            process = subprocess.run(
                ["git", "pull"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            output, _ = process.stdout.decode(), process.stderr.decode()
            print(output)
            await inter.edit_original_message(f"Updated!\n```{output}```")

        if step == "vps":
            print("asked for vps info")
            embed = (
                disnake.Embed(
                    title="VPS Info",
                    color=0x7289DA,
                )
                .add_field(
                    name="CPU Usage",
                    value=str(psutil.cpu_percent()) + "%",
                    inline=False,
                )
                .add_field(
                    name="RAM Usage",
                    value=str(psutil.virtual_memory().percent) + "%",
                    inline=False,
                )
                .add_field(
                    name="Disk Usage",
                    value=str(psutil.disk_usage("/").percent) + "%",
                    inline=False,
                )
                .add_field(
                    name="System Boot Time",
                    value=str(
                        datetime.datetime.fromtimestamp(psutil.boot_time()).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    ),
                ),
            )

            await inter.edit_original_message(embeds=list(embed), components=None)


def setup(client: commands.InteractionBot):
    client.add_cog(Commands())
