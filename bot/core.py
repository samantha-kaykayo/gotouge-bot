from pymongo import MongoClient
import os
from dotenv import load_dotenv
import discord
from discord.ext.commands import Bot

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")  # correct
MONGO_URI = os.getenv("MONGO_URI")  # correct

client = MongoClient(MONGO_URI)
db = client['gotouge_bot']
quotes_col = db['quotes']
channels_col = db['channels']

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = Bot(command_prefix="!", intents=intents)