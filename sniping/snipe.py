import calendar
import asyncio
from datetime import datetime

import discord
import discord.ext.commands as commands

from data import code as Database
from data.code import Environment

import sniping.carepackage as CarePackage


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

        if Database.DATABASE == Database.DEV_DATABASE:
            channel = self.bot.get_channel(self.test_channel)
        else:
            channel = self.bot.get_channel(self.snipe_channel)
        guild = self.bot.get_guild(self.indies_guild)

        while not self.bot.is_closed():
            respawns = Database.getAllRespawns()
            Database.removeExpiredRevenges()

            if Database.remove_expired_carepackage():
                print('Expired')

            if len(respawns) > 0:
                users = []
                for user in respawns:
                    users.append(guild.get_member(int(user)).nick)

                await channel.send('```The following user(s) have respawned: {}```'.format(', '.join(users)))
            await asyncio.sleep(60)

    def joinListWithAnd(self, data):
        if len(data) == 0:
            return None

        if len(data) == 1:
            return data[0]

        return ', '.join(data[:-1]) + ' and ' + data[-1]

    # Returns a user's points or snipes

    @commands.command(name='Points', brief='Returns the calling user\'s points (or snipes)',
                      help='Returns the calling user\'s points (or snipes)\nIf the user doesn\'t exists, they will be prompted to register their account')
    async def getPoints(self, ctx: commands.Context):
        author = ctx.message.author
        points = Database.getUserPoints(author.id)

        if not points:
            await ctx.send("Error retrieving points...")

        if points is None:
            success = Database.registerUser(ctx.author.id)

            if not success:
                await ctx.send('User was not found and failed to be registered.')
                return
            else:
                points = Database.getUserPoints(author.id)

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
        immune = []
        respawns = []
        errors = []
        leaderId = Database.getLeader()
        revengeId = Database.getRevengeUser(ctx.author.id)
        bonusPoints = 0
        leaderHit = False
        revengeHit = False
        hasPotato = Database.has_potato(ctx.author.id)

        multiplier = Database.get_multiplier(ctx.author.id)

        if multiplier is None or not multiplier:
            multiplier = 1

        for i, loser in enumerate(losers):

            # Ignore bots
            if loser.bot:
                continue

            # Ignore immune users
            if Database.isImmune(loser.id):
                immune.append(loser.display_name)
                continue

            # Ignore respawning users
            if Database.isRespawning(loser.id):
                respawns.append(loser.display_name)
                continue

            # Try to snipe the user
            if Database.addSnipe(ctx.author.id, loser.id):
                if i == 0 and hasPotato:
                    Database.pass_potato(ctx.author.id, loser.id)

                if loser.id == leaderId:
                    leaderHit = True
                    bonusPoints += 3

                if loser.id == revengeId:
                    revengeHit = True
                    bonusPoints += 2
                    Database.resetRevenge(ctx.author.id)

                hits.append(loser.display_name)
            else:
                errors.append(loser.display_name)

        totalPoints = bonusPoints * multiplier + \
            (len(hits) * multiplier - len(hits))

        Database.addPoints(ctx.author.id, totalPoints)

        returnStr = ''

        if len(hits) > 0:
            returnStr += 'SNIPED! {} has sniped {}!\n'.format(
                ctx.author.display_name, self.joinListWithAnd(hits))

        if hasPotato:
            returnStr += '{} has passed the potato to {}! Get rid of it before it explodes!!!\n'.format(
                ctx.author.display_name, losers[0].display_name)

        if leaderHit:
            returnStr += 'NICE SHOT! The leader has been taken out! Enjoy 3 bonus points!\n'

        if revengeHit:
            revenge = ctx.guild.get_member(revengeId)
            returnStr += 'Revenge is so sweet! You got revenge on {}! Enjoy 2 bonus points!\n'. format(
                revenge.display_name)

        if len(respawns) > 0:
            returnStr += '{} was/were not hit because they\'re still respawning.\n'.format(
                self.joinListWithAnd(respawns))

        if len(immune) > 0:
            returnStr += '{} was/were not hit because they\'re immune!\n'.format(
                self.joinListWithAnd(immune))

        if len(errors) > 0:
            returnStr += 'Error registering hit on {}.\n'.format(
                self.joinListWithAnd(errors))

        returnStr += '\n```Kill Summary:\n\n'
        returnStr += 'Kills:                {}\n'.format(len(hits))
        if leaderHit:
            returnStr += 'Leader Kill Points:   3\n'
        if revengeHit:
            returnStr += 'Revenge Kill Points:  2\n'
        returnStr += 'Multiplier:          x{}\n'.format(multiplier)
        returnStr += 'Total Points:         {}```'.format(
            totalPoints + len(hits))

        await ctx.send(returnStr)

    @snipeUser.error
    async def sniperUser_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('```Command failed (Bad Arguments): Please resubmit your snipe\n\
Ensure you write the command as !snipe @Target1 @Target2 etc..\n\
Be sure not to write any other text like:\n\
\t!snipe @Justin Got you Justin!\n\
This will fail.```')

    @commands.command(name='admin_snipe', hidden=True)
    @commands.has_role(item='Dev Team')
    async def admin_snipe(self, ctx: commands.Context, *members: discord.Member):
        if len(members) < 1:
            return

        sniper = members[0]

        hits = []
        immune = []
        respawns = []
        errors = []
        leaderId = Database.getLeader()
        revengeId = Database.getRevengeUser(ctx.author.id)
        bonusPoints = 0
        leaderHit = False
        revengeHit = False
        hasPotato = Database.has_potato(ctx.author.id)

        multiplier = Database.get_multiplier(ctx.author.id)

        if multiplier is None or not multiplier:
            multiplier = 1

        for i, loser in enumerate(members[1:]):

            # Ignore bots
            if loser.bot:
                continue

            # Ignore immune users
            if Database.isImmune(loser.id):
                immune.append(loser.display_name)
                continue

            # Ignore respawning users
            if Database.isRespawning(loser.id):
                respawns.append(loser.display_name)
                continue

            if Database.addSnipe(sniper.id, loser.id):
                if i == 0 and hasPotato:
                    Database.pass_potato(ctx.author.id, loser.id)

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

        totalPoints = bonusPoints * multiplier + \
            (len(hits) * multiplier - len(hits))

        Database.addPoints(sniper.id, totalPoints)

        returnStr = ''

        if len(hits) > 0:
            returnStr += 'SNIPED! {} has sniped {}!\n'.format(
                sniper.display_name, self.joinListWithAnd(hits))

        if leaderHit:
            returnStr += 'NICE SHOT! The leader has been taken out! Enjoy 3 bonus points!\n'

        if revengeHit:
            revenge = ctx.guild.get_member(revengeId)
            returnStr += 'Revenge is so sweet! You got revenge on {}! Enjoy 2 bonus points!\n'. format(
                revenge.display_name)

        if len(respawns) > 0:
            returnStr += '{} was/were not hit because they\'re still respawning.\n'.format(
                self.joinListWithAnd(respawns))

        if len(immune) > 0:
            returnStr += '{} was/were not hit because they\'re immune!\n'.format(
                self.joinListWithAnd(immune))

        if len(errors) > 0:
            returnStr += 'Error registering hit on {}.\n'.format(
                self.joinListWithAnd(errors))

        await ctx.send(returnStr)

    # Returns the current leaderboard

    @commands.command(name='Leaderboard', brief='Returns the Top 10 users sorted by snipes')
    async def leaderboard(self, ctx: commands.Context):
        rows = Database.getLeaderboard()
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
    # @commands.has_role(item="Dev Team")
    async def set_carepackage_cmd(self, ctx: commands.Context, keyword, time, hint):
        await ctx.send(CarePackage.set_carepackage(keyword, time, hint))

    @commands.command(name='get_hint', hidden=True)
    # @commands.has_role(item="Dev Team")
    async def get_carepackage_hint(self, ctx: commands.Context):
        await ctx.send(CarePackage.get_hint())

    @commands.command(name='announce_carepackage', hidden=True)
    # @commands.has_role(item="Dev Team")
    async def announce_carepackage(self, ctx: commands.Context):
        channel = ctx.guild.get_channel(566052230256656415)
        await channel.send('{} A carepackage is spawning soon!'.format(ctx.guild.default_role))

    @commands.command(name='guess', hidden=True)
    # @commands.has_role(item="Dev Team")
    async def guess_keyword(self, ctx: commands.Context, keyword):
        success, msg = CarePackage.isKeyword(keyword)

        if not success:
            if msg is not None:
                await ctx.send(msg)
            else:
                await ctx.send('Sorry {}, that is not the keyword.'.format(ctx.author.display_name))

            return

        reward = Database.get_random_reward()
        msg = CarePackage.get_reward(reward[0], ctx.author.id)

        await ctx.send('{} guessed the keyword correctly! You open the care package and earn {}!'.format(ctx.author.display_name, msg))
