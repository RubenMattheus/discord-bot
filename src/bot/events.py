import discord
from discord.ext import commands
from discord.ext.commands import Bot
from src.db import Repository

class Events(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.repo = Repository()

    """
    Sets the bot activity and starts the countdown function
    """
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.playing, name=self.bot.theme.get("status", self.bot.config.get("themes")["default"]["status"])))

    """
    Make bot leave vc when last person in said vc leaves
    """
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        for vc in self.bot.voice_clients:
            if vc.channel:
                non_bots = [m for m in vc.channel.members if not m.bot]
                if not non_bots:
                    await vc.disconnect()

def setup(bot):
    bot.add_cog(Events(bot))
