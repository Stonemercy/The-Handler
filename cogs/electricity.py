from disnake import AppCmdInter, ModalInteraction
from disnake.ext import commands
from helpers.generators import Modals
from helpers.db import Electricity
from datetime import datetime


class ElectricityCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("Electricity cog has finished loading")

    @commands.slash_command()
    async def electricity(self, inter: AppCmdInter):
        pass

    @electricity.sub_command(
        description="Get average electricity payments over the last 12 months"
    )
    async def year(self, inter: AppCmdInter):
        total_spent = await Electricity.yearly_average()
        if not total_spent:
            await inter.response.send_message("You havent reported any payments")
        else:
            await inter.response.send_message(
                f"You have spent £{total_spent:.2f} on electricity in the last 12 months"
            )

    @electricity.sub_command(description="Report a payment made for electricity")
    async def report(self, inter: AppCmdInter):
        modal = Modals.ElectricityModal()
        await inter.response.send_modal(modal)

    @commands.Cog.listener("on_modal_submit")
    async def electricity_listener(self, inter: ModalInteraction):
        if inter.custom_id != "electricity_modal":
            return
        if inter.text_values["electricity_date"] == "":
            date = datetime.now()
        else:
            try:
                date = datetime.strptime(
                    inter.text_values["electricity_date"], "%d/%m/%y"
                )
            except ValueError:
                return await inter.send(
                    "Looks your date wasnt formatted correctly.\nPlease try again.", ephemeral=True
                )
        amount = inter.text_values["electricity_amount"]
        if amount is not int or amount is not float:
            return await inter.send(
                "Looks like the amount you spent wasnt a number.\nPlease try again.",
                ephemeral=True
            )
        report = await Electricity.report(amount, date)
        if report:
            await inter.send(
                f"Cool, you bought £{amount} worth of electricity on {date.strftime('%d/%m/%y')}",
            )

    @electricity.sub_command(description="Delete an electricity submission")
    async def delete(
        inter: AppCmdInter, date: str = datetime.now().strftime("%d/%m/%y")
    ):
        deleted = await Electricity.delete(date)
        if not deleted:
            await inter.response.send_message("Something went wrong")
        else:
            await inter.response.send_message(f"Deleted event `{date}`")


def setup(bot: commands.Bot):
    bot.add_cog(ElectricityCommand(bot))
