from disnake import AppCmdInter, ModalInteraction
from disnake.ext import commands
from helpers.functions import get_datetime
from helpers.generators import Modals
from helpers.db import Gas
from datetime import datetime


class GasCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
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
                f"You have spent £{total_spent:.2f} on gas in the last 12 months"
            )

    @gas.sub_command(description="Report a payment made for gas")
    async def report(self, inter: AppCmdInter):
        modal = Modals.GasModal()
        await inter.response.send_modal(modal)

    @commands.Cog.listener("on_modal_submit")
    async def gas_listener(self, inter: ModalInteraction):
        if inter.custom_id != "gas_modal":
            return
        if inter.text_values["gas_date"] == "":
            date = datetime.now()
        else:
            try:
                date = datetime.strptime(inter.text_values["gas_date"], "%d/%m/%y")
            except ValueError:
                return await inter.send(
                    "Looks your date wasnt formatted correctly.\nPlease try again."
                )
        amount = inter.text_values["gas_amount"]
        report = await Gas.report(amount, date)
        if report:
            await inter.send(
                f"Cool, you bought £{amount} worth of gas on {date.strftime('%d/%m/%y')}"
            )

    @gas.sub_command(description="Delete a gas submission")
    async def delete(
        inter: AppCmdInter,
        date: str = commands.Param(description="The date to purge of reports"),
    ):
        """Delete an event"""
        date = get_datetime(date)
        if not date:
            return await inter.send("That wasn't a valid date", ephemeral=True)
        deleted = await Gas.delete(date)
        if not deleted:
            await inter.send("Something went wrong", ephemeral=True)
        else:
            await inter.send(f"Deleted gas payment on `{date}`")


def setup(bot: commands.Bot):
    bot.add_cog(GasCommand(bot))
