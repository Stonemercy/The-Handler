from disnake.ext import commands, tasks
from helpers.classes import WeatherData
from datetime import datetime

from os import getenv
from disnake import AppCmdInter


class Weather(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.weather_info.start()
        print("Weather cog has finished loading")

    def cog_unload(self):
        self.weather_info.stop()

    @tasks.loop(minutes=1)
    async def weather_info(self):
        now = datetime.now()
        if now.minute != 0 or now.hour not in [6, 9, 12, 15, 18]:
            return
        channel = self.bot.get_channel(int(getenv("CHANNEL")))

        weather_data = WeatherData(3)
        await channel.send(embeds=weather_data.embeds)

    @weather_info.before_loop
    async def before_weather_info(self):
        await self.bot.wait_until_ready()

    @commands.slash_command(description="Get weather for `x` amount of hours")
    async def weather(
        self,
        inter: AppCmdInter,
        hours: int = commands.Param(
            lt=22,
            gt=0,
            default=3,
            description="How many hours in the future you want to check",
        ),
    ):
        weather_data = WeatherData(hours)
        await inter.send(embeds=weather_data.embeds)


def setup(bot: commands.Bot):
    bot.add_cog(Weather(bot))
