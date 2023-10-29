from disnake.ext import commands, tasks
from helpers.generators import embed_gen
from datetime import datetime
from pyowm.owm import OWM
from helpers.generators import WeatherEmojis
import os

# sets up the weather stuffs
API_KEY = str(os.getenv("API_KEY"))
HOME_LAT = float(os.getenv("HOME_LAT"))
HOME_LON = float(os.getenv("HOME_LON"))
owm = OWM(API_KEY)
weather_mgr = owm.weather_manager()


# the entire cog for the weather function
class Weather(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.weather_info.start()

    def cog_load(self):
        print("Weather cog has finished loading")

    @tasks.loop(minutes=1)
    async def weather_info(self):
        now = datetime.now()
        """if now.minute != 0:
            return"""
        channel = self.bot.get_guild(int(os.getenv("GUILD"))).get_channel(
            int(os.getenv("CHANNEL"))
        )
        embed = embed_gen("weather")
        weather_call = weather_mgr.one_call(
            lat=HOME_LAT, lon=HOME_LON, exclude="minutely"
        )
        hourly = weather_call.forecast_hourly[0:6]
        for hour in hourly:
            time = datetime.fromisoformat(
                str(hour.reference_time(timeformat="iso"))
            ).strftime("%H:%M")
            emoji = WeatherEmojis(hour.status)
            temp = hour.temperature("celsius")["temp"]
            feels_like = hour.temperature("celsius")["feels_like"]
            humidity = hour.humidity
            windspeed = hour.wind()["speed"]
            embed.add_field(
                f"{time} - {hour.detailed_status.title()} {emoji}",
                f"Temp: {temp:.0f}°\nFeels like: {feels_like:.0f}°\nHumidity: {humidity}%\nWindspeed: {windspeed:.0f}mph",
                inline=False,
            )

        await channel.send(embed=embed)

    @weather_info.before_loop
    async def before_weather_info(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(Weather(bot))
