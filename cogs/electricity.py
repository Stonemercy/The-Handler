from disnake import AppCmdInter, ModalInteraction
from disnake.ext import commands
from helpers.classes import Modals
from helpers.db import Electricity
from helpers.functions import get_datetime
from datetime import datetime


class ElectricityCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("Electricity cog has finished loading")

    @commands.slash_command()
    async def electricity(self, inter: AppCmdInter):
        pass

    async def year_autocomp(inter: AppCmdInter, user_input: str):
        """Quick autocomplete for the electricty year command"""
        years = await Electricity.years()
        return [year for year in years if user_input in year]

    @electricity.sub_command(description="Check how much we've spent this year")
    async def year(
        self,
        inter: AppCmdInter,
        year: int = commands.Param(
            description="The year you want to check",
            default=datetime.now().year,
            autocomp=year_autocomp,
        ),
    ):
        total_spent = await Electricity.yearly_spend(year)
        if not total_spent:
            await inter.send(f"No payments have been reported for {year}")
        else:
            await inter.response.send_message(
                (
                    f"We have spent £{total_spent} on electricity in {year}\n"
                    "||This total doesnt include payments that havent been reported||"
                )
            )

    @electricity.sub_command(description="Report a payment made for electricity")
    async def report(self, inter: AppCmdInter):
        modal = Modals.ElectricityModal()
        await inter.response.send_modal(modal)

    @commands.Cog.listener("on_modal_submit")
    async def electricity_listener(self, inter: ModalInteraction):
        if inter.custom_id != "electricity_modal":
            return
        date = get_datetime(inter.text_values["electricity_date"])
        if not date:
            return await inter.send(
                (
                    "Looks like your date wasn't formatted correctly\n"
                    "Please try again"
                ),
                ephemeral=True,
            )
        elif date > datetime.now():
            return await inter.send(
                "Your date can't be in the future",
                ephemeral=True,
            )
        try:
            amount = int(inter.text_values["electricity_amount"])
        except ValueError:
            return await inter.send(
                (
                    "Looks like the amount you spent wasnt numerical.\n"
                    "Please try again."
                ),
                ephemeral=True,
            )
        report = await Electricity.report(amount, date)
        if report:
            return await inter.send(
                f"Cool, you bought £{amount} worth of electricity on {date.strftime('%d/%m/%y')}",
            )
        else:
            return await inter.send("Something went wrong :(", ephemeral=True)

    async def delete_autocomp(inter: AppCmdInter, user_input: str):
        all_records = await Electricity.all()
        dates = []
        for i in all_records:
            date = get_datetime(i[0]).strftime("%d/%m/%y")
            if date not in dates:
                dates.append(date)
                continue
            else:
                continue
        return [date for date in dates if user_input in date]

    @electricity.sub_command(description="Delete an electricity submission")
    async def delete(
        inter: AppCmdInter,
        date: str = commands.Param(
            description="The date to purge of reports", autocomp=delete_autocomp
        ),
    ):
        date_dt = get_datetime(date)
        if not date_dt:
            return await inter.send(
                "Your supplied date wasnt formatted correctly", ephemeral=True
            )
        else:
            deleted = await Electricity.delete(date_dt)
        if not deleted:
            await inter.send("The date you supplied isn't in the logs", ephemeral=True)
        else:
            await inter.send(f"Deleted event `{date}`")


def setup(bot: commands.Bot):
    bot.add_cog(ElectricityCommand(bot))
