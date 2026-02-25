# discord.py
import discord
from discord.ext import commands
# config
import os
from dotenv import load_dotenv
import yaml
# default
from src.cmds import Commands, Admin
from .events import Events
# modules
from src.cmds.modules import Casino, Countdown, Music, Todo

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
    def __init__(self, theme, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theme = theme
        self.config = config

    """
    Add cogs to Bot
    """
    async def setup_hook(self):
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
Bot = MyBot(
    theme=theme,
    config=config,
    command_prefix=theme.get("prefix", config.get("themes")["default"]["prefix"]),
    intents=discord.Intents.all()
)
Bot.remove_command('help')

# Run bot
Bot.run(token)
