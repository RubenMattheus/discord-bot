import json
import discord
from discord.ext import commands
from discord.ext.commands import Context, Bot
from src.db import Repository

class Todo(commands.Cog):
    """ Todo class for todo list functionality """
    def __init__(self, bot: Bot):
        self.bot = bot
        self.repo = Repository()

    @commands.command()
    async def todo(self, ctx: Context):
        """ Generate embed for the todo list and send it """
        server_id = ctx.guild.id

        todo = self.repo.get_todo(server_id)

        if (todo is None or todo[0] == "{}"):
            await ctx.send("No todo list made yet")
            return

        text = "\t"
        todo_dict = json.loads(todo[0])
        for task in todo_dict:
            text += f"\n {task} - {todo_dict[task]}"

        embed = discord.Embed(
            title='TODO',
            description=f'{text}',
            color=discord.Color.from_rgb(40, 11, 15)
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def add(self, ctx: Context, task: str, count: int):
        """ Add element to todo list """
        server_id = ctx.guild.id

        todo = self.repo.get_todo(server_id)
        if not todo:
            todo_dict = {}
        else:
            todo_dict = json.loads(todo[0])

        todo_dict[task] = todo_dict.get(task, 0) + count

        todo_text = json.dumps(todo_dict)
        self.repo.add_todo(server_id, todo_text)

        await self.todo(ctx)

    @commands.command()
    async def done(self, ctx: Context, task: str, count: int):
        """ Remove element from todo list """
        server_id = ctx.guild.id

        todo = self.repo.get_todo(server_id)
        todo_dict = json.loads(todo[0])

        todo_dict[task] = todo_dict.get(task, 0) - count
        if todo_dict[task] <= 0:
            todo_dict.pop(task)

        todo_text = json.dumps(todo_dict)
        self.repo.add_todo(server_id, todo_text)

        if todo_text != "{}":
            await self.todo(ctx)
        else:
            await ctx.send("Todo list finished!")

def setup(bot):
    """ Add cog to the Discord bot """
    bot.add_cog(Todo(bot))
