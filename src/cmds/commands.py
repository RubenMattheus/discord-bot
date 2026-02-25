import discord
from discord.ext import commands
from discord.ext.commands import Context, Bot
import os
import random
import asyncio
from datetime import datetime
from src.db import Repository

class Commands(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.repo = Repository()
    
    """
    Print errors to console
    """
    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error):
        print(f"<{datetime.now()}> user: {ctx.message.author}; command: {ctx.message.content}; error: {error}")

    """
    List commands
    """
    @commands.command()
    async def help(self, ctx: Context):
        cogs = self.bot.cogs
        text = "\t"
        
        for c in cogs:
            cog = self.bot.get_cog(c)
            commands = cog.get_commands()
            if len(commands) == 0:
                continue
            text += f"\n**{c}**"
            for command in commands:
                if "help" in command.name:
                    continue
                text += f"\n- {command}"

        embed = discord.Embed(title='', description=f'{text}', color=discord.Color.from_rgb(40, 11, 15))
        await ctx.send(embed=embed)

    """
    Play a random .mp3 file from ./audio_files
    """
    @commands.command()
    async def audio(self, ctx):
        voice_channel = ctx.author.voice.channel
        vc = await voice_channel.connect()

        folder = os.path.abspath("audio_files")
        files = [f for f in os.listdir(folder) if f.endswith('.mp3')]
        if not files:
            await ctx.send("No audio files found.")
            return

        track = random.choice(files)
        track_path = os.path.join(folder, track)

        # FFMPEG command to play with fade-in/out, max 4 hours
        # 10s fade-in, 10s fade-out starting at 4h - 10s (14390s)
        ffmpeg_options = {
            'before_options': '-nostdin',
            'options': (
                "-vn "
                "-af 'afade=t=in:ss=0:d=10,afade=t=out:st=14390:d=10' "
                "-t 14400"
            )
        }

        ffmpeg_source = discord.FFmpegPCMAudio(track_path, **ffmpeg_options)
        source = discord.PCMVolumeTransformer(ffmpeg_source, volume=0.25)  # volume: 0.0–1.0

        vc.play(source)

        while True:
            await asyncio.sleep(10)

def setup(bot):
    bot.add_cog(Commands(bot))
