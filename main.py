from datetime import datetime
from logging import getLogger, DEBUG, FileHandler, Formatter
from disnake.ext import commands
from dotenv import load_dotenv
from os import getenv
from helpers.db import Dashboard, db_startup
from disnake import Intents

# intents for dashboard
intents = Intents.default()
intents.members = True

# env's
load_dotenv("data/.env")
OWNER = int(getenv("OWNER"))
MY_GUILD = int(getenv("GUILD"))

# logging
logger = getLogger("disnake")
logger.setLevel(DEBUG)
handler = FileHandler(filename="logs/disnake.log", encoding="utf-8", mode="w")
handler.setFormatter(Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

# sets up the bot, sets me as owner, and sends the commands out to my guild
bot = commands.InteractionBot(
    owner_id=OWNER, test_guilds=[MY_GUILD], reload=True, intents=intents
)

# load cogs
bot.load_extensions("cogs")


# when bot is ready...
@bot.event
async def on_ready():
    now = datetime.now().timestamp()
    print("===============================")
    await db_startup()
    await Dashboard.set_startup(now)
    print(f"{bot.user.name} is awake and ready for action!")
    print("===============================")


# runs the bot with token
bot.run(getenv("TOKEN"))
