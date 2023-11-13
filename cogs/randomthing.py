import random
from disnake.ext import commands, tasks
from os import getenv


# the entire cog for the invasions command
class RandomThingsCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.im_hungry.start()

    def cog_load(self):
        print("Random things cog has finished loading")

    def cog_unload(self):
        self.im_hungry.stop()

    # loop that runs at 1pm
    @tasks.loop(minutes=1)
    async def im_hungry(self):
        randomnum = random.randint(0, 10000)
        if randomnum == 10000:
            self.channel = self.bot.get_guild(int(getenv("GUILD"))).get_channel(
                int(getenv("CHANNEL"))
            )
            message = await self.channel.send(content=f"I'm hungry...")
            await message.delete(delay=3.0)

    @im_hungry.before_loop
    async def before_meds(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(RandomThingsCommand(bot))
