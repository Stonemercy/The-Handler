from disnake import AppCmdInter
from disnake.ext import commands, tasks
from helpers.generators import Embeds
from helpers.db import MHNow
from helpers.functions import get_date_format
from datetime import datetime
from os import getenv


class MHNowCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mhnow_spawns.start()
        self.mhnow_event_purge.start()
        print("MHNow cog has finished loading")

    def cog_unload(self):
        self.mhnow_spawns.stop()
        self.mhnow_event_purge.stop()

    @tasks.loop(minutes=1)
    async def mhnow_spawns(self):
        now = datetime.now()
        if now.minute != 0 or now.hour not in [0, 3, 6, 9, 12, 15, 18, 21]:
            return
        channel = self.bot.get_channel(int(getenv("CHANNEL")))
        embed = Embeds.mhnow()
        embed.set_image(
            "https://64.media.tumblr.com/1b024be20ab8a76fda1fce9ab3641540/tumblr_inline_p0tvpnZU0E1t9mqf1_500.gif"
        )
        await channel.send(embed=embed)

    @tasks.loop(minutes=1)
    async def mhnow_event_purge(self):
        deleted_list = await MHNow.delete_old()
        channel = self.bot.get_channel(int(getenv("CHANNEL")))
        if not deleted_list:
            return
        else:
            for i in deleted_list:
                await channel.send(f"`{i}` has ended!")

    @mhnow_event_purge.before_loop
    @mhnow_spawns.before_loop
    async def before_mhnow_spawns(self):
        await self.bot.wait_until_ready()

    @commands.slash_command()
    async def mhnow(self, inter: AppCmdInter):
        pass

    @mhnow.sub_command(description="List events")
    async def list(self, inter: AppCmdInter):
        events = await MHNow.all()
        if not events:
            return await inter.send("There are no events :(")
        else:
            embed = Embeds.mhnow_events()
            for i in events:
                embed.add_field(
                    i[2],
                    f"""{i[3]}
                    Starts <t:{int(datetime.fromisoformat(i[0]).timestamp())}:R>
                    Ends <t:{int(datetime.fromisoformat(i[1]).timestamp())}:R>""",
                )
                continue
            return await inter.send(embed=embed)

    @mhnow.sub_command(description="Add a new event")
    async def report(
        inter: AppCmdInter,
        start_time: str,
        end_time: str,
        event_name: str,
        event_desc: str,
    ):
        start_datetime = get_date_format(start_time)
        end_datetime = get_date_format(end_time)
        new_event = await MHNow.new_event(
            start_datetime, end_datetime, event_name, event_desc
        )
        if not new_event:
            return await inter.send(
                "That didn't seem to work, try again.", ephemeral=True
            )
        else:
            embed = Embeds.mhnow_events()
            all_events = await MHNow.all()
            for i in all_events:
                embed.add_field(
                    i[2],
                    f"""{i[3]}
                    Start time: <t:{int(datetime.fromisoformat(i[0]).timestamp())}:R>
                    End time: <t:{int(datetime.fromisoformat(i[1]).timestamp())}:R>""",
                )
                continue
            return await inter.send(
                """New event created!
                Here's the reported events:""",
                embed=embed,
            )

    @mhnow.sub_command(description="Delete an event")
    async def delete(inter: AppCmdInter, event_name: str):
        delete = await MHNow.delete_event(event_name)
        if not delete:
            return await inter.send("That command didn't work", ephemeral=True)
        else:
            return await inter.send(f"Deleted the event `{event_name}`")


def setup(bot: commands.Bot):
    bot.add_cog(MHNowCommand(bot))
