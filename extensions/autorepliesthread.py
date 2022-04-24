import interactions
from credentials import help_channel

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

                # Create the thread and send the start message (as above)
                thread = await msg.create_thread(name=f"{msg.author.username}'s Help Thread")
                await thread.send(thread_start_msg)

            """AUTOREPLIES SECTION"""

            STAFF_PING = """I have detected that you pinged the Moderation team!
Please note that this is ONLY for moderation purposes, and should not be used for spotDL assistance.
The moderation team may not be able to assist you. Please refer to <#796939712828801074>, <#797661959037780019> and if you need to, <#796571887635267614>
**Remember our teams are human as well! Please wait patiently, we will reply as soon as we can.**"""

            message = msg.content.lower()

            if "dll load failed" in message:
                message_for_sending = ("On Windows? You need to install Visual C++ 2019 redistributable\nhttps://docs.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist")
            elif "unable to get audio stream" in message:
                message_for_sending = ("On OSX? You need to install SSL certificates\nNavigate to `Applications/Python 3.9`, and double click `Install Certificates.command`\n(Change 3.9 to relevant version number)")
            elif "could not match any of the results on youtube" in message:
                message_for_sending = ("**YouTube Music must be available in your country for spotDL to work. This is because we use YouTube Music to filter search results. You can check if YouTube Music is available in your country, by visiting YouTube Music.** <https://music.youtube.com/>")
            elif "&dl_branch=1" in message or "&utm_source" in message:
                message_for_sending = ("**You must remove `&dl_branch=1`/`&utm_source` from URLs, since the `&` is a control operator in terminal**")
            elif "<@&798504444534587412>" in message:
                await msg.create_reaction("\U0001F6A8")  # 🚨
                await msg.create_reaction("ping:896186295771095040")  # Pinged emoji
                message_for_sending = (STAFF_PING)
            elif "'spotdl' is not recognized" in message:
                msg = "You need to install Python from <https://www.python.org/downloads/>\n\nEnsure to add to PATH when installing:\nhttps://i.imgur.com/jWq5EnV.png"
                message_for_sending = (f"**Python/(site packages) is not added to PATH correctly.**\n{msg} ")
            elif "error: http error 410: gone" in message:
                message_for_sending = ("This error has been patched. Update spotDL - `pip install -U --force spotdl`")
            elif "requests>=2.25.0" in message:
                message_for_sending = ("Outdated packages. `pip install -U --force requests urllib3 chardet`\nChange `pip` to `pip3` if running *UNIX")


            """SENDING AUTOREPLY"""
            if int(msg.channel_id) != int(help_channel):
                # Reply to msgs in every channel EXCEPT help channel (due to autothread)
                await msg.reply(message_for_sending)
            else:
                # If message in help channel, send the prompt in the created thread.
                await thread.send(f"_ _\n\n**Automatic Prompt for {msg.author.username}:**\n{message_for_sending}")        


def setup(client):
    AutoRepliesThread(client)
