import discord
import discord.ext.commands as commands

from data import code
from data.code import Environment


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='remove_user', brief='(Admin-Only) Removes a user from the sniping leaderboard')
    @commands.has_permissions(ban_members=True)
    async def removeUser(self, ctx: commands.Context, member: discord.Member):
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
            success = code.removeUser(member.id)
            
            if success:
                await ctx.send('```User removed.```')
            else:
                await ctx.send('```Error: User failed to be removed.```')
        else:
            await ctx.send('```User lives to fight another day.```')

    @commands.command(name='RegisterUser', hidden=True)
    @commands.is_owner()
    async def registerUser(self, ctx: commands.Context, user: discord.Member):
        response = code.registerUser(user.id)

        msg = '```User succesfully added.```'

        if not response:
            msg = '```Potential Error - User could not be added.```'

        await ctx.send(msg)

    @commands.command(name='SetSnipes', hidden=True)
    @commands.is_owner()
    async def setSnipes(self, ctx: commands.Context, user: discord.Member, amount: int):
        response = code.setSnipes(user.id, amount)

        msg = '```User snipes updated.```'

        if not response:
            msg = '```Potential Error - User could not be updated.```'

        await ctx.send(msg)

    @commands.command(name='SetDeaths', hidden=True)
    @commands.is_owner()
    async def setDeaths(self, ctx: commands.Context, user: discord.Member, amount: int):
        response = code.setDeaths(user.id, amount)

        msg = '```User deaths updated.```'

        if not response:
            msg = '```Potential Error - User could not be updated.```'

        await ctx.send(msg)

    @commands.command(name='switchDB', hidden=True)
    @commands.has_permissions(ban_members=True)
    async def switchDB(self, ctx: commands.Context, env=None):

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

        response = code.switchDatabase(dbEnv)

        if response:
            await ctx.send('Database successfully changed.')
        else:
            await ctx.send('Error changing database.')

    @commands.command(name='db_environment', hidden=True)
    @commands.has_permissions(ban_members=True)
    async def getDBEnvironment(self, ctx: commands.Context, env=None):

        if code.DATABASE == code.DEV_DATABASE:
            await ctx.send('```Dev```')
        else:
            await ctx.send('```Live```')
