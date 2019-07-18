import os

import discord
import discord.ext.commands as commands

from cogs.utils.sniper import Sniper

from data import api as Database
from data.api import Environment


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.has_role(item='Dev Team')
    async def q2(self, ctx):
        await self.bot.logout()

    @commands.command(name='remove_user', brief='(Admin-Only) Removes a user from the sniping leaderboard')
    @commands.has_role(item='Dev Team')
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
            success = Database.removeUser(member.id)

            if success:
                await ctx.send('```User removed.```')
            else:
                await ctx.send('```Error: User failed to be removed.```')
        else:
            await ctx.send('```User lives to fight another day.```')

    @commands.command(name='RegisterUser', hidden=True)
    @commands.has_role(item='Dev Team')
    async def registerUser(self, ctx: commands.Context, user: discord.Member):
        user = Sniper.from_database(user.id, ctx.guild, user.display_name)
        user.register_self()

        await ctx.send('```User succesfully added.```')

    @commands.command(name='SetSnipes', hidden=True)
    @commands.has_role(item='Dev Team')
    async def setSnipes(self, ctx: commands.Context, user: discord.Member, amount: int):
        response = Database.setSnipes(user.id, amount)

        msg = '```User snipes updated.```'

        if not response:
            msg = '```Potential Error - User could not be updated.```'

        await ctx.send(msg)

    @commands.command(name='SetPoints', hidden=True)
    @commands.has_role(item='Dev Team')
    async def setPoints(self, ctx: commands.Context, user: discord.Member, amount: int):
        response = Database.setPoints(user.id, amount)

        msg = '```User points updated.```'

        if not response:
            msg = '```Potential Error - User could not be updated.```'

        await ctx.send(msg)

    @commands.command(name='AddPoints', hidden=True)
    @commands.has_role(item='Dev Team')
    async def addPoints(self, ctx: commands.Context, user: discord.Member, amount: int):
        response = Database.addPoints(user.id, amount)

        msg = '```User points added.```'

        if not response:
            msg = '```Potential Error - User could not be updated.```'

        await ctx.send(msg)

    @commands.command(name='SetDeaths', hidden=True)
    @commands.has_role(item='Dev Team')
    async def setDeaths(self, ctx: commands.Context, user: discord.Member, amount: int):
        response = Database.setDeaths(user.id, amount)

        msg = '```User deaths updated.```'

        if not response:
            msg = '```Potential Error - User could not be updated.```'

        await ctx.send(msg)

    @commands.command(name='switchDB', hidden=True)
    @commands.has_role(item="Dev Team")
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

        response = Database.switchDatabase(dbEnv)

        if response:
            await ctx.send('Database successfully changed.')
            print('Database: ' + Database.DATABASE)
        else:
            await ctx.send('Error changing database.')

    @commands.command(name='db_env', hidden=True)
    @commands.has_role(item='Dev Team')
    async def db_environment(self, ctx: commands.Context, env=None):
        if Database.DATABASE == Database.DEV_DATABASE:
            await ctx.send('```Dev```')
        else:
            await ctx.send('```Live```')

    # region CPU Health
    @commands.command(name='HealthCheck', brief='Returns a health check for the bot and the Pi',
                      help='It\'s the simplest one in the book')
    async def getHealth(self, ctx: commands.Context):

        healthStr = 'Tell the Indies that the Pi said hello.\n\n'
        heat = self.getCPUtemperature()
        healthStr += 'Temp: {}C | {:.2f}F\n'.format(heat,
                                                    9.0 / 5.0 * float(heat) + 32)
        healthStr += 'Free RAM: {}KB\n'.format(
            int(float(self.getRAMinfo()[1]) / 1024))
        healthStr += 'Current CPU Usage: {}%\n'.format(self.getCPUuse())

        await ctx.send(healthStr)

    # Return CPU temperature as a character string
    def getCPUtemperature(self):
        res = os.popen('vcgencmd measure_temp').readline()
        return(res.replace("temp=", "").replace("'C\n", ""))

    # Return RAM information (unit=kb) in a list
    # Index 0: total RAM
    # Index 1: used RAM
    # Index 2: free RAM
    def getRAMinfo(self):
        p = os.popen('free')
        i = 0
        while 1:
            i = i + 1
            line = p.readline()
            if i == 2:
                return(line.split()[1:4])

    # Return % of CPU used by user as a character string
    def getCPUuse(self):
        return(str(os.popen(r"top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip()))

    # endregion CPU Health

    @commands.command(name='backup_db')
    @commands.has_role(item='Dev Team')
    async def backup_db(self, ctx: commands.Context):
        dev_db = discord.File(fp='./data/dev_database.db')
        live_db = discord.File(fp='./data/database.db')

        dm_channel = ctx.author.dm_channel

        if dm_channel is None:
            await ctx.author.create_dm()

        dm_channel = ctx.author.dm_channel

        await dm_channel.send('', files=[dev_db, live_db])

    @commands.command(name='update_scores_names')
    @commands.has_role(item='Dev Team')
    async def update_scores_names(self, ctx: commands.Context):
        if Database.update_scores_names(ctx.guild.members):
            await ctx.send('```Usernames updated.```')
        else:
            await ctx.send('```Usernames failed to be updated.```')

    @commands.command()
    @commands.has_role(item='Dev Team')
    async def assign_sniper_role(self, ctx: commands.Context):
        userIds = Database.getAllUsers()
        role = discord.utils.get(ctx.guild.roles, name='Sniper Team')

        for userId in userIds:
            member = ctx.guild.get_member(userId)
            await member.add_roles(role)
