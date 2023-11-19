from disnake import AppCmdInter
from disnake.ext import commands
from helpers.db import Pearl
from datetime import datetime


# the entire cog for the energy command
class BokeCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_load(self):
        print("Boke cog has finished loading")

    @commands.slash_command(
        description="Report that pearl has boked (submits upon pressing enter for this command)"
    )
    async def boke(self, inter: AppCmdInter):
        await Pearl.boked()
        await inter.response.send_message("Ah fuck...", delete_after=3.0)
        history = await Pearl.all()
        if history == []:
            return await inter.send("No bokes have been recorded, yay!")
        content = ""
        last = None
        for i in history:
            if last is None:
                content = (
                    f"Record began: {datetime.fromisoformat(i[0]).strftime('%d/%m/%y')}"
                )
                last = datetime.fromisoformat(i[0])
                await inter.send(content=content)
            else:
                next_date = datetime.fromisoformat(i[0])
                difference = next_date - last
                content += f"\n⬇️\n{difference.days} day(s) of no bokes\n⬇️\nBoked on {next_date.strftime('%d/%m/%y')}"
                last = next_date
        await inter.send(content=content)


def setup(bot: commands.Bot):
    bot.add_cog(BokeCommand(bot))
