from datetime import datetime
import disnake
import math
from pyowm.owm import OWM
from os import getenv

blue = disnake.Colour.blue()
green = disnake.Colour.brand_green()
red = disnake.Colour.brand_red()
orange = disnake.Colour.orange()
lighter_grey = disnake.Colour.lighter_grey()


class Embeds:
    def dashboard_embed():
        return disnake.Embed(title="Hunter's Log", colour=green)

    def event_list():
        return disnake.Embed(title="Upcoming events", colour=blue)

    def event_create():
        return disnake.Embed(
            title="Event Created...", description="You nailed it!", colour=green
        )

    def event_warning():
        return disnake.Embed(
            title="Event Warning!",
            description="This event is happening soon!",
            colour=red,
        )

    def weather():
        return disnake.Embed(
            title="Weather Watch",
            description="Here's the latest weather, pard!",
            colour=lighter_grey,
        )

    def weather_alert():
        return disnake.Embed(
            title="Watch out!", description="There's a weather warning!", colour=red
        )

    """def mhnow():
        return disnake.Embed(
            title="Woah!",
            description="The local monsters have migrated!\nTime to cash in on the new population!",
            colour=green,
        )
    
    def mhnow_events():
        return disnake.Embed(
            title="Here are the current reported events", description="", color=green
        )"""

    def youtube():
        return disnake.Embed(
            title="Toonpish Crafts has uploaded a new video",
            description="The url and thumbnail have been downloaded and stored.",
            colour=green,
        )

    def meds():
        return disnake.Embed(title="Take your meds now", description="", colour=red)


class Modals:
    class EventModal(disnake.ui.Modal):
        def __init__(self):
            now = datetime.now()
            components = [
                disnake.ui.TextInput(
                    label="Event name",
                    placeholder="The event's name",
                    custom_id="event_name",
                    max_length=50,
                ),
                disnake.ui.TextInput(
                    label="Event description",
                    placeholder="Description goes here",
                    custom_id="event_desc",
                    style=disnake.TextInputStyle.long,
                    required=False,
                ),
                disnake.ui.TextInput(
                    label="Date",
                    value=now.strftime("%d/%m/%y"),
                    custom_id="event_date",
                ),
                disnake.ui.TextInput(
                    label="Time",
                    value=now.strftime("%H:%M"),
                    custom_id="event_time",
                ),
            ]
            super().__init__(
                title="Submit an event",
                components=components,
                custom_id="event_modal",
            )

    class GasModal(disnake.ui.Modal):
        def __init__(self):
            now = datetime.now()
            components = [
                disnake.ui.TextInput(
                    label="How much?",
                    value="49",
                    placeholder="e.g. 49.99",
                    custom_id="gas_amount",
                    max_length=5,
                ),
                disnake.ui.TextInput(
                    label="When?",
                    value=now.strftime("%d/%m/%y"),
                    custom_id="gas_date",
                ),
            ]
            super().__init__(
                title="So you spent money on gas...",
                components=components,
                custom_id="gas_modal",
            )

    class ElectricityModal(disnake.ui.Modal):
        def __init__(self):
            now = datetime.now()
            components = [
                disnake.ui.TextInput(
                    label="How much?",
                    value="80",
                    placeholder="e.g. 80",
                    custom_id="electricity_amount",
                    max_length=5,
                ),
                disnake.ui.TextInput(
                    label="When?",
                    value=now.strftime("%d/%m/%y"),
                    custom_id="electricity_date",
                ),
            ]
            super().__init__(
                title="So you spent money on electricity...",
                components=components,
                custom_id="electricity_modal",
            )


class WeatherData:
    """Provides embeds based on how many hours are requested

    Parameters
    ----------
    data: `OneCall`
        I use pyowm to obtain this
    hours: `int`
        How many hours of data you want to get back"""

    def __init__(self, hours: int):
        # pyOWM docs: https://pyowm.readthedocs.io/en/latest/index.html
        API_KEY = str(getenv("API_KEY"))
        HOME_LAT = float(getenv("HOME_LAT"))
        HOME_LON = float(getenv("HOME_LON"))
        owm = OWM(API_KEY)
        weather_mgr = owm.weather_manager()
        data = weather_mgr.one_call(lat=HOME_LAT, lon=HOME_LON, exclude="minutely")
        self.alerts = data.national_weather_alerts
        self.current = data.current
        self.hourly = data.forecast_hourly[:hours]
        self.embeds = []
        """The list of embeds for this data set"""
        self.weather_embed = Embeds.weather()
        self.alert_embed = Embeds.weather_alert()

        if self.alerts is not None:
            for i in self.alerts:
                self.alert_embed.add_field(
                    "Alert from:", i.sender, inline=False
                ).add_field("Alert name:", i.title, inline=False).add_field(
                    "Time start:",
                    f"<t:{i.start}:f>",
                ).add_field(
                    "Time end:",
                    f"<t:{i.end}:f>",
                ).add_field(
                    "Description:", "", inline=False
                )
                descriptions = len(i.description) / 1024
                bottom = 0
                top = 1024
                for j in range(math.ceil(descriptions)):
                    self.alert_embed.add_field(
                        "",
                        i.description[bottom:top],
                        inline=False,
                    )
                    bottom = top
                    top = top + top
                    continue
                self.embeds.append(self.alert_embed)

        self.weather_embed.add_field(
            "Sunrise:",
            f"<t:{self.current.sunrise_time(timeformat='unix')}:t>",
        ).add_field(
            "Sunset:",
            f"<t:{self.current.sunset_time(timeformat='unix')}:t>",
        ).add_field(
            "\u200b", "\u200b"
        )

        for hour in self.hourly:
            time = f"<t:{hour.reference_time(timeformat='unix')}:t>"
            if not hour.snow:
                snow = ""
            else:
                snow = f"Snow: `{hour.snow['1h']}mm/h`\n"
            self.weather_embed.add_field(
                f"{time}\n{hour.detailed_status.title()}",
                f"Temp: `{hour.temperature('celsius')['temp']:.0f}°`\n"
                f"Feels like: `{hour.temperature('celsius')['feels_like']:.0f}°`\n"
                f"Humidity: `{hour.humidity}%`\n"
                f"Precipitation: `{hour.precipitation_probability:.0%}`\n"
                f"{snow}"
                f"Windspeed: `{hour.wind('miles_hour')['speed']:.0f}mph`\n"
                f"Gusts: `{hour.wind('miles_hour')['gust']:.0f}mph`\n"
                f"UV Index: `{hour.uvi}`",
            )
        self.embeds.append(self.weather_embed)
