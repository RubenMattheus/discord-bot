import discord
from discord.ext import commands
from discord.ext.commands import Context, Bot
import asyncio

class AdminCommands(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def adminhelp(self, ctx: Context):
        text = "\t"

        for command in self.bot.commands:
            if command.cog_name != "AdminCommands" or "help" in command.name:
                continue
            text += f"\n- {command}"
            
        embed = discord.Embed(title='Admin commands', description=text, color=discord.Color.from_rgb(40, 11, 15))
        await ctx.send(embed=embed)

    async def check_for_admin(self, ctx: Context):
        if ctx.author.guild_permissions.administrator:
            return True
        else:
            await ctx.message.channel.send(f"{ctx.message.author.mention} : you need admin permissions for this command")
            return False

    @commands.command()
    async def music_setup(self, ctx: Context):
        music = self.bot.get_cog('Music')
        if not await self.check_for_admin(ctx):
            return

        await asyncio.sleep(1)
        await ctx.message.delete()

        await music.setup_queue(ctx)


def setup(bot):
    bot.add_cog(AdminCommands(bot))
