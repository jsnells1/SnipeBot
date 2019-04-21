import os

import discord
import discord.ext.commands as commands


from data import code as Database
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
            success = Database.removeUser(member.id)

            if success:
                await ctx.send('```User removed.```')
            else:
                await ctx.send('```Error: User failed to be removed.```')
        else:
            await ctx.send('```User lives to fight another day.```')

    @commands.command(name='RegisterUser', hidden=True)
    @commands.is_owner()
    async def registerUser(self, ctx: commands.Context, user: discord.Member):
        response = Database.registerUser(user.id)

        msg = '```User succesfully added.```'

        if not response:
            msg = '```Potential Error - User could not be added.```'

        await ctx.send(msg)

    @commands.command(name='SetSnipes', hidden=True)
    @commands.is_owner()
    async def setSnipes(self, ctx: commands.Context, user: discord.Member, amount: int):
        response = Database.setSnipes(user.id, amount)

        msg = '```User snipes updated.```'

        if not response:
            msg = '```Potential Error - User could not be updated.```'

        await ctx.send(msg)

    @commands.command(name='SetPoints', hidden=True)
    @commands.is_owner()
    async def setPoints(self, ctx: commands.Context, user: discord.Member, amount: int):
        response = Database.setPoints(user.id, amount)

        msg = '```User points updated.```'

        if not response:
            msg = '```Potential Error - User could not be updated.```'

        await ctx.send(msg)

    @commands.command(name='SetDeaths', hidden=True)
    @commands.is_owner()
    async def setDeaths(self, ctx: commands.Context, user: discord.Member, amount: int):
        response = Database.setDeaths(user.id, amount)

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

        response = Database.switchDatabase(dbEnv)

        if response:
            await ctx.send('Database successfully changed.')
        else:
            await ctx.send('Error changing database.')

    @commands.command(name='db_environment', hidden=True)
    @commands.has_role(item='Dev Team')
    async def getDBEnvironment(self, ctx: commands.Context, env=None):

        if Database.DATABASE == Database.DEV_DATABASE:
            await ctx.send('```Dev```')
        else:
            await ctx.send('```Live```')

    @commands.command(name='HealthCheck', brief='Returns a health check for the bot and the Pi',
                      help='It\'s the simplest one in the book')
    async def getHealth(self, ctx: commands.Context):

        healthStr = 'Tell the Indies that the Pi said hello.\n\n'
        heat = self.getCPUtemperature()
        healthStr += 'Temp: {}C | {}F\n'.format(heat,
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

    @commands.command(name='admin_snipe')
    @commands.has_role(item='Dev Team')
    async def admin_snipe(self, ctx: commands.Context, *members: discord.Member):
        if len(members) < 1:
            return

        sniper = members[0]

        hits = []
        respawns = []
        errors = []
        leaderId = Database.getLeader()
        revengeId = Database.getRevengeUser(sniper.id)
        bonusPoints = 0
        leaderHit = False
        revengeHit = False

        for loser in members[1:]:
            if loser.bot:
                continue
            if Database.isRespawning(loser.id):
                respawns.append(loser.display_name)
            elif Database.addSnipe(sniper.id, loser.id):
                if loser.id == leaderId:
                    leaderHit = True
                    bonusPoints += 3

                if loser.id == revengeId:
                    revengeHit = True
                    bonusPoints += 2
                    Database.resetRevenge(sniper.id)

                hits.append(loser.nick)
            else:
                errors.append(loser.nick)

        Database.addPoints(sniper.id, bonusPoints)

        returnStr = ''

        if len(hits) == 1:
            returnStr += 'SNIPED! {} has sniped {}!\n'.format(
                sniper.nick, hits[0])
        elif len(hits) > 1:
            returnStr += 'SNIPED! {} has sniped {}!\n'.format(
                sniper.nick, ', '.join(hits[:-1]) + ' and ' + hits[-1])

        if leaderHit:
            returnStr += 'NICE SHOT! The leader has been taken out! Enjoy 3 bonus points!\n'

        if revengeHit:
            revenge = ctx.guild.get_member(revengeId)
            returnStr += 'Revenge is so sweet! You got revenge on {}! Enjoy 2 bonus points!\n'. format(
                revenge.nick)

        if len(respawns) == 1:
            returnStr += '{} was not hit because they\'re still respawning.\n'.format(
                respawns[0])
        elif len(respawns) > 1:
            returnStr += '{} were not hit because they\'re still respawning.\n'.format(
                ', '.join(respawns[:-1]) + ' and ' + respawns[-1])

        if len(errors) == 1:
            returnStr += 'Error registering hit on {}.\n'.format(errors[0])
        elif len(errors) > 1:
            returnStr += 'Error registering hit on {}.\n'.format(
                ', '.join(errors[:-1]) + ' and ' + errors[-1])

        await ctx.send(returnStr)
