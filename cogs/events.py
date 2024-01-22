from disnake import AppCmdInter, ModalInteraction
from disnake.ext import commands, tasks
from helpers.functions import get_datetime
from helpers.generators import Embeds, Modals
from helpers.db import Events
from datetime import datetime
from os import getenv


class EventsCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.event_check.start()
        print("Events cog has finished loading")

    def cog_unload(self):
        self.event_check.stop()

    @tasks.loop(minutes=1)
    async def event_check(self):
        now = datetime.now()
        await Events.purge(now)
        if now.minute != 0 or now.hour not in [9, 12, 17, 21]:
            return
        channel = self.bot.get_channel(int(getenv("CHANNEL")))
        embeds = await Events.warnings(now)
        if not embeds:
            return
        else:
            await channel.send(content="# Upcoming events:", embeds=embeds)

    @event_check.before_loop
    async def before_event_check(self):
        await self.bot.wait_until_ready()

    @commands.slash_command()
    async def events(self, inter: AppCmdInter):
        pass

    @events.sub_command(description="List events")
    async def list(self, inter: AppCmdInter):
        embed = Embeds.event_list()
        current_events = await Events.all()

        if not current_events:
            embed.add_field("Looks like there are no upcoming events, pard.", "")
            return await inter.response.send_message(embed=embed)
        for i in current_events:
            time = get_datetime(" ".join([i[0], i[1]]))
            print(time)
            if time < datetime.now():
                continue
            submitter = await inter.guild.fetch_member(i[4])
            embed.add_field(
                f"{time.strftime('%d/%m/%y - %H:%M')}",
                f"**__{i[2]}__**\n{i[3]}\nSubmitted by {submitter.mention}\n\u200b",
                inline=False,
            )
            continue
        await inter.send(embed=embed)

    @events.sub_command(description="Report an event")
    async def report(inter: AppCmdInter):
        modal = Modals.EventModal()
        await inter.response.send_modal(modal)

    @commands.Cog.listener("on_modal_submit")
    async def event_listener(self, inter: ModalInteraction):
        if inter.custom_id != "event_modal":
            return
        else:
            embed = Embeds.event_create()
            event_name, event_desc, event_date, event_time = inter.text_values.values()
            if event_desc == "":
                event_desc = "No description"

            event_dt = get_datetime(event_date + " " + event_time)
            if not event_dt:
                return await inter.send(
                    "The provided date or time wasnt in the correct format of **dd/mm/yy** or **HH:MM**.\nPlease try again."
                )

            await Events.submit(
                event_date,
                event_time,
                event_name,
                inter.author.id,
                event_desc,
            )
            event = await Events.specific(event_name)
            embed.add_field(
                "Event date and time:",
                event[0] + " " + event[1],
                inline=False,
            ).add_field("Event name:", event[2], inline=False).add_field(
                "Event description:", event[3], inline=False
            )
            await inter.send(embed=embed)

    @events.sub_command(description="Delete an event")
    async def delete(
        inter: AppCmdInter,
        event_name: str = commands.Param(
            description="The name of the event you want to delete"
        ),
    ):
        deleted = await Events.delete(event_name)
        if not deleted:
            await inter.response.send_message("Something went wrong")
        else:
            await inter.response.send_message(f"Deleted event `{event_name}`")


def setup(bot: commands.Bot):
    bot.add_cog(EventsCommand(bot))
