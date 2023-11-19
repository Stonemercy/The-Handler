from disnake import AppCmdInter, ModalInteraction
from disnake.ext import commands
from helpers.generators import Modals
from helpers.db import Gas
from datetime import datetime


# the entire cog for the energy command
class GasCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_load(self):
        print("Gas cog has finished loading")

    @commands.slash_command()
    async def gas(self, inter: AppCmdInter):
        pass

    @gas.sub_command(description="Get average gas payments over the last 12 months")
    async def year(self, inter: AppCmdInter):
        total_spent = await Gas.yearly_average()
        if not total_spent:
            await inter.response.send_message("You havent reported any payments")
        else:
            await inter.response.send_message(
                f"You have spent £{total_spent} on gas in the last 12 months"
            )

    # gas subcommand
    @gas.sub_command(description="Report a payment made for gas")
    async def report(self, inter: AppCmdInter):
        modal = Modals.gas()
        await inter.response.send_modal(modal)

    # listener for gas modal
    @commands.Cog.listener("on_modal_submit")
    async def gas_listener(self, inter: ModalInteraction):
        if inter.custom_id != "gas_modal":
            return
        else:
            amount = list(inter.text_values.values())[0]
            report = await Gas.report(amount)
            if report:
                await inter.send(f"Cool, you bought £{amount} worth of gas")

    # delete command
    @gas.sub_command(description="Delete a gas submission")
    async def delete(
        inter: AppCmdInter, date: str = datetime.now().strftime("%d/%m/%y")
    ):
        """Delete an event"""
        deleted = await Gas.delete(date)
        if not deleted:
            await inter.response.send_message("Something went wrong")
        else:
            await inter.response.send_message(f"Deleted event `{date}`")


def setup(bot: commands.Bot):
    bot.add_cog(GasCommand(bot))
