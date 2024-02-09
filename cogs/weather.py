from disnake.ext import commands, tasks
from helpers.generators import Embeds, WeatherData
from datetime import datetime
from pyowm.owm import OWM
from os import getenv
from disnake import AppCmdInter

# pyOWM docs: https://pyowm.readthedocs.io/en/latest/index.html
API_KEY = str(getenv("API_KEY"))
HOME_LAT = float(getenv("HOME_LAT"))
HOME_LON = float(getenv("HOME_LON"))
owm = OWM(API_KEY)
weather_mgr = owm.weather_manager()


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
        embeds = []
        weather_embed = Embeds.weather()
        weather_call = weather_mgr.one_call(
            lat=HOME_LAT, lon=HOME_LON, exclude="minutely"
        )
        weather_data = WeatherData(weather_call, 3)
        weather_data.add_weather_alerts(Embeds.weather_alert(), embeds)
        weather_data.add_suns(weather_embed)
        weather_data.add_weather(weather_embed)
        embeds.append(weather_embed)
        await channel.send(embeds=embeds)

    @weather_info.before_loop
    async def before_weather_info(self):
        await self.bot.wait_until_ready()

    @commands.slash_command(description="Get weather for `x` amount of hours")
    async def weather(self, inter: AppCmdInter, hours: int = 3):
        embeds = []
        weather_embed = Embeds.weather()
        weather_call = weather_mgr.one_call(
            lat=HOME_LAT, lon=HOME_LON, exclude="minutely"
        )
        weather_data = WeatherData(weather_call, hours)
        weather_data.add_weather_alerts(Embeds.weather_alert(), embeds)
        weather_data.add_suns(weather_embed)
        weather_data.add_weather(weather_embed)
        embeds.append(weather_embed)
        await inter.send(embeds=embeds)


def setup(bot: commands.Bot):
    bot.add_cog(Weather(bot))
