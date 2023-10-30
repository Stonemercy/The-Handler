from disnake.ext import commands, tasks
from helpers.generators import embed_gen
from main import cur, con
import requests, shutil, os, scrapetube


# the entire cog for the MHNow function
class Youtube(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.upload_check.start()
        current_id = cur.execute("Select * from youtube").fetchall()
        if current_id != []:
            self.latest_video = current_id[0][0]
        else:
            self.latest_video = "None"

    def cog_load(self):
        print("Youtube cog has finished loading")

    def cog_unload(self):
        self.upload_check.stop()

    @tasks.loop(seconds=10)
    async def upload_check(self):
        videos = scrapetube.get_channel(channel_url=str(os.getenv("YOUTUBE")), limit=1)
        latest_video = videos.send(None)
        if self.latest_video != latest_video["videoId"]:
            print("New youtube upload detected, getting thumbnail and link now")
            self.latest_video = latest_video["videoId"]
            cur.execute("Delete from youtube")
            cur.execute("Insert into youtube values(?)", (self.latest_video,))
            con.commit()
            url = f"https://img.youtube.com/vi/{self.latest_video}/maxresdefault.jpg"
            file_name = "thumbnail.jpg"
            res = requests.get(url, stream=True)
            if res.status_code == 200:
                with open(file_name, "wb") as f:
                    shutil.copyfileobj(res.raw, f)
                shutil.move(file_name, f"youtube/{file_name}")
            url_file = open("youtube/link.txt", "w")
            url_file.write(f"https://www.youtube.com/watch?v={self.latest_video}")
            url_file.close()
        else:
            return

        channel = self.bot.get_guild(int(os.getenv("GUILD"))).get_channel(
            int(os.getenv("CHANNEL"))
        )
        embed = embed_gen("youtube")
        await channel.send(f"<@{os.getenv('OWNER')}>", embed=embed)

    @upload_check.before_loop
    async def before_upload_check(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(Youtube(bot))
