from disnake.ext import commands, tasks
from helpers.generators import Embeds
from datetime import datetime
from os import getenv


# the entire cog for the invasions command
class MedsCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.meds.start()

    def cog_load(self):
        print("Meds cog has finished loading")

    def cog_unload(self):
        self.meds.stop()

    # loop that runs at midday for 3-4 times (gotta check)
    @tasks.loop(seconds=15)
    async def meds(self):
        self.channel = self.bot.get_guild(int(getenv("GUILD"))).get_channel(
            int(getenv("CHANNEL"))
        )
        now = datetime.now()
        if now.hour == 12 and now.minute == 00:
            embed = Embeds.meds()
            await self.channel.send(content=f"<@{getenv('OWNER')}>", embed=embed)

    @meds.before_loop
    async def before_invasions_ping(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(MedsCommand(bot))
