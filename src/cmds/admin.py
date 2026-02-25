from discord.ext import commands
from discord.ext.commands import Context, Bot
import asyncio

"""
Check if the author of the passed context has admin permissions in the server
"""
async def check_for_admin(ctx: Context):
    if ctx.author.guild_permissions.administrator:
        return True
    else:
        await ctx.message.channel.send(f"{ctx.message.author.mention} : you need admin permissions for this command")
        return False

class Admin(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    """
    Mute everyone in the current voice channel after a certain amount of time
    """
    @commands.command()
    async def mutevc(self, ctx: Context, time = "1h"):
        if not await check_for_admin(ctx):
            return
        
        ms_dict = {
            "m" : 60,
            "h" : 3600
        }

        current_number  = ""
        wait_time       = 0
        for char in time:
            if not char.isnumeric() and char not in ms_dict:
                ctx.send("Invalid time format (valid format example: 1h30)")
                return
            
            if char.isnumeric():
                current_number += char

            else:
                wait_time += int(current_number) * ms_dict[char]

        author = ctx.message.author
        try:
            vc = author.voice.channel
        except AttributeError:
            await author.send("Please join a vc before using u!mutevc <time>")
            return      
        
        await ctx.send(f"Muting everyone in {vc.mention} in {time}")

        await asyncio.sleep(wait_time)

        users = vc.members
        for user in users:
            await user.edit(mute=True)

def setup(bot):
    bot.add_cog(Admin(bot))
