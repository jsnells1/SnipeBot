import discord
import discord.ext.commands as commands

import cogs.utils.db as Database
from cogs.utils.db import Environment
from cogs.utils.sniper import Sniper


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='remove_user', brief='(Admin-Only) Removes a user from the sniping leaderboard')
    @commands.has_role(item='Dev Team')
    async def removeUser(self, ctx: commands.Context, member: discord.Member):
        if not await Sniper.exists(member.id, member.guild.id):
            await ctx.send('User is not registered.')

        await ctx.send(f'Are you sure you want to remove user: {member.display_name} (Y/N)')

        author = ctx.message.author
        channel = ctx.message.channel

        def check(m):
            return (m.content in ('y', 'Y', 'n', 'N')) and m.channel == channel and m.author.id == author.id

        try:
            response = await self.bot.wait_for('message', check=check, timeout=10)
        except:
            await ctx.send('Timeout reached. User lived to fight another day.')
            return

        if response.content == 'Y' or response.content == 'y':
            try:
                await Sniper.remove_user(member.id, member.guild.id)
                await ctx.send('User removed.')
            except:
                await ctx.send('Error: User failed to be removed.')
        else:
            await ctx.send('User lives to fight another day.')

    @commands.command(name='RegisterUser', hidden=True)
    @commands.has_role(item='Dev Team')
    async def registerUser(self, ctx: commands.Context, user: discord.Member):
        user = await Sniper.from_database(user.id, ctx.guild, user.display_name, register=True)

        await ctx.send('User succesfully added.')

    @commands.command(name='SetSnipes', hidden=True)
    @commands.has_role(item='Dev Team')
    async def setSnipes(self, ctx: commands.Context, user: discord.Member, amount: int):
        user = await Sniper.from_database(user.id, user.guild, user.display_name, register=True)
        user.snipes = amount

        await user.update()
        await ctx.send('Done')

    @commands.command(name='SetPoints', hidden=True)
    @commands.has_role(item='Dev Team')
    async def setPoints(self, ctx: commands.Context, user: discord.Member, amount: int):
        user = await Sniper.from_database(user.id, user.guild, user.display_name, register=True)
        user.points = amount

        await user.update()
        await ctx.send('Done')

    @commands.command(name='SetDeaths', hidden=True)
    @commands.has_role(item='Dev Team')
    async def setDeaths(self, ctx: commands.Context, user: discord.Member, amount: int):
        user = await Sniper.from_database(user.id, user.guild, user.display_name, register=True)
        user.deaths = amount

        await user.update()
        await ctx.send('Done')

    @commands.command(name='switchDB', hidden=True)
    @commands.has_role(item="Dev Team")
    async def switchDB(self, ctx: commands.Context, env=None):
        if env is None:
            await ctx.send('Please pass the environment to switch to (live/dev)')
            return

        if env == 'live':
            dbEnv = Environment.LIVE
        elif env == 'dev':
            dbEnv = Environment.DEV
        else:
            await ctx.send('Invalid argument.')
            return

        response = Database.switch_database(dbEnv)

        if response:
            await ctx.send('Database successfully changed.')
            print('Database: ' + Database.DATABASE)
        else:
            await ctx.send('Error changing database.')

    @commands.command(name='db_env', aliases=['env', 'environment'], hidden=True)
    @commands.has_role(item='Dev Team')
    async def db_environment(self, ctx: commands.Context, env=None):
        if Database.DATABASE == Database.DEV_DATABASE:
            await ctx.send('**Dev**')
        else:
            await ctx.send('**Live**')

    @commands.command(name='update_names')
    @commands.has_role(item='Dev Team')
    async def update_names(self, ctx: commands.Context):
        num_updated = 0

        for member in ctx.guild.members:
            if await Sniper.exists(member.id, member.guild.id):
                user = await Sniper.from_database(member.id, member.guild.id, member.display_name)
                await user.update()
                num_updated += 1

        await ctx.send(f'Done - Updated {num_updated} member(s)')
