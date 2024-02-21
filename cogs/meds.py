from disnake.ext import commands, tasks
from helpers.classes import Embeds
from datetime import datetime
from os import getenv


class MedsCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.meds.start()
        print("Meds cog has finished loading")

    def cog_unload(self):
        self.meds.stop()

    @tasks.loop(minutes=1)
    async def meds(self):
        now = datetime.now().strftime("%H:%M")
        if now == "16:00":
            self.channel = self.bot.get_channel(int(getenv("CHANNEL")))
            embed = Embeds.meds()
            await self.channel.send(content=f"<@{getenv('OWNER')}>", embed=embed)

    @meds.before_loop
    async def before_meds(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(MedsCommand(bot))
