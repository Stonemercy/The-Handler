from disnake import AppCmdInter, ModalInteraction
from disnake.ext import commands
from helpers.generators import electricity_report_modal
from data.db import Electricity
from datetime import datetime


# the entire cog for the electricity command
class ElectricityCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_load(self):
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

    # electricity subcommand
    @electricity.sub_command(description="Report a payment made for electricity")
    async def report(self, inter: AppCmdInter):
        modal = electricity_report_modal()
        await inter.response.send_modal(modal)

    # listener for electricity modal
    @commands.Cog.listener("on_modal_submit")
    async def electricity_listener(self, inter: ModalInteraction):
        if inter.custom_id != "electricity_modal":
            return
        else:
            amount = list(inter.text_values.values())[0]
            report = await Electricity.report(amount)
            if report:
                await inter.send(f"Cool, you bought £{amount} worth of electricity")

    # delete command
    @electricity.sub_command(description="Delete an electricity submission")
    async def delete(
        inter: AppCmdInter, date: str = datetime.now().strftime("%d/%m/%y")
    ):
        # """Delete an electricity submission"""
        deleted = await Electricity.delete(date)
        if not deleted:
            await inter.response.send_message("Something went wrong")
        else:
            await inter.response.send_message(f"Deleted event `{date}`")


def setup(bot: commands.Bot):
    bot.add_cog(ElectricityCommand(bot))
