import discord
from discord.ext import commands
from discord.ext.commands import Context, Bot
from src.data.repository import Repository

class Commands(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.repo = Repository()
        self.bot.add_check(self.not_in_music_channel)

    async def not_in_music_channel(self, ctx: Context):
        if ctx.channel.id != self.repo.get_musicchannel(ctx.guild.id):
            return True
        else:
            target = ctx.author
            await target.send("Can't use commands in the music channel")
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error):
        print(f"{error} user: {ctx.message.author}")

    @commands.command()
    async def help(self, ctx: Context):
        text = "\t"

        for command in self.bot.commands:
            if command.cog_name != "Commands" or "help" in command.name:
                continue
            text += f"\n- {command}"

        bottomtext = "\n\nMore commands: jokehelp & adminhelp"
        embed = discord.Embed(title='Commands', description=f'{text} {bottomtext}', color=discord.Color.from_rgb(40, 11, 15))
        await ctx.send(embed=embed)

    @commands.command()
    async def music(self, ctx: Context):
        server_id = ctx.message.guild.id
        music_channel = self.repo.get_musicchannel(server_id)
        music_channel = await ctx.message.guild.fetch_channel(music_channel)
        await ctx.send(music_channel.mention)


def setup(bot):
    bot.add_cog(commands(bot))
