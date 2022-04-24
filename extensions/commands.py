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

def setup(client):
    Commands(client)
