from disnake import AppCmdInter, ModalInteraction
from disnake.ext import commands, tasks
from helpers.generators import Embeds, event_report_modal
from datetime import datetime
from os import getenv
from data.db import Events


# the entire cog for the invasions command
class EventsCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.event_check.start()

    def cog_load(self):
        print("Events cog has finished loading")

    def cog_unload(self):
        self.event_check.stop()

    async def warning(self, events):
        self.channel = self.bot.get_guild(int(getenv("GUILD"))).get_channel(
            int(getenv("CHANNEL"))
        )
        for event in events:
            unit = await Events.warnings(event)
            if unit is None:
                continue
            embed = Embeds.event_warning()
            submitter = await self.bot.fetch_user(event[3])
            embed.description = f"This event is happening within 1 {unit}:"
            embed.add_field(event[1], event[2]).add_field(
                "Submitted by:", f"{submitter.mention}", inline=False
            )
            await self.channel.send(embed=embed)

    @tasks.loop(minutes=1)
    async def event_check(self):
        current_events = await Events.all()
        if current_events != []:
            await self.warning(current_events)
            await Events.purge()

    @event_check.before_loop
    async def before_event_check(self):
        await self.bot.wait_until_ready()

    # events parent command
    @commands.slash_command()
    async def events(self, inter: AppCmdInter):
        pass

    # events list subcommand
    @events.sub_command(description="List events")
    async def list(self, inter: AppCmdInter):
        embed = Embeds.list()
        current_events = await Events.all()

        if current_events == []:
            embed.add_field("Looks like there are no upcoming events, pard.", "")
            await inter.response.send_message(embed=embed)
        else:
            for event in current_events:
                if datetime.fromisoformat(event[0]) < datetime.now():
                    continue
                time = datetime.fromisoformat(event[0]).strftime("%d/%m/%Y - %H:%M")
                submitter = await inter.guild.fetch_member(event[3])
                embed.add_field(
                    f"{time}",
                    f"**__{event[1]}__**\n**Description:**\n{event[2]}\nSubmitted by {submitter.mention}\n\u200b",
                    inline=False,
                )

            await inter.response.send_message(embed=embed)

    # event report subcommand
    @events.sub_command(description="Report an event")
    async def report(inter: AppCmdInter):
        """Submit an event"""
        modal = event_report_modal()
        await inter.response.send_modal(modal)

    # listener for event modal
    @commands.Cog.listener("on_modal_submit")
    async def event_listener(self, inter: ModalInteraction):
        if inter.custom_id != "event_modal":
            return
        else:
            embed = Embeds.event_create()
            event_name, event_desc, event_date, event_time = inter.text_values.values()
            if event_desc == "":
                event_desc = "No description"
            event_check = await Events.specific(event_name)
            if event_check is not None:
                await inter.send(
                    "An event with this name has already been reported, pard\nCheck the list!",
                    ephemeral=True,
                    delete_after=5.0,
                )
                return
            event_date_and_time = datetime.combine(
                datetime.strptime(event_date, "%d/%m/%y"),
                datetime.time(datetime.strptime(event_time, "%H:%M")),
            ).replace(second=0)
            await Events.submit(
                event_date_and_time,
                event_name,
                inter.author.id,
                event_desc,
            )
            event_confirm = await Events.specific(event_name)
            embed.add_field(
                "Event date and time:",
                f"{datetime.fromisoformat(event_confirm[0]).strftime('%d/%m/%y - %H:%M')}",
                inline=False,
            ).add_field("Event name:", event_confirm[1], inline=False).add_field(
                "Event description:", event_confirm[2], inline=False
            )
            await inter.send(embed=embed)

    # delete command
    @events.sub_command(description="Delete an event")
    async def delete(inter: AppCmdInter, event_name: str):
        """Delete an event"""
        deleted = await Events.delete(event_name)
        if not deleted:
            await inter.response.send_message("Something went wrong")
        else:
            await inter.response.send_message(f"Deleted event `{event_name}`")


def setup(bot: commands.Bot):
    bot.add_cog(EventsCommand(bot))
