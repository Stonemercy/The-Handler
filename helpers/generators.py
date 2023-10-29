import disnake
from disnake import TextInputStyle
import datetime


# generator for embeds
def embed_gen(embed_type: str):
    if embed_type == "list":
        embed = disnake.Embed(title="Upcoming events", colour=disnake.Colour.blue())
        return embed
    elif embed_type == "event_creation":
        embed = disnake.Embed(
            title="Event created...",
            description="You nailed it!",
            colour=disnake.Colour.green(),
        )
        return embed
    elif embed_type == "event_hour":
        embed = disnake.Embed(
            title="ONE HOUR WARNING",
            description="WATCH OUT PARD",
            colour=disnake.Colour.brand_red(),
        )
        return embed
    elif embed_type == "weather":
        embed = disnake.Embed(
            title="Daily weather watch",
            description="Here's the daily forecast for Belfast",
            colour=disnake.Colour.lighter_grey(),
        )
        return embed


def modal_gen(modal_type: str):
    if modal_type == "event":

        class EventModal(disnake.ui.Modal):
            def __init__(self):
                components = [
                    disnake.ui.TextInput(
                        label="Event name",
                        placeholder="The event's name",
                        custom_id="event_name",
                        style=TextInputStyle.short,
                        max_length=50,
                    ),
                    disnake.ui.TextInput(
                        label="Event description",
                        placeholder="Description goes here",
                        custom_id="event_desc",
                        style=TextInputStyle.long,
                    ),
                    disnake.ui.TextInput(
                        label="Date",
                        placeholder="07/04/16",
                        custom_id="event_date",
                        style=TextInputStyle.short,
                    ),
                    disnake.ui.TextInput(
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
        time_list.append(datetime.datetime.strptime(time_zero, "%H:%M").time())
        time_list.append(datetime.datetime.strptime(time_half, "%H:%M").time())
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
