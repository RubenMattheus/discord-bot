import asyncio
import logging
from dataclasses import dataclass, field
from typing import Optional
import discord
from discord import Message, RawReactionActionEvent, VoiceClient
from discord.ext import commands
from discord.ext.commands import Bot, Context
from yt_dlp import YoutubeDL
from src.db import Repository
from src.commands import check_for_admin

logger = logging.getLogger(__name__)

@dataclass
class ServerMusicState:
    voice_channel: Optional[VoiceClient] = None
    music_queue: list = field(default_factory=list)
    is_playing: bool = False

class Music(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.repo = Repository()

        self.commands = {
            "⏹️": self.stop_command,
            "⏸️": self.pause_command,
            "▶️": self.resume_command,
            "⏩": self.skip_command
        }
        self.state = {}
        self.fill_state()

        self.YDL_OPTIONS = {
            'format': 'bestaudio',
            'noplaylist': True,
            'extractaudio': True,
            'audioquality': 1,
            'outtmpl': 'song.mp3',
            'quiet': True,
            'default_search': 'ytsearch',
            'extractor_args': {
                'soundcloud': ['--no-warnings'],
            },
        }
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn', 'executable': 'ffmpeg'}

    @commands.command()
    async def musicsetup(self, ctx: Context):
        if not await check_for_admin(ctx):
            return

        await asyncio.sleep(1)
        await ctx.message.delete()

        embed = discord.Embed(
            title="**QUEUE**",
            description="*enter song title to start playing music*"
        )
        queue_message = await ctx.message.channel.send(embed=embed)

        emoji = ['⏹️', '⏸️', '▶️', '⏩']
        for e in emoji:
            await queue_message.add_reaction(e)

        server_id, channel_id = ctx.guild.id, ctx.message.channel.id
        self.repo.add_musicqueue(server_id, channel_id, queue_message.id)

        self.state[server_id] = ServerMusicState()

    @commands.command()
    async def music(self, ctx: Context):
        """ Get the textchannel where the music queuemessage is located """
        server_id = ctx.message.guild.id
        music_channel = self.repo.get_musicchannel(server_id)
        music_channel = await ctx.message.guild.fetch_channel(music_channel)
        await ctx.send(music_channel.mention)

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        """ Process messages sent in the music channel """
        if isinstance(message.channel, discord.DMChannel):
            return

        if message.author == self.bot.user:
            return

        server_id = message.guild.id
        if message.channel.id == self.repo.get_musicchannel(server_id):
            await self.process_message(message, server_id)
            return

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        """ Process reactions being added to the queue message """
        server_id, message_id, user = payload.guild_id, payload.message_id, payload.user_id

        if user == self.bot.user.id:
            return

        if message_id == self.repo.get_queuemessage(server_id):
            await self.handle_emoji(payload)
            return

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        """ Process reactions being removed from the queue message """
        server_id, message_id, user = payload.guild_id, payload.message_id, payload.user_id

        if user == self.bot.user.id:
            return

        if message_id == self.repo.get_queuemessage(server_id):
            await self.handle_emoji(payload)
            return


    def fill_state(self):
        """ Create a state entry for every server that has music set up """
        servers = self.repo.get_server_ids_music()
        if not servers:
            return
        for server_id in servers:
            server_id = server_id[0]
            self.state[server_id] = ServerMusicState()

    # Manage vc, queue and playing state when adding/removing emoji on the queue message

    def stop_command(self, server_id):
        state = self.state[server_id]
        state.voice_channel.stop()
        state.music_queue.clear()
        state.is_playing = False

    def pause_command(self, server_id):
        self.state[server_id].voice_channel.pause()

    def resume_command(self, server_id):
        self.state[server_id].voice_channel.resume()

    def skip_command(self, server_id):
        self.state[server_id].voice_channel.stop()

    async def update_queue(self, server_id):
        """ Update the content of the queue message to reflect the current queue """
        state = self.state[server_id]
        server = self.bot.get_guild(server_id)
        music_channel = await server.fetch_channel(self.repo.get_musicchannel(server_id))
        queue_message = await music_channel.fetch_message(self.repo.get_queuemessage(server_id))

        if len(state.music_queue) == 0:
            song_lijst = "*enter song title to start playing music*"
        else:
            song_lijst = f"*currently playing:*\n**{state.music_queue[0]['title']}**\n"

        if len(state.music_queue) > 1:
            song_lijst += "\t\n*queue:*"

        if len(state.music_queue) <= 11:
            for i in range(1, len(state.music_queue)):
                song_lijst += f"\n{i}. **{state.music_queue[i]['title']}**"
        elif len(state.music_queue) > 11:
            for i in range(1, 11):
                song_lijst += f"\n{i}. {state.music_queue[i]}"

            song_lijst += f"\n*and **{len(state.music_queue) - 11}** more*"

        queue_embed = discord.Embed(title="**QUEUE**", description=song_lijst)
        await queue_message.edit(embed=queue_embed)

    async def process_message(self, message: Message, server_id):
        content = message.content
        author = message.author

        if author == self.bot.user:
            return

        await asyncio.sleep(1)
        await message.delete()

        if self.bot.get_theme_value("prefix") in content:
            return

        try:
            author_vc = message.author.voice.channel
        except AttributeError:
            # DMed instead of posted here: this channel auto-deletes every message,
            # so an in-channel error would just vanish too.
            await author.send("Please join a vc before queueing songs")
            return

        song = self.search_song(content)
        if not song:
            await author.send("Error with song: invalid url")
            return
        elif song['duration'] > 600:
            await author.send("Error with song: duration over 10 minutes")
            return

        state = self.state[server_id]
        state.music_queue.append(song)

        if not state.is_playing:
            state.voice_channel = await author_vc.connect()
            await self.play_music(message)

        await self.update_queue(server_id)

    async def handle_emoji(self, payload: RawReactionActionEvent):
        """ Process the payload of an added or removed reaction  """
        server_id = payload.guild_id
        emoji = payload.emoji.name

        if emoji in self.commands:
            self.commands[emoji](server_id)
        elif payload.event_type == "REACTION_ADD":
            server = self.bot.get_guild(server_id)
            channel = await server.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            user = await server.fetch_member(payload.user_id)

            await message.remove_reaction(payload.emoji, user)
            await user.send("Please don't add reactions to the queue message")
            return

        if emoji == '⏹️':
            await self.state[server_id].voice_channel.disconnect()
            await self.update_queue(server_id)

    def search_song(self, message):
        """ Extract the info of the top result of a youtube or soundcloud search """
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            platforms = ['youtube.com', 'youtu.be', 'soundcloud.com']
            if any(platform in message for platform in platforms):
                try:
                    info = ydl.extract_info(message, download=False)
                except Exception as e:
                    logger.error("Error extracting song info for %s: %s", message, e)
                    return False
            else:
                try:
                    info = ydl.extract_info(f"ytsearch:{message}", download=False)['entries'][0]
                except Exception as e:
                    logger.error("Error searching for song %s: %s", message, e)
                    return False
            return {'source': info['url'], 'title': info['title'], 'duration': info['duration']}

    async def play_music(self, ctx: Context):
        server_id = ctx.guild.id
        state = self.state[server_id]
        state.is_playing = True

        while len(state.music_queue) > 0:
            await self.update_queue(server_id)
            url = state.music_queue[0]['source']
            audio_source = discord.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS)
            state.voice_channel.play(discord.PCMVolumeTransformer(audio_source, volume=0.05))

            while state.voice_channel.is_playing() or state.voice_channel.is_paused():
                await asyncio.sleep(1)

            if state.is_playing:
                state.music_queue.pop(0)

        await state.voice_channel.disconnect()
        state.is_playing = False
