from datetime import datetime
import disnake

blue = disnake.Colour.blue()
green = disnake.Colour.brand_green()
red = disnake.Colour.brand_red()
orange = disnake.Colour.orange()
lighter_grey = disnake.Colour.lighter_grey()


class Embeds:
    def list():
        embed = disnake.Embed(title="Upcoming events", colour=blue)
        return embed

    def event_create():
        embed = disnake.Embed(
            title="Event Created...", description="You nailed it!", colour=green
        )
        return embed

    def event_warning():
        embed = disnake.Embed(
            title="Event Warning!",
            description="This event is happening soon!",
            colour=red,
        )
        return embed

    def weather():
        embed = disnake.Embed(
            title="Weather Watch",
            description="Here's the latest weather, pard!",
            colour=lighter_grey,
        )
        return embed

    def weather_alert():
        embed = disnake.Embed(
            title="Watch out!", description="There's a weather warning!", colour=red
        )
        return embed

    def mhnow():
        embed = disnake.Embed(
            title="Woah!",
            description="The local monsters have migrated!\nTime to cash in on the new population!",
            colour=green,
        )
        return embed

    def youtube():
        embed = disnake.Embed(
            title="Toonpish Crafts has uploaded a new video",
            description="The url and thumbnail have been downloaded and stored (I need to find a way to upload them)",
            colour=green,
        )
        return embed

    def meds():
        embed = disnake.Embed(
            title="Take your meds now", description="Ping Ping Pong", colour=red
        )
        return embed


def event_report_modal():
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
                    placeholder="07/04/16",
                    custom_id="event_date",
                ),
                disnake.ui.TextInput(
                    label="Time",
                    value=now.replace(minute=0, hour=now.hour + 1).strftime("%H:%M"),
                    placeholder="18:00 (just hours and minutes)",
                    custom_id="event_time",
                ),
            ]
            super().__init__(
                title="Submit an event",
                components=components,
                custom_id="event_modal",
            )

    return EventModal()


def gas_report_modal():
    class GasModal(disnake.ui.Modal):
        def __init__(self):
            components = [
                disnake.ui.TextInput(
                    label="How much?",
                    value="49.99",
                    placeholder="e.g. 49.99",
                    custom_id="gas_amount",
                    max_length=5,
                ),
            ]
            super().__init__(
                title="So you spent money on gas...",
                components=components,
                custom_id="gas_modal",
            )

    return GasModal()


def electricity_report_modal():
    class ElectricityModal(disnake.ui.Modal):
        def __init__(self):
            components = [
                disnake.ui.TextInput(
                    label="How much?",
                    value="80",
                    placeholder="e.g. 80",
                    custom_id="electricity_amount",
                    max_length=5,
                ),
            ]
            super().__init__(
                title="So you spent money on electricity...",
                components=components,
                custom_id="electricity_modal",
            )

    return ElectricityModal()


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
