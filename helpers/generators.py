from disnake.ui import Modal
from disnake import TextInput, TextInputStyle, Colour, Embed
from datetime import datetime

blue = Colour.blue()
green = Colour.brand_green()
red = Colour.brand_red()
orange = Colour.orange()
lighter_grey = Colour.lighter_grey()


class Embeds:
    def __init__(self, event_warning_time: str = None):
        self.e_w_t = event_warning_time
        pass

    def list():
        embed = Embed(title="Upcoming events", colour=blue)
        return embed

    def event_create():
        embed = Embed(
            title="Event Created...", description="You nailed it!", colour=green
        )
        return embed

    def weather():
        embed = Embed(
            title="Weather Watch",
            description="Here's the latest weather, pard!",
            colour=lighter_grey,
        )
        return embed

    def weather_alert():
        embed = Embed(
            title="Watch out!", description="There's a weather warning!", colour=red
        )
        return embed

    def mhnow():
        embed = Embed(
            title="Woah!",
            description="The local monsters have migrated!\nTime to cash in on the new population!",
            colour=green,
        )
        return embed

    def youtube():
        embed = Embed(
            title="Toonpish Crafts has uploaded a new video",
            description="The url and thumbnail have been downloaded and stored (I need to find a way to upload them)",
            colour=green,
        )
        return embed

    def meds():
        embed = Embed(
            title="Take your meds now", description="Ping Ping Pong", colour=red
        )
        return embed

    class EventWarning:
        def hour():
            embed = Embed(
                title="Event Warning!", description="1 hour notification!", colour=red
            )
            return embed

        def day():
            embed = Embed(
                title="Event Warning!",
                description="1 day notification!",
                colour=orange,
            )
            return embed

        def week():
            embed = Embed(
                title="Event Warning!",
                description="1 week notification!",
                colour=orange,
            )
            return embed


def modal_gen(modal_type: str):
    if modal_type == "event":

        class EventModal(Modal):
            def __init__(self):
                components = [
                    TextInput(
                        label="Event name",
                        placeholder="The event's name",
                        custom_id="event_name",
                        style=TextInputStyle.short,
                        max_length=50,
                    ),
                    TextInput(
                        label="Event description",
                        placeholder="Description goes here",
                        custom_id="event_desc",
                        style=TextInputStyle.long,
                    ),
                    TextInput(
                        label="Date",
                        placeholder="07/04/16",
                        custom_id="event_date",
                        style=TextInputStyle.short,
                    ),
                    TextInput(
                        label="Time",
                        placeholder="18:00",
                        custom_id="event_time",
                        style=TextInputStyle.short,
                    ),
                ]
                super().__init__(
                    title="Submit an event",
                    components=components,
                    custom_id="event_modal",
                )

        return EventModal()


def time_list_gen():
    time_list = []
    for i in range(0, 12):
        if len(i) == 1:
            j = "0" + str(i)
        time_zero = f"{j}:00"
        time_half = f"{j}:30"
        time_list.append(datetime.strptime(time_zero, "%H:%M").time())
        time_list.append(datetime.strptime(time_half, "%H:%M").time())
    return time_list


def WeatherEmojis(weather: str = "Clear"):
    if weather == "Thunderstorm":
        return "⛈️"
    elif weather == "Drizzle":
        return "🌦️"
    elif weather == "Rain":
        return "🌧️"
    elif weather == "Snow":
        return "🌨️"
    elif weather == "Mist" or weather == "Fog":
        return "🌫️"
    elif weather == "Clear":
        return "☀️"
    elif weather == "Clouds":
        return "☁️"
