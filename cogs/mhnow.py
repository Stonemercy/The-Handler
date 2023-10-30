from disnake.ext import commands, tasks
from helpers.generators import embed_gen
from datetime import datetime
import os


# the entire cog for the MHNow function
class MHNow(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.MHNow_spawns.start()

    def cog_load(self):
        print("MHNow cog has finished loading")

    def cog_unload(self):
        self.MHNow_spawns.stop()

    @tasks.loop(minutes=1)
    async def MHNow_spawns(self):
        now = datetime.now()
        if now.minute != 0 and now.hour not in [1, 4, 7, 10]:
            return
        channel = self.bot.get_guild(int(os.getenv("GUILD"))).get_channel(
            int(os.getenv("CHANNEL"))
        )
        embed = embed_gen("MHNow")
        embed.set_image(
            "https://64.media.tumblr.com/1b024be20ab8a76fda1fce9ab3641540/tumblr_inline_p0tvpnZU0E1t9mqf1_500.gif"
        )
        await channel.send(embed=embed)

    @MHNow_spawns.before_loop
    async def before_weather_info(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(MHNow(bot))
