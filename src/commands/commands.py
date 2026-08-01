import os
import random
import asyncio
import logging
import discord
from discord.ext import commands
from discord.ext.commands import Context, Bot
from src.constants import EMBED_COLOR

logger = logging.getLogger(__name__)

class Commands(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error):
        logger.error(
            "user: %s; command: %s; error: %s", ctx.message.author, ctx.message.content, error
        )


    @commands.command()
    async def help(self, ctx: Context):
        cogs = self.bot.cogs
        text = "\t"

        for c in cogs:
            cog = self.bot.get_cog(c)
            cog_commands = cog.get_commands()
            if len(cog_commands) == 0:
                continue
            text += f"\n**{c}**"
            for command in cog_commands:
                if "help" in command.name:
                    continue
                text += f"\n- {command}"

        embed = discord.Embed(
            title='',
            description=f'{text}',
            color=EMBED_COLOR
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def audio(self, ctx):
        """ Play a random .mp3 file from ./audio_files """
        try:
            voice_channel = ctx.author.voice.channel
        except AttributeError:
            await ctx.send("Please join a vc before using audio")
            return

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

        while vc.is_playing() or vc.is_paused():
            await asyncio.sleep(10)

        await vc.disconnect()
