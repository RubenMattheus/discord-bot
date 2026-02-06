import sys
sys.path.append('../')
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

from src.commands.commands import Commands
from src.commands.admin_commands import AdminCommands
from src.commands.joke_commands import JokeCommands
from events import Events
from music import Music

load_dotenv()
token = os.getenv('TOKEN')

Bot = commands.Bot(command_prefix="b!", intents=discord.Intents.all())
Bot.remove_command('help')

async def startup():
    await Bot.add_cog(Commands(Bot))
    await Bot.add_cog(AdminCommands(Bot))
    await Bot.add_cog(JokeCommands(Bot))
    await Bot.add_cog(Events(Bot))
    await Bot.add_cog(Music(Bot))

asyncio.run(startup())
Bot.run(token)
