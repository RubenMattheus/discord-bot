import logging
import os
from dotenv import load_dotenv
import yaml
import discord
from discord.ext import commands
from src.commands import Commands, Admin
from src.bot.events import Events
from src.modules import Casino, Countdown, Music, Todo
from src.db.sqlite_setup import create_tables

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# Load config
with open("config/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# Load .env
load_dotenv()
token = os.getenv("TOKEN")

# Load theme
selected_theme = config["theme"]["active"]
theme = config["themes"][selected_theme]


def get_theme_value(theme_dict, config_dict, key):
    return theme_dict.get(key, config_dict.get("themes")["default"][key])


class MyBot(commands.Bot):
    def __init__(self, theme, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theme = theme
        self.config = config

    def get_theme_value(self, key):
        return get_theme_value(self.theme, self.config, key)

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
    command_prefix=get_theme_value(theme, config, "prefix"),
    intents=discord.Intents.all(),
)
BOT.remove_command("help")

# Ensure database tables exist, then run bot
create_tables()
BOT.run(token)
