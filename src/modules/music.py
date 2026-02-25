import discord
from discord import Message, RawReactionActionEvent
from discord.ext import commands
from discord.ext.commands import Bot, Context
from yt_dlp import YoutubeDL
import asyncio
from src.db import Repository
from src.cmds import check_for_admin

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
        self.is_playing = {}
        self.voice_channel = {}
        self.music_queue = {}
        self.fill_dictionaries()

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
        
    """
    Create a queuemessage, add the emoji, save the IDs in the db and update the dictionary
    """
    @commands.command()
    async def musicsetup(self, ctx: Context):
        if not await check_for_admin(ctx):
            return
        
        await asyncio.sleep(1)
        await ctx.message.delete()

        embed = discord.Embed(title="**QUEUE**", description="*enter song title to start playing music*")
        queue_message = await ctx.message.channel.send(embed=embed)

        emoji = ['⏹️', '⏸️', '▶️', '⏩']
        for e in emoji:
            await queue_message.add_reaction(e)

        server_id, channel_id = ctx.guild.id, ctx.message.channel.id
        self.repo.add_musicqueue(server_id, channel_id, queue_message.id)

        self.is_playing[server_id] = False
        self.voice_channel[server_id] = ""
        self.music_queue[server_id] = []
        
    """
    Get the textchannel where the music queuemessage is located
    """
    @commands.command()
    async def music(self, ctx: Context):
        server_id = ctx.message.guild.id
        music_channel = self.repo.get_musicchannel(server_id)
        music_channel = await ctx.message.guild.fetch_channel(music_channel)
        await ctx.send(music_channel.mention)
        
    """
    Process messages sent in the music channel
    """
    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if isinstance(message.channel, discord.DMChannel):
            return

        if message.author == self.bot.user:
            return
        
        server_id = message.guild.id
        if message.channel.id == self.repo.get_musicchannel(server_id):
            await self.process_message(message, server_id)
            return

    """
    Process reactions being added to the queue message
    """
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        server_id, message_id, user = payload.guild_id, payload.message_id, payload.user_id

        if user == self.bot.user.id:
            return

        if message_id == self.repo.get_queuemessage(server_id):
            await self.handle_emoji(payload)
            return

    """
    Process reactions being removed from the queue message
    """
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        server_id, message_id, user = payload.guild_id, payload.message_id, payload.user_id

        if user == self.bot.user.id:
            return
        
        if message_id == self.repo.get_queuemessage(server_id):
            await self.handle_emoji(payload)
            return

    """
    Create dictionary key - value pairs for every server
    """
    def fill_dictionaries(self):
        servers = self.repo.get_server_ids_music()
        if not servers:
            return
        for ID in servers:
            ID = ID[0]
            self.is_playing[ID] = False
            self.voice_channel[ID] = ""
            self.music_queue[ID] = []

    """
    Manage vc, queue and playing state when adding/removing emoji on the queue message
    """
    def stop_command(self, server_id):
        self.voice_channel[server_id].stop()
        self.music_queue[server_id].clear()
        self.is_playing[server_id] = False

    def pause_command(self, server_id):
        self.voice_channel[server_id].pause()

    def resume_command(self, server_id):
        self.voice_channel[server_id].resume()

    def skip_command(self, server_id):
        self.voice_channel[server_id].stop()

    """
    Update the content of the queue message to reflect the current queue
    """
    async def update_queue(self, server_id):
        server = self.bot.get_guild(server_id)
        music_channel = await server.fetch_channel(self.repo.get_musicchannel(server_id))
        queue_message = await music_channel.fetch_message(self.repo.get_queuemessage(server_id))

        if len(self.music_queue[server_id]) == 0:
            song_lijst = "*enter song title to start playing music*"
        else:
            song_lijst = f"*currently playing:*\n**{self.music_queue[server_id][0]['title']}**\n"

        if len(self.music_queue[server_id]) > 1:
            song_lijst += "\t\n*queue:*"

        if len(self.music_queue[server_id]) <= 11:
            for i in range(1, len(self.music_queue[server_id])):
                song_lijst += f"\n{i}. **{self.music_queue[server_id][i]['title']}**"
        elif len(self.music_queue[server_id]) > 11:
            for i in range(1, 11):
                song_lijst += f"\n{i}. {self.music_queue[server_id][i]}"

            song_lijst += f"\n*and **{len(self.music_queue[server_id]) - 11}** more*"    

        queue_embed = discord.Embed(title="**QUEUE**", description=song_lijst)
        await queue_message.edit(embed=queue_embed)

    """
    Process the content of a message
    """
    async def process_message(self, message: Message, server_id):
        Commands = self.bot.get_cog('Commands')

        content = message.content
        author = message.author

        if author == self.bot.user:
            return

        await asyncio.sleep(1)
        await message.delete()

        if self.bot.theme.get("prefix", self.bot.config.get("themes")["default"]["prefix"]) in content:
            return

        try:
            author_vc = message.author.voice.channel
        except AttributeError:
            await author.send("Please join a vc before queueing songs")
            return      

        song = self.search_song(content)
        if not song:
            await author.send("Error with song: invalid url")
            return
        elif song['duration'] > 600:
            await author.send("Error with song: duration over 10 minutes")
            return

        self.music_queue[server_id].append(song)

        if not self.is_playing[server_id]:
            self.voice_channel[server_id] = await author_vc.connect()
            await self.play_music(message)

        await self.update_queue(server_id)

    """
    Process the payload of an added or removed reaction 
    """
    async def handle_emoji(self, payload: RawReactionActionEvent): 
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
            await self.voice_channel[server_id].disconnect()
            await self.update_queue(server_id)
        return

    """
    Extract the info of the top result of a youtube or soundcloud search
    """
    def search_song(self, message):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            platforms = ['youtube.com', 'youtu.be', 'soundcloud.com']
            if any(platform in message for platform in platforms):
                try:
                    info = ydl.extract_info(message, download=False)
                except Exception as e:
                    print(e)
                    return False
            else:
                try:
                    info = ydl.extract_info("ytsearch:%s" % message, download=False)['entries'][0]
                except Exception as e:
                    print(e)
                    return False
            return {'source': info['url'], 'title': info['title'], 'duration': info['duration']}

    """
    Play audio in a vc
    """
    async def play_music(self, ctx: Context):
        server_id = ctx.guild.id
        self.is_playing[server_id] = True

        while len(self.music_queue.get(server_id)) > 0:
            await self.update_queue(server_id)
            url = self.music_queue[server_id][0]['source']
            audio_source = discord.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS)
            self.voice_channel[server_id].play(discord.PCMVolumeTransformer(audio_source, volume=0.05))

            while self.voice_channel[server_id].is_playing() or self.voice_channel[server_id].is_paused():
                await asyncio.sleep(1)

            if self.is_playing[server_id]:
                self.music_queue[server_id].pop(0)

        await self.voice_channel[server_id].disconnect()
        self.is_playing[server_id] = False

def setup(bot):
    bot.add_cog(Music(bot))
