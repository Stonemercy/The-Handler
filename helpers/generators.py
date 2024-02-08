from datetime import datetime
import disnake

blue = disnake.Colour.blue()
green = disnake.Colour.brand_green()
red = disnake.Colour.brand_red()
orange = disnake.Colour.orange()
lighter_grey = disnake.Colour.lighter_grey()


class Embeds:
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
        return disnake.Embed(
            title="Take your meds now", description="Ping Ping Pong", colour=red
        )


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
                    value="49.99",
                    placeholder="e.g. 49.99",
                    custom_id="gas_amount",
                    max_length=5,
                ),
                disnake.ui.TextInput(
                    label="When?",
                    placeholder=now.strftime("%d/%m/%y"),
                    custom_id="gas_date",
                    required=False,
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
    def __init__(self, data, max=3):
        self.alerts = data.national_weather_alerts
        self.current = data.current
        self.hourly = data.forecast_hourly[:max]
