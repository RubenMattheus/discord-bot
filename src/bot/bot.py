# config
import os
from dotenv import load_dotenv
import yaml
# discord.py
import discord
from discord.ext import commands
# default
from src.commands import Commands, Admin
from src.bot.events import Events
# modules
from src.modules import Casino, Countdown, Music, Todo

# Load config
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Load .env
load_dotenv()
token = os.getenv('TOKEN')

# Load theme
selected_theme = config["theme"]["active"]
theme = config["themes"][selected_theme]

class MyBot(commands.Bot):
    """ class module for the Discord bot, sets the specified modules """
    def __init__(self, theme, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theme = theme
        self.config = config

    async def setup_hook(self):
        # Add cogs to Bot
        await self.add_cog(Commands(self))
        await self.add_cog(Admin(self))
        await self.add_cog(Events(self))

        modules = self.config["modules"]
        if modules["casino"]:
            await self.add_cog(Casino(self))
        if modules["countdown"]:
            await self.add_cog(Countdown(self))
        if modules["music"]:
            await self.add_cog(Music(self))
        if modules["todo"]:
            await self.add_cog(Todo(self))

# Create Bot instance
BOT = MyBot(
    theme=theme,
    config=config,
    command_prefix=theme.get("prefix", config.get("themes")["default"]["prefix"]),
    intents=discord.Intents.all()
)
BOT.remove_command('help')

# Run bot
BOT.run(token)
