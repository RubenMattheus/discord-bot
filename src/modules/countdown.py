from discord.ext import commands, tasks
from discord.ext.commands import Context, Bot
from datetime import datetime
import random
from src.db import Repository
from src.cmds import check_for_admin

class Countdown(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.repo = Repository()

    """
    Starts the countdown function
    """
    @commands.Cog.listener()
    async def on_ready(self):
        self.send_countdown.start()

    """
    (Admin permissions needed)
    Start a countdown in the countdown channel
    """
    @commands.command()
    async def countdown(self, ctx: Context, day: int = None, month: int = None, year: int = None):
        if not await check_for_admin(ctx):
            return
        
        server_id, channel_id = ctx.guild.id, ctx.message.channel.id
        
        if day is None or month is None or year is None:
            await ctx.send(f'Usage: {self.bot.theme.get("prefix")}countdown <day> <month> <year>')
            return

        try:
            test_date = datetime(year, month, day)
        except ValueError:
            await ctx.send("Invalid date. Please provide a valid day, month and year.")
            return

        try:
            self.repo.add_countdown(server_id, channel_id, day, month, year)
            await ctx.send(f"Countdown set to {day}/{month}/{year}.")
        except Exception as e:
            await ctx.send(f"Error saving countdown: {e}")

    """
    Send countdown every day at 06:00
    """
    @tasks.loop(minutes=1)
    async def send_countdown(self):
        countdowns = self.repo.get_countdowns()

        for cd in countdowns:
            server_id, channel_id, day, month, year = cd
            now = datetime.now().date()
            if datetime.now().hour != 6 or datetime.now().minute != 0:
                return
            
            channel = self.bot.get_channel(channel_id)
            if not channel:
                return
            
            try:
                target_date = datetime(year, month, day)
            except Exception:
                return
            
            target_date_only = target_date.date()
            delta_days = (target_date_only - now).days
            if delta_days <= 0:
                await channel.send(self.bot.theme.get("countdown_finished", self.bot.config.get("themes")["default"]["countdown_finished"])),
                self.repo.remove_countdown(server_id)
            else:
                day_word = "day" if delta_days == 1 else "days"
                await channel.send(
                    f'{random.choice(self.bot.theme.get("countdown", self.bot.config.get("themes")["default"]["countdown"]))} {delta_days} {day_word}!'
                )

    """
    Ensure bot has started properly before sending the countdown
    """
    @send_countdown.before_loop
    async def before_send_countdown(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Countdown(bot))
