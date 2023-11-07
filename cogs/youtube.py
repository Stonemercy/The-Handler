import requests, shutil, os, googleapiclient.discovery, datetime
from disnake.ext import commands, tasks
from helpers.generators import Embeds
from main import cur, con


# the entire cog for the YouTube function
class Youtube(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.upload_check.start()

    def cog_load(self):
        print("Youtube cog has finished loading")

    def cog_unload(self):
        self.upload_check.stop()

    @tasks.loop(minutes=1)
    async def upload_check(self):
        now = datetime.datetime.now()
        if now.minute not in [0, 15, 30, 45]:
            return

        youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=os.getenv("YOUTUBE_KEY")
        )

        latest_video = (
            youtube.playlistItems()
            .list(part="snippet", playlistId="UUhBCrfYgpz-e0N0zDgQcTLA", maxResults=1)
            .execute()
        )["items"][0]
        video_id = latest_video["snippet"]["resourceId"]["videoId"]
        current_id = cur.execute("Select * from youtube").fetchall()
        if current_id != []:
            current_id = current_id[0][0]
        if video_id == current_id:
            return
        launch_time = (
            youtube.videos().list(part="liveStreamingDetails", id=video_id).execute()
        )["items"][0]["liveStreamingDetails"]["scheduledStartTime"]
        launch_from_iso = datetime.datetime.fromisoformat(launch_time).strftime(
            "%Y-%m-%d"
        )
        if self.latest_video != video_id:
            print("New youtube upload detected, getting thumbnail and link now")
            cur.execute("Delete from youtube")
            cur.execute("Insert into youtube values(?)", (video_id,))
            con.commit()
            thumbnail = latest_video["snippet"]["thumbnails"]["maxres"]["url"]
            thumbnail_name = launch_from_iso
            res = requests.get(thumbnail, stream=True)
            if res.status_code == 200:
                with open(f"{thumbnail_name}.jpg", "wb") as f:
                    shutil.copyfileobj(res.raw, f)
                shutil.move(f"{thumbnail_name}.jpg", f"youtube/{thumbnail_name}.jpg")
                url_file = open("youtube/link.txt", "w")
                url_file.write(f"https://www.youtube.com/watch?v={self.latest_video}")
                url_file.close()
            else:
                return

            channel = self.bot.get_guild(int(os.getenv("GUILD"))).get_channel(
                int(os.getenv("CHANNEL"))
            )
            embed = Embeds.youtube()
            embed.add_field(f"Video title: {latest_video['snippet']['title']}", "")
            embed.set_image(thumbnail)
            await channel.send(f"<@{os.getenv('OWNER')}>", embed=embed)
            # youtube.close()

    @upload_check.before_loop
    async def before_upload_check(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(Youtube(bot))
