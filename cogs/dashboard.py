from disnake.ext import commands, tasks
from helpers.classes import Embeds, WeatherData
from helpers.db import Dashboard
from datetime import datetime
from os import getenv


class DashboardCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.dashboard.start()
        self.dashboard_weather.start()
        print("Dashboard cog has finished loading")

    def cog_unload(self):
        self.dashboard.stop()
        self.dashboard_weather.stop()

    @tasks.loop(minutes=1)
    async def dashboard(self):
        time = datetime.now()
        info = await Dashboard.get_data()
        channel = self.bot.get_channel(int(getenv("DASHBOARD_CHANNEL")))
        try:
            message = await channel.fetch_message(int(info[0]))
        except:
            message = await channel.send("This is a placeholder")
            result = await Dashboard.set_message_id(message_id=message.id)
            if not result:
                await channel.send("Something broke", delete_after=3000.0)
        embed = Embeds.dashboard_embed()
        embed.description = (
            f"I woke up <t:{info[1]:.0f}:R>\n"
            "[Here](<https://github.com/Stonemercy/The-Handler>) is a link to my github repo\n"
            f"I have {len(self.bot.slash_commands)} commands available\n"
            f"I am currently helping out {len(self.bot.users)} hunters in {len(self.bot.guilds)} guilds\n"
        )
        embed.set_footer(text=f"Last updated at {time.strftime('%H:%M')}")
        message.embeds[0] = embed
        await message.edit(embeds=message.embeds)

    @dashboard.before_loop
    async def before_dashboard(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=1)
    async def dashboard_weather(self):
        time = datetime.now()
        if time.minute != 1:
            return
        info = await Dashboard.get_data()
        channel = self.bot.get_channel(int(getenv("DASHBOARD_CHANNEL")))
        try:
            message = await channel.fetch_message(int(info[0]))
        except:
            return await channel.send("Couldn't add weather", delete_after=300.0)
        weather_data = WeatherData(1)
        message.embeds[1] = weather_data.weather_embed
        await message.edit(embeds=message.embeds)

    @dashboard_weather.before_loop
    async def before_dashboard_weather(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(DashboardCog(bot))
