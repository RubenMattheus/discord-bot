import random
from datetime import datetime
from discord.ext import commands, tasks
from discord.ext.commands import Context, Bot
from src.db import Repository
from src.commands import check_for_admin

class Countdown(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.repo = Repository()

    @commands.Cog.listener()
    async def on_ready(self):
        """ Starts the countdown function """
        self.send_countdown.start()

    @commands.command()
    async def countdown(self, ctx: Context, day: int = None, month: int = None, year: int = None):
        """
        Starts a countdown in the countdown channel

        < requires admin permissions >
        """
        if not await check_for_admin(ctx):
            return

        server_id, channel_id = ctx.guild.id, ctx.message.channel.id

        if day is None or month is None or year is None:
            await ctx.send(f'Usage: {self.bot.get_theme_value("prefix")}countdown <day> <month> <year>')
            return

        try:
            _ = datetime(year, month, day)
        except ValueError:
            await ctx.send("Invalid date. Please provide a valid day, month and year.")
            return

        try:
            self.repo.add_countdown(server_id, channel_id, day, month, year)
            await ctx.send(f"Countdown set to {day}/{month}/{year}.")
        except Exception as e:
            await ctx.send(f"Error saving countdown: {e}")

    @tasks.loop(minutes=1)
    async def send_countdown(self):
        """ Send countdown every day at 06:00 """
        now = datetime.now()
        if now.hour != 6 or now.minute != 0:
            return

        countdowns = self.repo.get_countdowns()

        for cd in countdowns:
            server_id, channel_id, day, month, year = cd

            channel = self.bot.get_channel(channel_id)
            if not channel:
                continue

            try:
                target_date = datetime(year, month, day)
            except ValueError:
                continue

            delta_days = (target_date.date() - now.date()).days
            if delta_days <= 0:
                await channel.send(self.bot.get_theme_value("countdown_finished"))
                self.repo.remove_countdown(server_id)
            else:
                day_word = "day" if delta_days == 1 else "days"
                await channel.send(
                    f"{random.choice(self.bot.get_theme_value('countdown'))} {delta_days} {day_word}!"
                )

    @send_countdown.before_loop
    async def before_send_countdown(self):
        await self.bot.wait_until_ready()
