from disnake.ext import commands, tasks
from helpers.db import YouTube
from helpers.generators import Embeds
from datetime import datetime
from googleapiclient import discovery
from os import getenv
from requests import get
from shutil import copyfileobj, move


class Youtube(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.upload_check.start()
        print("Youtube cog has finished loading")

    def cog_unload(self):
        self.upload_check.stop()

    @tasks.loop(minutes=1)
    async def upload_check(self):
        now = datetime.now()
        if now.minute not in [0, 15, 30, 45]:
            return
        youtube = discovery.build("youtube", "v3", developerKey=getenv("YOUTUBE_KEY"))
        latest_video = (
            youtube.playlistItems()
            .list(part="snippet", playlistId="UUhBCrfYgpz-e0N0zDgQcTLA", maxResults=1)
            .execute()
        )["items"][0]
        video_id = latest_video["snippet"]["resourceId"]["videoId"]
        current_id = await YouTube.current_id()
        if current_id is False or current_id == video_id:
            return
        else:
            print("New youtube upload detected, getting thumbnail and link now")
            channel = self.bot.get_guild(int(getenv("GUILD"))).get_channel(
                int(getenv("CHANNEL"))
            )
            launch_time = (
                youtube.videos()
                .list(part="liveStreamingDetails", id=video_id)
                .execute()
            )["items"][0]["liveStreamingDetails"]["scheduledStartTime"]
            launch_from_iso = datetime.fromisoformat(launch_time).strftime("%Y-%m-%d")
            await YouTube.new_code(video_id)
            thumbnail_url = latest_video["snippet"]["thumbnails"]["maxres"]["url"]
            thumbnail_name = launch_from_iso
            res = get(thumbnail_url, stream=True)
            if res.status_code == 200:
                with open(f"{thumbnail_name}.jpg", "wb") as f:
                    copyfileobj(res.raw, f)
                move(f"{thumbnail_name}.jpg", f"youtube/{thumbnail_name}.jpg")
                url_file = open("youtube/link.txt", "w")
                url_file.write(f"https://www.youtube.com/watch?v={video_id}")
                url_file.close()
            else:
                channel.send("I had trouble getting the thumbnail")

            embed = Embeds.youtube()
            embed.add_field(
                f"Video title:",
                f"[{latest_video['snippet']['title']}](https://www.youtube.com/watch?v={video_id})",
            )
            embed.set_image(thumbnail_url)
            await channel.send(f"<@{getenv('OWNER')}>", embed=embed)

    @upload_check.before_loop
    async def before_upload_check(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(Youtube(bot))
