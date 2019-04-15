from discord import User, Member, Embed, Guild
from discord.ext.commands import Cog, Context, command, is_owner, has_permissions

from data.code.bot_database import BotDatabase, Environment


class AdminCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='remove_user', brief='(Admin-Only) Removes a user from the sniping leaderboard')
    @has_permissions(ban_members=True)
    async def removeUser(self, ctx: Context, member: Member):
        await ctx.send('Are you sure you want to remove user: {} (Y/N)'.format(member.nick))

        author = ctx.message.author
        channel = ctx.message.channel

        def check(m):
            return (m.content == 'Y' or m.content == 'N' or m.content == 'n' or m.content == 'y') and m.channel == channel and m.author.id == author.id

        try:
            response = await self.bot.wait_for('message', check=check, timeout=10)
        except:
            await ctx.send("```Timeout reached. User lived to fight another day.```")
            return

        if response.content == 'Y' or response.content == 'y':
            success = BotDatabase().removeUser(member.id)

            if success:
                await ctx.send('```User removed.```')
            else:
                await ctx.send('```Error: User failed to be removed.```')
        else:
            await ctx.send('```User lives to fight another day.```')

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

    @command(name='switchDB', hidden=True)
    @has_permissions(ban_members=True)
    async def switchDB(self, ctx: Context, env=None):

        if env is None:
            await ctx.send('Please pass the environment to switch to (live/dev)')
            return

        if env == 'live':
            dbEnv = Environment.live
        elif env == 'dev':
            dbEnv = Environment.dev
        else:
            await ctx.send('Invalid argument.')
            return

        response = BotDatabase().switchDatabase(dbEnv)

        if response:
            await ctx.send('Database successfully changed.')
        else:
            await ctx.send('Error changing database.')

    @command(name='db_environment', hidden=True)
    @has_permissions(ban_members=True)
    async def getDBEnvironment(self, ctx: Context, env=None):
        
        if BotDatabase().DATABASE == BotDatabase().DEV_DATABASE:
            await ctx.send('```Dev```')
        else:
            await ctx.send('```Live```')
