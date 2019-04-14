from discord import User, Member, Embed, Guild
from discord.ext.commands import Cog, Context, command, is_owner

from data.bot_database import BotDatabase


class AdminCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='RemoveUser', hidden=True)
    @is_owner()
    async def removeUser(self, ctx: Context, user: Member):
        response = BotDatabase().removeUser(user.id)

        msg = '```User succesfully deleted.```'

        if not response:
            msg = '```Potential Error - User could not be deleted.```'

        await ctx.send(msg)

    @command(name='RegisterUser', hidden=True)
    @is_owner()
    async def registerUser(self, ctx: Context, user: Member):
        response = BotDatabase().registerUser(user.id)

        msg = '```User succesfully added.```'

        if not response:
            msg = '```Potential Error - User could not be added.```'

        await ctx.send(msg)

    @command(name='SetSnipes', hidden=True)
    @is_owner()
    async def setSnipes(self, ctx: Context, user: Member, amount: int):
        response = BotDatabase().setSnipes(user.id, amount)

        msg = '```User snipes updated.```'

        if not response:
            msg = '```Potential Error - User could not be updated.```'

        await ctx.send(msg)

    @command(name='SetDeaths', hidden=True)
    @is_owner()
    async def setDeaths(self, ctx: Context, user: Member, amount: int):
        response = BotDatabase().setDeaths(user.id, amount)

        msg = '```User deaths updated.```'

        if not response:
            msg = '```Potential Error - User could not be updated.```'

        await ctx.send(msg)
