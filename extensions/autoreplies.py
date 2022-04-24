import interactions

class AutoReplies(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

    @interactions.extension_listener()
    async def on_message_create(self, msg):
        # Only reply if  msg is not sent by a bot.
        if not msg.author.bot:
            message = msg.content.lower()

            staff_ping = """I have detected that you pinged the Moderation team!
Please note that this is ONLY for moderation purposes, and should not be used for spotDL assistance.
The moderation team may not be able to assist you. Please refer to <#796939712828801074>, <#797661959037780019> and if you need to, <#796571887635267614>
**Remember our teams are human as well! Please wait patiently, we will reply as soon as we can.**"""

            if "dll load failed" in message:
                await msg.reply("On Windows? You need to install Visual C++ 2019 redistributable\nhttps://docs.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist")
            elif "unable to get audio stream" in message:
                await msg.reply("On OSX? You need to install SSL certificates\nNavigate to `Applications/Python 3.9`, and double click `Install Certificates.command`\n(Change 3.9 to relevant version number)")
            elif "could not match any of the results on youtube" in message:
                await msg.reply("**YouTube Music must be available in your country for spotDL to work. This is because we use YouTube Music to filter search results. You can check if YouTube Music is available in your country, by visiting YouTube Music.** <https://music.youtube.com/>")
            elif "&dl_branch=1" in message or "&utm_source" in message:
                await msg.reply("**You must remove `&dl_branch=1`/`&utm_source` from URLs, since the `&` is a control operator in terminal**")
            elif "<@&798504444534587412>" in message:
                await msg.create_reaction("\U0001F6A8")  # 🚨
                await msg.create_reaction("ping:896186295771095040")  # Pinged emoji
                await msg.reply(staff_ping)
            elif "'spotdl' is not recognized" in message:
                msg = "You need to install Python from <https://www.python.org/downloads/>\n\nEnsure to add to PATH when installing:\nhttps://i.imgur.com/jWq5EnV.png"
                await msg.reply(f"**Python/(site packages) is not added to PATH correctly.**\n{msg} ")
            elif "error: http error 410: gone" in message:
                await msg.reply("This error has been patched. Update spotDL - `pip install -U --force spotdl`")
            elif "requests>=2.25.0" in message:
                await msg.reply("Outdated packages. `pip install -U --force requests urllib3 chardet`\nChange `pip` to `pip3` if running *UNIX")




def setup(client):
    AutoReplies(client)
