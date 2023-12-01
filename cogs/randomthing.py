from random import randint
from disnake.ext import commands, tasks
from os import getenv


class RandomThingsCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.im_hungry.start()
        print("Random things cog has finished loading")

    def cog_unload(self):
        self.im_hungry.stop()

    # loop that runs at 1pm
    @tasks.loop(minutes=1)
    async def im_hungry(self):
        randomnum = randint(0, 10000)
        if randomnum == 10000:
            self.channel = self.bot.get_channel(int(getenv("CHANNEL")))
            await self.channel.send(content=f"I'm hungry...")

    @im_hungry.before_loop
    async def before_meds(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(RandomThingsCommand(bot))
