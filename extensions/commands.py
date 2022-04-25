import interactions
import os
import sys
import psutil
import datetime
from credentials import guild_id, owner_id


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

    @interactions.extension_command(
        name="ffmpeg",
        description="FFmpeg Commands",
        scope=guild_id,
        options=[
            interactions.Option(
                name="install",
                description="Instructions to install FFmpeg",
                type=interactions.OptionType.SUB_COMMAND,
            ),
            interactions.Option(
                name="info",
                description="Info about using FFmpeg with spotDL v3",
                type=interactions.OptionType.SUB_COMMAND,
            ),
        ]
    )
    async def ffmpeg(self, ctx, sub_command: str):
        match sub_command:
            case "install":
                await ctx.send("Windows: [Download Binaries](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z) then [follow tutorial](https://windowsloop.com/install-ffmpeg-windows-10/)\nOSX: `brew install ffmpeg`\nUbuntu:`sudo apt install ffmpeg -y`")
            case "info":
                embed = interactions.Embed(
                    title="FFmpeg and spotDL v3",
                    description="spotDL requires FFmpeg v4.2 or above",
                    color=0x0000FF,
                    fields=[
                        interactions.EmbedField(
                            name="Specify path to FFmpeg",
                            value="If you don't want to add FFmpeg to your PATH, you can specify the path to the FFmpeg binary:\nAdd the `-f` or `--ffmpeg` flag to your command. e.g.\n`spotdl -f /path/to/ffmpeg.exe [trackUrl]`",
                            inline=False,
                        ),
                        interactions.EmbedField(
                            name="FFmpeg version couldn't be detected?",
                            value="Add the `--ignore-ffmpeg-version` flag to your spotDL command.\nThis is common if you are using a nightly FFmpeg build.",
                            inline=False,
                        )
                    ]
                )

                await ctx.send(embeds=embed)

    @interactions.extension_command(
        name="update",
        description="Various update instructions for spotDL",
        scope=guild_id,
        options=[
            interactions.Option(
                type=interactions.OptionType.STRING,
                name="location",
                description="Where should the update come from?",
                required=True,
                focused=True,
                choices=[
                    interactions.Choice(name="pip/PyPi", value="pip"),
                    interactions.Choice(name="Master Branch on GitHub", value="master"),
                    interactions.Choice(name="Dev Branch on GitHub", value="dev"),
                    interactions.Choice(name="v4 Master Branch on GitHub", value="v4"),
                ]
            ),
            interactions.Option(
                type=interactions.OptionType.BOOLEAN,
                name="force",
                description="Use --force-reinstall flag?",
                required=False,
            )
        ]
    )
    async def update(self, ctx, location: str, force: bool = False):
        match location:
            case "pip":
                message = ("To update spotDL, run `pip install -U spotdl`")
            case "master" | "dev":
                message = (f"To update spotDL, run `pip install -U https://codeload.github.com/spotDL/spotify-downloader/zip/{location}`")
            case "v4":
                message = ("To update spotDL, run `pip install -U https://codeload.github.com/spotDL/spotdl-v4/zip/master`")
        if force:
            split_message = message.split()
            split_message.insert(split_message.index("-U"), "--force")
            message = " ".join(split_message)

        await ctx.send(message)

    @interactions.extension_command(
        name="path",
        description="How to add things to PATH",
        scope=guild_id,
        options=[
            interactions.Option(
                type=interactions.OptionType.STRING,
                name="shell",
                description="What shell is the user running? Or Windows",
                required=True,
                focused=True,
                choices=[
                    interactions.Choice(name="Windows", value="Windows"),
                    interactions.Choice(name="zshrc", value="zshrc"),
                    interactions.Choice(name="bashrc", value="bashrc"),
                ]
            )
        ]
    )
    async def path(self, ctx, shell: str):
        match shell:
            case "Windows":
                await ctx.send("**Adding to PATH on Windows**\nIn Start Menu, Search `env` then click `Edit the system environment variables`, then click `Environment Variables` in the bottom right.\nIn System variables, scroll down to `Path` and double Click. You can now view or edit the PATH variable.")
            case "zshrc":
                await ctx.send("**Adding to PATH for Zsh terminal**\nAdd `export PATH=~/.local/bin:$PATH` at the bottom of `~/.zshrc`\nThen run `source ~/.zshrc`")
            case "bashrc":
                await ctx.send("**Adding to PATH for Bash terminal**\nAdd `export PATH=~/.local/bin:$PATH` at the bottom of `~/.bashrc`\nThen run `source ~/.bashrc`")

    @interactions.extension_command(
        name="outputformat",
        description="How to change output format? Options?",
        scope=guild_id,
    )
    async def outputformat(self, ctx):
        await ctx.send("**How to change output format?**\nUse the `--of` or `--output-format` flag.\nPossible formats are `mp3, ogg, flac, opus, m4a`\nE.g. `spotdl [trackUrl] --of opus`")

    @interactions.extension_command(
        name="download",
        description="Where did my files download?",
        scope=guild_id,
    )
    async def download(self, ctx):
        embed = interactions.Embed(
            title="Where are my files downloaded / How can I change download location?",
            color=0xFFFFFF,
            fields=[
                interactions.EmbedField(
                    name="By default, spotDL downloads to the working directory aka Where you ran spotDL from",
                    value="You can change the working directory with `cd`. On Windows, the default working directory is `C:\\Users\\YOURNAME\\`",
                    inline=False,
                ),
                interactions.EmbedField(
                    name="Changing Output Directory",
                    value="Use the `-o` or `--output` flag to change ouput directory, e.g. `spotdl [songUrl] -o /home/music/`",
                    inline=False,
                ),
                interactions.EmbedField(
                    name="Path Templates",
                    value="You can use the `--path-template` flag to specify a custom path template. For example, your music could be sorted into nested folders per album. (`spotdl [songUrl] --path-template '{artist}/{album}/{title} - {artist}.{ext}'`\
                        \nYou can use the following variables in your path template: `{artist}, {artists}, {title}, {album}, {playlist}, {ext}`.v4 will provide more customisability.",
                    inline=False,
                ),
            ],
        )
        await ctx.send(embeds=embed)

    @interactions.extension_command(
        name="testsong",
        description="Download command for the spotDL test song - for troubleshooting purposes",
        scope=guild_id,
    )
    async def testsong(self, ctx):
        await ctx.send("**Test Song:**\n`spotdl https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b`")

    @interactions.extension_command(
        name="github",
        description="Links to different spotDL documentation",
        scope=guild_id,
        options=[
            interactions.Option(
                type=interactions.OptionType.STRING,
                name="file",
                description="What file do you want to link to?",
                required=True,
                focused=True,
                choices=[
                    interactions.Choice(name="README", value="readme"),
                    interactions.Choice(name="Installation Guide", value="installationguide"),
                    interactions.Choice(name="Contributing Guidelines", value="contributing"),
                    interactions.Choice(name="Core Values", value="corevalues"),
                    interactions.Choice(name="License", value="license"),
                    interactions.Choice(name="Issues", value="issues"),
                ]
            )
        ]
    )
    async def github(self, ctx, file: str):
        match file:
            case "readme":
                await ctx.send("Detailed information in our README.md\n<https://github.com/spotDL/spotify-downloader/blob/master/README.md>")
            case "installationguide":
                await ctx.send("You can find our Installation Guide at <https://github.com/spotDL/spotify-downloader/blob/master/docs/INSTALLATION.md>")
            case "contributing":
                await ctx.send("You can find our Contributing Guidelines at <https://github.com/spotDL/spotify-downloader/blob/master/docs/CONTRIBUTING.md>")
            case "corevalues":
                await ctx.send("You can find our Core Values at <https://github.com/spotDL/spotify-downloader/blob/master/docs/CORE_VALUES.md>")
            case "license":
                await ctx.send("You can find our Project License at <https://github.com/spotDL/spotify-downloader/blob/master/LICENSE>")
            case "issues":
                await ctx.send("You can find our Issues Page at <https://github.com/spotDL/spotify-downloader/issues>")

    @interactions.extension_command(
        name="youtube",
        description="YouTube Music & spotDL",
        scope=guild_id,
    )
    async def youtube(self, ctx):
        embed = interactions.Embed(
            title="spotDL and YouTube",
            color=0xc4302b,
            image=interactions.EmbedImageStruct(url="https://i.imgur.com/tCaTBTt.png"),
            fields=[
                interactions.EmbedField(
                    name="Quality",
                    value="spotDL automatically gets the highest quality audio from YouTube",
                    inline=False,
                ),
                interactions.EmbedField(
                    name="YouTube Music Required",
                    value="YouTube Music must be available in your country for spotDL to work. This is because we use YouTube Music to filter search results. You can check if YouTube Music is available in your country, by visiting YouTube Music. <https://music.youtube.com/>",
                    inline=False,
                ),
                interactions.EmbedField(
                    name="spotDL Downloads From YouTube",
                    value="spotDL downloads from YouTube if a track is found.",
                    inline=False,
                ),
            ]
        )
        await ctx.send(embeds=embed)

    @interactions.extension_command(
        name="pickyoutube",
        description="How do I download a specific YouTube video with Spotify Metadata?",
        scope=guild_id,
    )
    async def pickyoutube(self, ctx):
        await ctx.send("""You can specify specific YouTube videos to download with Spotify metadata, or vice versa.\nTo do this, use the notation **`spotdl "YouTubeURL|SpotifyURL"`**\nNote that the quote marks (") are essential.""")

    @interactions.extension_command(
        name="zsh",
        description="Special instructions for users using Zsh (Z Shell) terminal",
        scope=guild_id,
    )
    async def zsh(self, ctx):
        await ctx.send('If you use Zsh terminal, **put the URL in quotes**, e.g.\n`spotdl "https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b"`')

    @interactions.extension_command(
        name="podcast",
        description="spotDL cannot download podcasts/episodes from Spotify",
        scope=guild_id,
    )
    async def podcast(self, ctx):
        await ctx.send("spotDL does not support downloading podcasts/episodes from Spotify")

    @interactions.extension_command(
        name="rules",
        description="Prompts for users to follow our rules",
        scope=guild_id,
        options=[
            interactions.Option(
                type=interactions.OptionType.STRING,
                name="rule",
                description="Which prompt?",
                required=True,
                focused=True,
                choices=[
                    interactions.Choice(name="Disabling Reply Pings", value="reply"),
                    interactions.Choice(name="Not Mentioning", value="mention"),
                    interactions.Choice(name="Don't spam issues across channels", value="channel"),
                ]
            )
        ]
    )
    async def rules(self, ctx, rule: str):
        match rule:
            case "reply":
                await ctx.send("**Please disable reply pings**\n\nOur devs are human as well! Please wait patiently, we will reply as soon as we can.\nhttps://i.imgur.com/yIxI1RW.png")
            case "mention":
                await ctx.send("**Please don't ping devs**\n\nOur devs are human as well! Please wait patiently, we will reply as soon as we can.")
            case "channel":
                await ctx.send("**Please don't spam your issue across channels**\n\nOur devs are human as well! Please wait patiently, we will reply as soon as we can.")

    @interactions.extension_command(
        name="admin",
        description="Administration Commands",
        scope=guild_id,
    )
    async def admin(self, ctx):
        button_row = interactions.ActionRow(
            components=[
                interactions.Button(
                    style=interactions.ButtonStyle.DANGER,
                    label="Shutdown Bot",
                    custom_id="shutdown",
                ),
                interactions.Button(
                    style=interactions.ButtonStyle.PRIMARY,
                    label="Restart Bot",
                    custom_id="restart",
                ),
                interactions.Button(
                    style=interactions.ButtonStyle.SECONDARY,
                    label="VPS Info",
                    custom_id="vps",
                ),
            ]
        )
        if int(ctx.author.id) == owner_id:
            await ctx.send("Administration Controls", components=button_row)
        else:
            await ctx.send("You do not have permission to use this command.", ephemeral=True)

    @interactions.extension_component("shutdown")
    async def shutdown(self, ctx):
        if int(ctx.author.id) == owner_id:
            await ctx.edit("Shutting down...", components=None)
            await sys.exit()
        else:
            await ctx.send("You do not have permission to use this command.", ephemeral=True)

    @interactions.extension_component("restart")
    async def restart(self, ctx):
        if int(ctx.author.id) == owner_id:
            await ctx.edit("Restarting...", components=None)
            os.execv(sys.executable, ['python'] + sys.argv)
        else:
            await ctx.send("You do not have permission to use this command.", ephemeral=True)

    @interactions.extension_component("vps")
    async def vps(self, ctx):
        if int(ctx.author.id) == owner_id:
            embed = interactions.Embed(
                title="VPS Info",
                color=0x7289DA,
                fields=[
                    interactions.EmbedField(
                        name="CPU Usage", value=str(psutil.cpu_percent()) + "%", inline=False
                        ),
                    interactions.EmbedField(
                        name="RAM Usage", value=str(psutil.virtual_memory().percent) + "%", inline=False
                        ),
                    interactions.EmbedField(
                        name="Disk Usage", value=str(psutil.disk_usage("/").percent) + "%", inline=False
                        ),
                    interactions.EmbedField(
                        name="System Boot Time", value=str(datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"))
                        ),
                    ],
            )

            await ctx.send(embeds=embed)


def setup(client):
    Commands(client)
