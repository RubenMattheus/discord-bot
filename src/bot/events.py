import discord
from discord import Message, RawReactionActionEvent
from discord.ext import commands
from discord.ext.commands import Bot
from src.data.repository import Repository

class Events(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.repo = Repository()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.playing, name='g!help'))

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if isinstance(message.channel, discord.DMChannel):
            return

        if message.author == self.bot.user:
            return
        
        server_id = message.guild.id
        if message.channel.id == self.repo.get_musicchannel(server_id):
            await self.process_music(message)

    async def process_music(self, message):
        music = self.bot.get_cog('Music')
        server_id = message.guild.id
        await music.process_message(message, server_id)
        return

def setup(bot):
    bot.add_cog(Events(bot))
