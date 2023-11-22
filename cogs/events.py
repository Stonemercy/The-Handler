from disnake import AppCmdInter, ModalInteraction
from disnake.ext import commands, tasks
from helpers.generators import Embeds, Modals
from datetime import datetime
from os import getenv
from helpers.db import Events


# the entire cog for the invasions command
class EventsCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.event_check.start()

    def cog_load(self):
        print("Events cog has finished loading")

    def cog_unload(self):
        self.event_check.stop()

    @tasks.loop(minutes=1)
    async def event_check(self):
        now = datetime.now()
        if now.minute != 0 or now.hour not in [9, 12, 17, 21]:
            return
        channel = self.bot.get_channel(int(getenv("CHANNEL")))
        embeds = await Events.warnings(channel)
        if not embeds:
            pass
        else:
            await channel.send(content="Upcoming events:", embeds=embeds)
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
                time = datetime.fromisoformat(event[0])
                if time < datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0
                ):
                    continue
                submitter = await inter.guild.fetch_member(event[3])
                embed.add_field(
                    f"{time.strftime('%d/%m/%y')}",
                    f"**__{event[1]}__**\n{event[2]}\nSubmitted by {submitter.mention}\n\u200b",
                    inline=False,
                )

            await inter.response.send_message(embed=embed)

    # event report subcommand
    @events.sub_command(description="Report an event")
    async def report(inter: AppCmdInter):
        """Submit an event"""
        modal = Modals.event()
        await inter.response.send_modal(modal)

    # listener for event modal
    @commands.Cog.listener("on_modal_submit")
    async def event_listener(self, inter: ModalInteraction):
        if inter.custom_id != "event_modal":
            return
        else:
            embed = Embeds.event_create()
            event_name, event_desc, event_date = inter.text_values.values()
            if event_desc == "":
                event_desc = "No description"
            event_date = datetime.strptime(event_date, "%d/%m/%y")
            event_check = await Events.specific(event_date=event_date)
            if event_check is not None:
                return await inter.send(
                    "An event has already been reported for that day, pard\nCheck the list!",
                    ephemeral=True,
                    delete_after=15.0,
                )

            await Events.submit(
                event_date,
                event_name,
                inter.author.id,
                event_desc,
            )
            event = await Events.specific(event_date=event_date)
            embed.add_field(
                "Event date:",
                datetime.fromisoformat(event[0]).strftime("%d/%m/%y"),
                inline=False,
            ).add_field("Event name:", event[1], inline=False).add_field(
                "Event description:", event[2], inline=False
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
