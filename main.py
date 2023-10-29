import os
import sqlite3
import scrapetube
from datetime import datetime
from helpers.generators import embed_gen, WeatherEmojis
from disnake.ext import commands, tasks
from dotenv import load_dotenv
import logging

# env's
load_dotenv()
OWNER = int(os.getenv("OWNER"))
MY_GUILD = int(os.getenv("GUILD"))

# logging
logger = logging.getLogger("disnake")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="disnake.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

# sets up the bot, sets me as owner, and sends the commands out to the my guild
bot = commands.InteractionBot(owner_id=OWNER, test_guilds=[MY_GUILD], reload=True)


# check for table and create table if it doesn't exist
con = sqlite3.connect("database.db")
cur = con.cursor()
cur.execute(
    "CREATE TABLE IF NOT EXISTS events(date_and_time timestamp, name text unique, description text)"
)
con.commit()

# load cogs
bot.load_extensions("cogs")


# when bot is ready...
@bot.event
async def on_ready():
    print("===============================")
    print(f"{bot.user.name} is awake and ready for action!")
    print("===============================")


@tasks.loop(minutes=1)
async def youtube_scraper():
    latest_video = scrapetube.get_channel(channel_username="Toonpishcrafts")
    print(f"latest video: {latest_video}")


@youtube_scraper.before_loop
async def before_weather_info():
    await bot.wait_until_ready()


# runs the bot with token
bot.run(os.getenv("TOKEN"))
