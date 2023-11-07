import asyncio, random, os, disnake
from disnake.ext import commands, tasks
from helpers.generators import Embeds
from datetime import datetime
from pyowm.owm import OWM
from helpers.generators import WeatherEmojis

# sets up the weather stuffs
# pyOWM docs: https://pyowm.readthedocs.io/en/latest/index.html
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

    def cog_unload(self):
        self.weather_info.stop()

    @tasks.loop(minutes=1)
    async def weather_info(self):
        now = datetime.now()
        if now.minute != 0 or now.hour not in range(6, 9, 12, 15, 18):
            return
        channel = self.bot.get_guild(int(os.getenv("GUILD"))).get_channel(
            int(os.getenv("CHANNEL"))
        )
        embeds = []
        embed = Embeds.weather()
        random_num = random.random() * 10000
        if random_num == 1000:
            embed.set_image(
                "https://media0.giphy.com/media/J5q4qtKqQ4plPl4YJN/giphy.gif"
            )
            m_one = await channel.send(embed=embed)
            await asyncio.sleep(2)
            m_two = await channel.send("lol jk")
            await asyncio.sleep(2)
            await channel.delete_messages([m_one, m_two])
            embed.set_image("")
        weather_call = weather_mgr.one_call(
            lat=HOME_LAT, lon=HOME_LON, exclude="minutely"
        )
        alerts = weather_call.national_weather_alerts
        current = weather_call.current
        hourly = weather_call.forecast_hourly[0:3]
        if alerts is not None:
            for i in alerts:
                alert_embed = Embeds.weather_alert()
                alert_embed.add_field("Alert from:", i.sender, inline=False).add_field(
                    "Alert name:", i.title, inline=False
                ).add_field("Time start:", i.start).add_field(
                    "Time end:", i.end
                ).add_field(
                    "Description:", i.description, inline=False
                )
            embeds.append(alert_embed)
        embed.add_field(
            "Sunrise:",
            datetime.fromisoformat(current.sunrise_time(timeformat="iso")).strftime(
                "%H:%M"
            ),
        ).add_field(
            "Sunset:",
            datetime.fromisoformat(current.sunset_time(timeformat="iso")).strftime(
                "%H:%M"
            ),
        )
        for hour in hourly:
            time = datetime.fromisoformat(
                str(hour.reference_time(timeformat="iso"))
            ).strftime("%H:%M")
            emoji = WeatherEmojis(hour.status)
            embed.add_field(
                f"{time} - {hour.detailed_status.title()} {emoji}",
                f"Temp: {hour.temperature('celsius')['temp']:.0f}°\n"
                f"Feels like: {hour.temperature('celsius')['feels_like']:.0f}°\n"
                f"Humidity: {hour.humidity}%\n"
                f"Precipitation: {hour.precipitation_probability:.0%}\n"
                f"Windspeed: {hour.wind()['speed']:.0f}mph\n"
                f"Cloud coverage: {hour.clouds:}%\n"
                f"UV Index: {hour.uvi}",
                inline=False,
            )
        embeds.append(embed)
        await channel.send(embeds=embeds)

    @weather_info.before_loop
    async def before_weather_info(self):
        await self.bot.wait_until_ready()

    @commands.slash_command(description="Get the next 3 hours of weather")
    async def weather(self, inter: disnake.ApplicationCommandInteraction):
        embed = Embeds.weather()
        embeds = []
        weather_call = weather_mgr.one_call(
            lat=HOME_LAT, lon=HOME_LON, exclude="minutely"
        )
        alerts = weather_call.national_weather_alerts
        current = weather_call.current
        hourly = weather_call.forecast_hourly[0:3]
        if alerts is not None:
            for i in alerts:
                alert_embed = Embeds.weather_alert()
                alert_embed.add_field("Alert from:", i.sender, inline=False).add_field(
                    "Alert name:", i.title, inline=False
                ).add_field("Time start:", i.start).add_field(
                    "Time end:", i.end
                ).add_field(
                    "Description:", i.description, inline=False
                )
            embeds.append(alert_embed)
        embed.add_field(
            "Sunrise:",
            datetime.fromisoformat(current.sunrise_time(timeformat="iso")).strftime(
                "%H:%M"
            ),
        ).add_field(
            "Sunset:",
            datetime.fromisoformat(current.sunset_time(timeformat="iso")).strftime(
                "%H:%M"
            ),
        )
        for hour in hourly:
            time = datetime.fromisoformat(
                str(hour.reference_time(timeformat="iso"))
            ).strftime("%H:%M")
            emoji = WeatherEmojis(hour.status)
            embed.add_field(
                f"{time} - {hour.detailed_status.title()} {emoji}",
                f"Temp: {hour.temperature('celsius')['temp']:.0f}°\n"
                f"Feels like: {hour.temperature('celsius')['feels_like']:.0f}°\n"
                f"Humidity: {hour.humidity}%\n"
                f"Precipitation: {hour.precipitation_probability:.0%}\n"
                f"Windspeed: {hour.wind()['speed']:.0f}mph\n"
                f"Cloud coverage: {hour.clouds:}%\n"
                f"UV Index: {hour.uvi}",
                inline=False,
            )
        embeds.append(embed)
        await inter.response.send_message(embeds=embeds)


def setup(bot: commands.Bot):
    bot.add_cog(Weather(bot))
