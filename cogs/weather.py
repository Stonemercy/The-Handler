from disnake.ext import commands, tasks
from requests import delete
from helpers.generators import Embeds
from datetime import datetime
from pyowm.owm import OWM
from os import getenv
from random import randint
from asyncio import sleep
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
        embed = Embeds.weather()
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
                ).add_field(
                    "Time start:",
                    f"<t:{i.start}:d>",
                ).add_field(
                    "Time end:",
                    f"<t:{i.end}:d>",
                ).add_field(
                    "Description:", i.description, inline=False
                )
            embeds.append(alert_embed)
        embed.add_field(
            "Sunrise:",
            f"<t:{current.sunrise_time(timeformat='unix')}:t>",
        ).add_field(
            "Sunset:",
            f"<t:{current.sunset_time(timeformat='unix')}:t>",
        )
        for hour in hourly:
            time = f"<t:{hour.reference_time(timeformat='unix')}:t>"
            if not hour.snow:
                snow = ""
            else:
                snow = f"Snow: `{hour.snow}`\n"
            embed.add_field(
                f"{time}\n{hour.detailed_status.title()}",
                f"Temp: `{hour.temperature('celsius')['temp']:.0f}°`\n"
                f"Feels like: `{hour.temperature('celsius')['feels_like']:.0f}°`\n"
                f"Humidity: `{hour.humidity}%`\n"
                f"Precipitation: `{hour.precipitation_probability:.0%}`\n"
                f"{snow}"
                f"Windspeed: `{hour.wind('miles_hour')['speed']:.0f}mph`\n"
                f"Gusts: `{hour.wind('miles_hour')['gust']:.0f}mph`\n"
                f"Cloud coverage: `{hour.clouds:}%`\n"
                f"UV Index: `{hour.uvi}`",
            )
        embed.insert_field_at(2, "\u200b", "\u200b")
        embeds.append(embed)
        await channel.send(embeds=embeds)

    @weather_info.before_loop
    async def before_weather_info(self):
        await self.bot.wait_until_ready()

    @commands.slash_command(description="Get the next 3 hours of weather")
    async def weather(self, inter: AppCmdInter):
        embeds = []
        embed = Embeds.weather()
        random_num = randint(1, 10000)
        if random_num == 10000:
            embed.set_image(
                "https://media0.giphy.com/media/J5q4qtKqQ4plPl4YJN/giphy.gif"
            )
            await inter.channel.send(embed=embed)
            await sleep(3)
            await inter.channel.send("haha, just kidding!")
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
                ).add_field(
                    "Time start:",
                    f"<t:{i.start}:d>",
                ).add_field(
                    "Time end:",
                    f"<t:{i.end}:d>",
                ).add_field(
                    "Description:", i.description, inline=False
                )
            embeds.append(alert_embed)
        embed.add_field(
            "Sunrise:",
            f"<t:{current.sunrise_time(timeformat='unix')}:t>",
        ).add_field(
            "Sunset:",
            f"<t:{current.sunset_time(timeformat='unix')}:t>",
        )
        for hour in hourly:
            time = f"<t:{hour.reference_time(timeformat='unix')}:t>"
            if not hour.snow:
                snow = ""
            else:
                snow = f"Snow: `{hour.snow}`\n"
            embed.add_field(
                f"{time}\n{hour.detailed_status.title()}",
                f"Temp: `{hour.temperature('celsius')['temp']:.0f}°`\n"
                f"Feels like: `{hour.temperature('celsius')['feels_like']:.0f}°`\n"
                f"Humidity: `{hour.humidity}%`\n"
                f"Precipitation: `{hour.precipitation_probability:.0%}`\n"
                f"{snow}"
                f"Windspeed: `{hour.wind('miles_hour')['speed']:.0f}mph`\n"
                f"Gusts: `{hour.wind('miles_hour')['gust']:.0f}mph`\n"
                f"Cloud coverage: `{hour.clouds:}%`\n"
                f"UV Index: `{hour.uvi}`",
            )
        embed.insert_field_at(2, "\u200b", "\u200b")
        embeds.append(embed)
        await inter.send(embeds=embeds)


def setup(bot: commands.Bot):
    bot.add_cog(Weather(bot))
