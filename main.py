from logging import getLogger, DEBUG, FileHandler, Formatter
from disnake.ext import commands
from dotenv import load_dotenv
from os import getenv
from data.db import db_startup

# from migrations import migration3

# env's
load_dotenv()
OWNER = int(getenv("OWNER"))
MY_GUILD = int(getenv("GUILD"))

# logging
logger = getLogger("disnake")
logger.setLevel(DEBUG)
handler = FileHandler(filename="disnake.log", encoding="utf-8", mode="w")
handler.setFormatter(Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

# sets up the bot, sets me as owner, and sends the commands out to my guild
bot = commands.InteractionBot(owner_id=OWNER, test_guilds=[MY_GUILD], reload=True)

# load cogs
bot.load_extensions("cogs")


# when bot is ready...
@bot.event
async def on_ready():
    print("===============================")
    await db_startup()
    # await migration3.migrate()
    print(f"{bot.user.name} is awake and ready for action!")
    print("===============================")


# runs the bot with token
bot.run(getenv("TOKEN"))
