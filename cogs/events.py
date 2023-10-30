import disnake
from disnake.ext import commands, tasks
from helpers.generators import modal_gen, embed_gen
from main import con, cur
from datetime import datetime, timedelta
import os

# autocomplete languages
"""async def zone_autocomplete(
    inter: disnake.ApplicationCommandInteraction, user_input: str
):
    if not str:
        return ["Type in a zone"]
    return [zones for zones in zones if user_input.title() in zones]"""


# the entire cog for the invasions command
class EventsCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.event_ping.start()

    def cog_load(self):
        print("Events cog has finished loading")

    def cog_unload(self):
        self.event_ping.stop()

    @tasks.loop(minutes=1)
    async def event_ping(self):
        owner_user = await self.bot.fetch_user(int(os.getenv("OWNER")))
        now = datetime.now()
        one_hour_warning = now + timedelta(hours=1)
        one_day_warning = now + timedelta(days=1)
        one_week_deleting = now - timedelta(weeks=1)
        # print(f"\n########## {now.strftime('%H:%M')} ##########") # use for printing every minute to termintal
        all_events = cur.execute("select * from events").fetchall()
        if now.minute == 30:
            print(f"{len(all_events)} events found")
        if all_events != []:
            channel = self.bot.get_guild(int(os.getenv("GUILD"))).get_channel(
                int(os.getenv("CHANNEL"))
            )
            for dead in all_events:
                if datetime.fromisoformat(dead[0]) < one_week_deleting:
                    cur.execute(
                        "Delete from events where date_and_time = ? and name = ?",
                        (dead[0], dead[1]),
                    )
                    con.commit()
                    await channel.send(f'Event "{dead[1]}" has left the locale')
                    print(f'Deleted event "{dead[1]}" from the db')
            all_events = cur.execute("select * from events").fetchall()
            time_now = now.time().replace(second=0, microsecond=0)
            for i in all_events:
                event_time = datetime.fromisoformat(i[0]).time()
                print(f"Event:   {i[1]}\nEvent_time:   {event_time}")
                if time_now > event_time:
                    print(f"  - Event {all_events.index(i)+1} has already happened")
                    pass
                elif now.time() < event_time < one_hour_warning.time():
                    embed = embed_gen("event_hour")
                    embed.add_field(f"This event is within an hour:", i[1])
                    await channel.send(f"{owner_user.mention}", embed=embed)
                    print(f"Event {i[1]} is happening soon!")
        if con.total_changes > 0:
            con.commit()

    @event_ping.before_loop
    async def before_invasions_ping(self):
        await self.bot.wait_until_ready()

    # events parent command (does nothing)
    @commands.slash_command()
    async def events(self, inter: disnake.ApplicationCommandInteraction):
        pass

    # events list subcommand
    @events.sub_command(description="List events")
    async def list(self, inter: disnake.ApplicationCommandInteraction):
        embed = embed_gen("list")
        events_in_db = cur.execute(
            "select * from events order by date_and_time asc"
        ).fetchall()

        if events_in_db == []:
            embed.add_field("Looks like there are no upcoming events, pard.", "")
            await inter.response.send_message(embed=embed)
        else:
            for i, j in enumerate(events_in_db, 1):
                embed.add_field(f"{i} - {j[0]} - {j[1]}", "", inline=False).add_field(
                    f"{j[2]}", "\u200b", inline=False
                )

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
            embed = embed_gen("event_creation")
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
                "Insert or ignore into events values (?, ?, ?)",
                (event_date_and_time, event_name, event_desc),
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

    """# listener for leaderboard vote buttons
    @commands.Cog.listener("on_button_click")
    async def leaderboard_vote_listener(self, inter:disnake.MessageInteraction):
        if inter.component.custom_id not in ["upvote", "downvote"]:
            return
        report_author = re.findall('\d{16,19}', inter.message.embeds[0].fields[2].value)[0]
        user_in_leaderboard = cur.execute("Select * from users where user_id = ?", (report_author,)).fetchone()
        if user_in_leaderboard == None:
            cur.execute(f"Insert or ignore into users values (?, ?)", (report_author, 0))
            con.commit()
        elif inter.component.custom_id == "upvote":
            cur.execute("Update users set votes = ? where user_id = ?", (user_in_leaderboard[1] + 1, report_author))
            con.commit()
        else:
            cur.execute("Update users set votes = ? where user_id = ?", (user_in_leaderboard[1] - 1, report_author))
            con.commit()"""

    """# invasions delete subcommand
    @invasions.sub_command(description="Delete an invasion")
    async def delete(self, inter: disnake.ApplicationCommandInteraction, number: int):
        global user_inputs
        user_inputs = [number - 1]
        actives = cur.execute("SELECT * FROM invasions ORDER BY time ASC")
        activeInvasions = actives.fetchall()
        embed = embed_generator("delete")

        if activeInvasions == []:
            embed.add_field(
                name="**No invasions have been reported for today**", value=""
            )
            await inter.response.send_message(embed=embed)
        else:
            user_choice = activeInvasions[user_inputs[0]]
            embed.add_field(
                name=f"{user_choice[0]} - {user_choice[1]}",
                value=f"Important: {user_choice[2]}",
                inline=True,
            )
            embed.add_field(
                name="===============================================",
                value="",
                inline=False,
            )
            await inter.response.send_message(
                embed=embed,
                components=[
                    disnake.ui.Button(
                        label="Yes",
                        style=disnake.ButtonStyle.success,
                        custom_id="delete_yes",
                    ),
                    disnake.ui.Button(
                        label="No",
                        style=disnake.ButtonStyle.danger,
                        custom_id="delete_no",
                    ),
                ],
            )

    # listener for delete confirmation buttons
    @commands.Cog.listener("on_button_click")
    async def delete_listener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id not in ["delete_yes", "delete_no"]:
            return
        actives = cur.execute("SELECT * FROM invasions ORDER BY time ASC")
        activeInvasions = actives.fetchall()
        target = activeInvasions[user_inputs[0]]
        embed = embed_generator("delete")

        if inter.component.custom_id == "delete_yes":
            embed.add_field(
                name=f"{int(user_inputs[0])+1} - {target[0]} , {target[1]}",
                value=f"Important: {target[2]}",
            )
            cur.execute(
                f"Delete from invasions where zone='{target[0]}' and time='{target[1]}'"
            )
            con.commit()
            print(
                f"User {inter.author.display_name} deleted {target[0]} at {target[1]}"
            )
            await inter.response.send_message(embed=embed)"""


def setup(bot: commands.Bot):
    bot.add_cog(EventsCommand(bot))
