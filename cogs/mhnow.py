from disnake.ext import commands, tasks
from helpers.generators import Embeds
from datetime import datetime
from os import getenv


class MHNow(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mhnow_spawns.start()
        print("MHNow cog has finished loading")

    def cog_unload(self):
        self.mhnow_spawns.stop()

    @tasks.loop(minutes=1)
    async def mhnow_spawns(self):
        now = datetime.now()
        if now.minute != 0 or now.hour not in [0, 3, 6, 9, 12, 15, 18, 21]:
            return
        channel = self.bot.get_channel(int(getenv("CHANNEL")))
        embed = Embeds.mhnow()
        embed.set_image(
            "https://64.media.tumblr.com/1b024be20ab8a76fda1fce9ab3641540/tumblr_inline_p0tvpnZU0E1t9mqf1_500.gif"
        )
        await channel.send(embed=embed)

    @mhnow_spawns.before_loop
    async def before_mhnow_spawns(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(MHNow(bot))
