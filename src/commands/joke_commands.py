import discord
from discord import Member
from discord.ext import commands
from discord.ext.commands import Context, Bot
import random
import asyncio

class JokeCommands(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def jokehelp(self, ctx: Context):
        text = "\t"

        for command in self.bot.commands:
            if command.cog_name != "JokeCommands" or "help" in command.name:
                continue
            text += f"\n- {command}"

        embed = discord.Embed(title='Joke commands', description=text, color=discord.Color.from_rgb(40, 11, 15))
        await ctx.send(embed=embed)

    @commands.command()
    async def dice(self, ctx: Context, amount = "1"):
        total = 0

        try:
            amount = int(amount)
        except ValueError:
            amount = 1

        if amount < 1 or amount > 5:
            await ctx.send("Give a valid amount of dice (1-5)")
            return

        for i in range(amount):
            await asyncio.sleep(0.5)
            roll = random.randint(1, 6)
            total += roll
            await ctx.send(f"dice {i+1} is a {roll}")

        await asyncio.sleep(0.5)
        await ctx.send(f"total is {total}")

    @commands.command()
    async def rps(self, ctx: Context, member: Member = ""):
        if member == "":
            await ctx.send("Go look for friends to play with")
            return
        elif member == self.bot.user:
            await ctx.send("Go look for REAL friends to play with")
            return
        elif ctx.author == member:
            await ctx.send("Why u trying to play with yourself :face_with_raised_eyebrow:")
            return

        async def send_option(target: Member):
            embed = discord.Embed(title='choose one', color=discord.Color.from_rgb(40, 11, 15))
            dm = await target.send(embed=embed)
            emoji_dict = {
                "rock": "🗿", 
                "paper": "📄",
                "scissors": "✂"
            }

            for emoji in emoji_dict.values():
                await dm.add_reaction(emoji)
    
            try:
                reaction, _ = await self.bot.wait_for("reaction_add",
                                                      check=lambda r, u: u == target and str(r.emoji) in emoji_dict.values(),
                                                      timeout=60.0)
                return next(option for option, emoji in emoji_dict.items() if emoji == str(reaction.emoji))

            except asyncio.TimeoutError:
                return None

        author_choice = await send_option(ctx.author)
        member_choice = await send_option(member)

        win_dict = {
            "rock": "scissors",
            "paper": "rock",
            "scissors": "paper"
        }

        if author_choice == member_choice:
            await ctx.channel.send(f"{ctx.author.mention} and {member.mention} got a draw, both chose {author_choice}")
        elif win_dict.get(author_choice) == member_choice:
            await ctx.channel.send(f"{ctx.author.mention} ({author_choice}) won against {member.mention} ({member_choice})")
        else:
            await ctx.channel.send(f"{member.mention} ({member_choice}) won against {ctx.author.mention} ({author_choice})")

        return

    @commands.command()
    async def blackjack(self, ctx: Context):

        def blackjacktotal(cards: list):
            total = 0
            for card in cards:
                if card == "A":
                    total += 1
                elif card in ["J", "Q", "K"]:
                    total += 10
                else:
                    total += int(card)
                if total <= 11 and "A" in cards:
                    total += 10
            return total

        def add_card(cards: list):
            options = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
            draw = random.randint(0, 12)
            card = options[draw]
            cards.append(card)
            return card
    
        hand = []
        dealer_hand = []

        await ctx.send(f"You draw a {add_card(hand)} and a {add_card(hand)}, your total is {blackjacktotal(hand)}")
        await ctx.send(f"Dealer draws a {add_card(dealer_hand)} and a face down card")
        add_card(dealer_hand)

        if blackjacktotal(hand) == 21:
            if blackjacktotal(dealer_hand) == 21:
                await ctx.send(f"You got a blackjack, dealers hand was {' '.join(str(card) for card in dealer_hand)} resulting in a draw")
                return
            await ctx.send("You got a blackjack, you win!")
            return

        while blackjacktotal(hand) < 21:
            embed = discord.Embed(title='HIT or QUIT', color=discord.Color.from_rgb(40, 11, 15))
            choice = await ctx.send(embed=embed)
            emoji = ["🇭", "🇶"]

            for i in emoji:
                await choice.add_reaction(i)

            def check(reaction, reactor):
                return reactor.id == ctx.author.id and reaction.emoji in emoji

            try:
                reaction, member = await self.bot.wait_for("reaction_add", check=check, timeout=60.0)

                if reaction.emoji == "🇭":
                    await ctx.send(f"You draw a {add_card(hand)}, making your total {blackjacktotal(hand)}")

                if reaction.emoji == "🇶":
                    break

            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.author.mention}: blackjack timed out")
                return

        if blackjacktotal(hand) > 21:
            await ctx.send(f"Bust! You lose...")
            return

        await ctx.send(f"Dealers face down card is a {dealer_hand[1]}, making their total {blackjacktotal(dealer_hand)}")

        while blackjacktotal(dealer_hand) < 17:
            await ctx.send(f"Dealer draws a {add_card(dealer_hand)}, making their total {blackjacktotal(dealer_hand)}")

            if blackjacktotal(dealer_hand) > 21:
                await ctx.send("Dealer busts! You win!")
                return

        if blackjacktotal(hand) > blackjacktotal(dealer_hand):
            await ctx.send(f"Your total is {blackjacktotal(hand)}, dealers total is {blackjacktotal(dealer_hand)}, you win!")
        elif blackjacktotal(hand) < blackjacktotal(dealer_hand):
            await ctx.send(f"Your total is {blackjacktotal(hand)}, dealers total is {blackjacktotal(dealer_hand)}, you lose...")
        else:
            await ctx.send(f"Your total is {blackjacktotal(hand)}, dealers total is {blackjacktotal(dealer_hand)}, you draw")
            
        return


def setup(bot: Bot):
    bot.add_cog(JokeCommands(bot))
