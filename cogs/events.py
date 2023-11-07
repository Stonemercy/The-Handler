import disnake
from disnake.ext import commands, tasks
from helpers.generators import modal_gen, Embeds
from main import con, cur
from datetime import datetime, timedelta
import os


# the entire cog for the invasions command
class EventsCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.event_check.start()

    def cog_load(self):
        print("Events cog has finished loading")

    def cog_unload(self):
        self.event_check.stop()

    async def warning(
        self,
        now: datetime,
        events: list,
        hour: bool = True,
        day: bool = False,
        month: bool = False,
    ):
        unit, hour, day, month = "hour", 1, 0, 0
        if day:
            unit, hour, day = "day", 0, 1
        elif month:
            unit, hour, month = "month", 0, 4

        for event in events:
            if (
                now
                < datetime.fromisoformat(event[0])
                <= now + timedelta(hours=hour, days=day, weeks=month * 4)
            ):
                embed = Embeds.EventWarning.hour()
                embed.add_field(
                    f"This event is happening within 1 {unit}:",
                    f"{event[1]}\n{event[2]}",
                ).add_field("Submitted by:", await self.bot.fetch_user(event[3]))
                print(f'Warned for event "{event[1]}"')
                await self.channel.send(embed=embed)

    def monthly_purge(
        self, con, cur, now: datetime = datetime.now(), events: list() = []
    ):
        for event in events:
            if datetime.fromisoformat(event[0]) < now - timedelta(weeks=4):
                cur.execute(
                    "Delete from events where date_and_time = ? and name = ?",
                    (event[0], event[1]),
                )
                con.commit()
                print(f'Deleted event "{event[1]}" from the db')

    @tasks.loop(minutes=1)
    async def event_check(self):
        self.channel = self.bot.get_guild(int(os.getenv("GUILD"))).get_channel(
            int(os.getenv("CHANNEL"))
        )
        now = datetime.now()
        all_events = cur.execute("select * from events").fetchall()
        if all_events != []:
            await self.warning(now, all_events, hour=True)
            await self.warning(now, all_events, day=True)
            await self.warning(now, all_events, month=True)
            self.monthly_purge(con, cur, now, all_events)

    @event_check.before_loop
    async def before_invasions_ping(self):
        await self.bot.wait_until_ready()

    # events parent command (does nothing)
    @commands.slash_command()
    async def events(self, inter: disnake.ApplicationCommandInteraction):
        pass

    # events list subcommand
    @events.sub_command(description="List events")
    async def list(self, inter: disnake.ApplicationCommandInteraction):
        embed = Embeds.list()
        events_in_db = cur.execute(
            "select * from events order by date_and_time asc"
        ).fetchall()

        if events_in_db == []:
            embed.add_field("Looks like there are no upcoming events, pard.", "")
            await inter.response.send_message(embed=embed)
        else:
            for i in events_in_db:
                if datetime.fromisoformat(i[0]) < datetime.now():
                    continue
                time = datetime.fromisoformat(i[0]).strftime("%d/%m/%Y - %H:%M")
                embed.add_field(f"{time} - {i[1]}", f"{i[2]}", inline=False)

            await inter.response.send_message(embed=embed)

    # event report subcommand
    @events.sub_command(description="Report an event")
    async def report(inter: disnake.AppCmdInter):
        """Submit an event"""

        modal = modal_gen("event")

        await inter.response.send_modal(modal=modal)

    # listener for event modal
    @commands.Cog.listener("on_modal_submit")
    async def event_listener(self, inter: disnake.ModalInteraction):
        if inter.custom_id != "event_modal":
            return
        else:
            embed = Embeds.event_create()
            event_name, event_desc, event_date, event_time = inter.text_values.values()
            event_check = cur.execute(
                "Select * from events where name is ?", (event_name,)
            ).fetchone()
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
            )
            cur.execute(
                "Insert or ignore into events values (?, ?, ?, ?)",
                (event_date_and_time, event_name, event_desc, inter.author.id),
            )
            con.commit()
            event_confirm = cur.execute(
                "Select * from events where name is ?", (event_name,)
            ).fetchone()

            embed.add_field(
                "Event date and time:",
                f"{datetime.fromisoformat(event_confirm[0]).strftime('%d/%m/%y - %H:%M')}",
                inline=False,
            ).add_field("Event name:", event_confirm[1], inline=False).add_field(
                "Event description:", event_confirm[2], inline=False
            )
            await inter.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(EventsCommand(bot))
