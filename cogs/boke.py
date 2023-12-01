from disnake import AppCmdInter
from disnake.ext import commands
from helpers.db import Pearl
from datetime import datetime


class BokeCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("Boke cog has finished loading")

    @commands.slash_command(description="Report that pearl has boked")
    async def boke(self, inter: AppCmdInter):
        await Pearl.boked()
        history = await Pearl.all()
        await inter.send("Boke history:")
        if history == []:
            return await inter.send("No bokes were recorded... until now")
        content = ""
        last = None
        for i in history:
            date = datetime.fromisoformat(i[0])
            if last is None:
                content = f"Record began: {date.strftime('%d/%m/%y')}"
                last = date
                return await inter.send(content=content)
            else:
                difference = date - last
                content += f"\n⬇️\n{difference.days} day(s) of no bokes\n⬇️\nBoked on {date.strftime('%d/%m/%y')}"
                last = date
        await inter.send(content=content)


def setup(bot: commands.Bot):
    bot.add_cog(BokeCommand(bot))
