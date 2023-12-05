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
        history = await Pearl.all_bokes()
        await inter.send("### Boke history:")
        if not history:
            return await inter.channel.send("No bokes were recorded... until now")
        content = ""
        last = None
        for i in history:
            date = datetime.fromisoformat(i[0])
            if last is None:
                last = date
                await inter.channel.send(f"Record began: {date.strftime('%d/%m/%y')}")
            else:
                difference = date - last
                content += f"\n⬇️\n{difference.days} day(s) of no bokes\n⬇️\nBoked on {date.strftime('%d/%m/%y')}"
                last = date
        await inter.channel.send(content=content)

    @commands.slash_command(description="Delete a boke submission")
    async def boke_delete(
        self, inter: AppCmdInter, date: str = datetime.now().strftime("%d/%m/%y")
    ):
        deleted = await Pearl.didnt_boke(date)
        if not deleted:
            await inter.response.send_message("No reports were found for that date")
        else:
            await inter.response.send_message(f"Deleted event `{date}`")


def setup(bot: commands.Bot):
    bot.add_cog(BokeCommand(bot))
