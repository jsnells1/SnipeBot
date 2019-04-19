import calendar
import asyncio
from datetime import datetime

import discord
import discord.ext.commands as commands

from data import code
from data.code import Environment

import sniping._carepackage as CarePackage


class Snipes(commands.Cog):
    def __init__(self, bot, day, start, end):
        self.bot = bot
        self.club_day = day
        self.club_start = start
        self.club_end = end
        self.general_channel = 427276681510649868
        self.test_channel = 566076016825597972
        self.snipe_channel = 568115558206406656
        self.indies_guild = 427276681510649866
        self.bg_task = self.bot.loop.create_task(self.maintenance())

    async def maintenance(self):
        await self.bot.wait_until_ready()

        if code.DATABASE == code.DEV_DATABASE:
            channel = self.bot.get_channel(self.test_channel)
        else:
            channel = self.bot.get_channel(self.snipe_channel)
        guild = self.bot.get_guild(self.indies_guild)

        while not self.bot.is_closed():
            respawns = code.getAllRespawns()
            code.removeExpiredRevenges()

            if len(respawns) > 0:
                users = []
                for user in respawns:
                    users.append(guild.get_member(int(user)).nick)

                await channel.send('```The following user(s) have respawned: {}```'.format(', '.join(users)))
            await asyncio.sleep(60)

    # Returns a user's points or snipes

    @commands.command(name='Points', brief='Returns the calling user\'s points (or snipes)',
                      help='Returns the calling user\'s points (or snipes)\nIf the user doesn\'t exists, they will be prompted to register their account')
    async def getPoints(self, ctx: commands.Context):
        author = ctx.message.author
        points = code.getUserPoints(author.id)

        if not points:
            await ctx.send("Error retrieving points...")

        if points is None:
            success = code.registerUser(ctx.author.id)

            if not success:
                await ctx.send('User was not found and failed to be registered.')
                return
            else:
                points = code.getUserPoints(author.id)

        await ctx.send("{} you have {} point(s)".format(author.mention, points))

    # Registers a snipe with snipe bot

    @commands.command(name='Snipe', brief='Registers a snipe from the calling user to the mentioned user', usage='<@TargetUser>',
                      help='Registers a snipe from the calling user to the mentioned user.\nBoth the calling and mentioned users will be created if not already.')
    async def snipeUser(self, ctx: commands.Context, *losers: discord.Member):

        if ctx.message.channel.id != self.snipe_channel and ctx.message.channel.id != self.test_channel:
            await ctx.send('Please use the snipebot channel for sniping :)')
            return

        today = datetime.now()

        if today.weekday() == self.club_day and today.hour >= self.club_start and today.hour < self.club_end:
            await ctx.send('```Sniping disabled during club hours: {} from {}:00 to {}:00 (Military Time)```'.format(calendar.day_name[self.club_day], self.club_start, self.club_end))
            return

        if len(losers) == 0:
            await ctx.send('To snipe a user, type !snipe <@Target>. You can snipe multiple users by typing !snipe <@Target1> <@Target2> etc..')
            return

        if any(x.id == ctx.author.id for x in losers):
            await ctx.send('Sorry, you cannot snipe yourself...')
            return

        hits = []
        respawns = []
        errors = []
        leaderId = code.getLeader()
        revengeId = code.getRevengeUser(ctx.author.id)
        bonusPoints = 0
        leaderHit = False
        revengeHit = False

        for loser in losers:
            if loser.bot:
                continue
            if code.isRespawning(loser.id):
                respawns.append(loser.nick)
            elif code.addSnipe(ctx.author.id, loser.id):
                if loser.id == leaderId:
                    leaderHit = True
                    bonusPoints += 3

                if loser.id == revengeId:
                    revengeHit = True
                    bonusPoints += 2
                    code.resetRevenge(ctx.author.id)

                hits.append(loser.nick)
            else:
                errors.append(loser.nick)

        code.addPoints(ctx.author.id, bonusPoints)

        returnStr = ''

        if len(hits) == 1:
            returnStr += 'SNIPED! {} has sniped {}!\n'.format(
                ctx.author.nick, hits[0])
        elif len(hits) > 1:
            returnStr += 'SNIPED! {} has sniped {}!\n'.format(
                ctx.author.nick, ', '.join(hits[:-1]) + ' and ' + hits[-1])

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

    @snipeUser.error
    async def sniperUser_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('```Command failed (Bad Arguments): Please resubmit your snipe\n\
Ensure you write the command as !snipe @Target1 @Target2 etc..\n\
Be sure not to write any other text like:\n\
\t!snipe @Justin Got you Justin!\n\
This will fail.```')

    # Returns the current leaderboard

    @commands.command(name='Leaderboard', brief='Returns the Top 10 users sorted by snipes')
    async def leaderboard(self, ctx: commands.Context):
        rows = code.getLeaderboard()
        if not rows:
            await ctx.send('```Error retrieving leaderboard```')
            return

        _padding = 3
        _paddingString = ' ' * _padding
        _userColName = 'Name'
        _pointsColName = 'P'
        _snipesColName = 'S'
        _deathsColName = 'D'

        nameColLength = len(_userColName)
        pointsColLength = len(_pointsColName)
        snipeColLength = len(_snipesColName)
        deathColLength = len(_deathsColName)

        for i, row in enumerate(rows):
            user = ctx.guild.get_member(int(row[0]))

            name = '{:<4}'.format(str(i + 1) + '.') + user.nick[0:10]

            nameColLength = max(nameColLength, len(name))
            pointsColLength = max(pointsColLength, len(str(row[1])))
            snipeColLength = max(snipeColLength, len(str(row[2])))
            deathColLength = max(deathColLength, len(str(row[3])))

        output = _userColName + _paddingString + \
            ((nameColLength - len(_userColName)) * ' ')
        output += _pointsColName + _paddingString + \
            ((pointsColLength - len(_pointsColName)) * ' ')
        output += _snipesColName + _paddingString + \
            ((snipeColLength - len(_snipesColName)) * ' ')
        output += _deathsColName + \
            ((deathColLength - len(_deathsColName)) * ' ') + '\n'
        output += '-' * (_padding * 3 + nameColLength + pointsColLength +
                         snipeColLength + deathColLength) + '\n'

        for i, row in enumerate(rows):
            user = ctx.guild.get_member(int(row[0]))

            name = '{:<4}'.format(str(i + 1) + '.') + user.nick[0:10]

            output += name + _paddingString + \
                ((nameColLength - len(name)) * ' ')
            output += str(row[1]) + _paddingString + \
                ((pointsColLength - len(str(row[1]))) * ' ')
            output += str(row[2]) + _paddingString + \
                ((snipeColLength - len(str(row[2]))) * ' ')
            output += str(row[3]) + \
                ((deathColLength - len(str(row[3]))) * ' ') + '\n'

        await ctx.send('```' + output + '```')

    @commands.command(name='set_carepackage', hidden=True)
    @commands.has_role(item="Dev Team")
    async def set_carepackage_cmd(self, ctx: commands.Context, keyword, time, hint):
        await ctx.send(CarePackage.set_carepackage(keyword, time, hint))
