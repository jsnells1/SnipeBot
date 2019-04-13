from discord import User, Member, Embed, Guild
from discord.ext.commands import Cog, Context, command

from data import bot_database


class AdminCommands(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.OWNER_ID = 273946109896818701

    def check_if_owner(self, ctx: Context):
        return ctx.message.author.id == self.OWNER_ID

    @command(name='RemoveUser', hidden=True)
    async def removeUser(self, ctx: Context, user: Member):
        response = bot_database.removeUser(user.id)

        msg = '```User succesfully deleted.```'

        if not response:
            msg = '```Potential Error - User could not be deleted.```'

        await ctx.send(msg)

    @command(name='SetSnipes', hidden=True)
    async def setSnipes(self, ctx: Context, user: Member, amount: int):
        response = bot_database.setSnipes(user.id, amount)

        msg = '```User snipes updated.```'

        if not response:
            msg = '```Potential Error - User could not be updated.```'

        await ctx.send(msg)

    @command(name='SetDeaths', hidden=True)
    async def setDeaths(self, ctx: Context, user: Member, amount: int):
        response = bot_database.setDeaths(user.id, amount)

        msg = '```User deaths updated.```'

        if not response:
            msg = '```Potential Error - User could not be updated.```'

        await ctx.send(msg)
