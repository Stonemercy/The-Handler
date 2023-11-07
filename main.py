from logging import getLogger, DEBUG, FileHandler, Formatter
from disnake.ext import commands
from dotenv import load_dotenv
from os import getenv
from sqlite3 import connect

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

# sets up the bot, sets me as owner, and sends the commands out to the my guild
bot = commands.InteractionBot(owner_id=OWNER, test_guilds=[MY_GUILD], reload=True)


# check for table and create table if it doesn't exist
con = connect("database.db")
cur = con.cursor()
cur.execute(
    "CREATE TABLE IF NOT EXISTS events(date_and_time timestamp, name text unique, description text, submitter)"
)
cur.execute("CREATE TABLE IF NOT EXISTS youtube(video_id)")
con.commit()

# load cogs
bot.load_extensions("cogs")


# when bot is ready...
@bot.event
async def on_ready():
    print("===============================")
    print(f"{bot.user.name} is awake and ready for action!")
    print("===============================")


# runs the bot with token
bot.run(getenv("TOKEN"))
