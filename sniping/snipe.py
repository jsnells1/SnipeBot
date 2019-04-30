import asyncio
import calendar
import logging
from datetime import datetime

import discord
import discord.ext.commands as commands

import sniping.carepackage as CarePackage
from data import code as Database
from data.code import Environment

from .formatting import SnipingFormatter


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

        guild = self.bot.get_guild(self.indies_guild)

        snipe_channel = self.bot.get_channel(self.snipe_channel)
        test_channel = self.bot.get_channel(self.test_channel)

        while not self.bot.is_closed():
            if Database.DATABASE == Database.DEV_DATABASE:
                channel = test_channel
            else:
                channel = snipe_channel

            respawns = Database.getAllRespawns()
            Database.removeExpiredRevenges()
            explosions = Database.check_exploded_potatoes()
            expirations = Database.get_expired_immunes()

            expirations = [guild.get_member(
                user).display_name for user in expirations]

            if expirations and len(expirations) > 0:
                await channel.send('```It\'s hunting season! Immunity has expired for: {}```'.format(', '.join(expirations)))

            explosions = [guild.get_member(
                user).display_name for user in explosions]

            if explosions and len(explosions) > 0:
                await channel.send('```BOOM! One or more potatoes exploded and the following players lost a life and 3 points: {}```'.format(', '.join(explosions)))

            if Database.remove_expired_carepackage():
                await channel.send('```A carepackage has expired without anyone claiming it. Better luck next time.```')

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
        points = Database.getUserPoints(author.id)

        if isinstance(points, bool) and not points:
            await ctx.send("Error retrieving points...")
            return

        if points is None:
            success = Database.registerUser(ctx.author.id)

            if not success:
                await ctx.send('User was not found and failed to be registered.')
                return
            else:
                points = Database.getUserPoints(author.id)

        await ctx.send("{} you have {} point(s)".format(author.mention, points))

    # region Register Snipes
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

        await ctx.send(self.do_snipe(ctx.author, losers))

    @snipeUser.error
    async def sniperUser_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            error = 'Command failed(Bad Arguments): Please resubmit your snipe\n'
            error += 'Ensure you write the command as !snipe @Target1 @Target2 etc..\n'
            error += 'Be sure not to write any other text like: \n'
            error += '\t!snipe @Justin Got you Justin!\n'
            error += 'This will fail.'

            await ctx.send('```' + error + '```')

    def do_snipe(self, sniper, targets):
        hits = []
        immune = []
        respawns = []
        errors = []
        leaderId = Database.getLeader()
        revengeId = Database.getRevengeUser(sniper.id)
        bonusPoints = 0
        leaderHit = False
        revengeHit = False
        hasPotato = Database.has_potato(sniper.id)

        multiplier = Database.get_multiplier(sniper.id)

        if multiplier is None or not multiplier:
            multiplier = 1

        for i, loser in enumerate(targets):

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
                    Database.pass_potato(sniper.id, loser.id)

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

        killstreak = len(hits)
        if len(hits) > 0:
            killstreak = Database.update_killstreak(sniper.id, len(hits))

        bonusPoints = bonusPoints * multiplier + \
            (len(hits) * multiplier - len(hits))

        Database.addPoints(sniper.id, bonusPoints)

        totalPoints = bonusPoints + len(hits)

        output = SnipingFormatter()
        output.hits = hits
        output.immune = immune
        output.respawns = respawns
        output.errors = errors
        output.author = sniper
        output.hasPotato = hasPotato
        output.leaderHit = leaderHit
        output.revengeHit = revengeHit
        output.potatoName = targets[0].display_name
        output.killstreak = killstreak

        guild = self.bot.get_guild(self.indies_guild)

        output.revengeMember = guild.get_member(revengeId)
        output.totalPoints = totalPoints
        output.multiplier = multiplier

        return output.formatSnipeString()

    @commands.command(name='admin_snipe', hidden=True)
    @commands.has_role(item='Dev Team')
    async def admin_snipe(self, ctx: commands.Context, *members: discord.Member):
        if len(members) <= 1:
            await ctx.send('```Need atleast 2 arguments.```')
            return

        sniper = members[0]

        await ctx.send(self.do_snipe(sniper, members[1:]))
    # endregion

    # Returns the current leaderboard

    @commands.command(name='Leaderboard', brief='Returns the Top 10 users sorted by snipes')
    async def leaderboard(self, ctx: commands.Context):
        rows = Database.getLeaderboard()
        killstreakHiScore = Database.get_highest_killstreak()

        if not rows or not killstreakHiScore:
            await ctx.send('```Error retrieving leaderboard```')
            return

        killstreakHolder = ctx.guild.get_member(killstreakHiScore[0])

        _padding = 3
        _paddingString = ' ' * _padding
        _userColName = 'Name'
        _pointsColName = 'P'
        _snipesColName = 'S'
        _deathsColName = 'D'
        output = ''

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

        output += 'HiScores \n'
        output += '-' * (_padding * 3 + nameColLength +
                         pointsColLength + snipeColLength + deathColLength) + '\n'
        output += 'Longest Streak: {} - {}\n\n'.format(
            killstreakHiScore[1], killstreakHolder.display_name[0:10])

        output += _userColName + _paddingString + \
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

    # region CarePackage Commands
    @commands.command(name='smoke_bomb', hidden=True)
    async def use_smoke_bomb(self, ctx: commands.Context):
        if Database.has_smoke_bomb(ctx.author.id):
            if Database.use_smoke_bomb(ctx.author.id):
                await ctx.send(ctx.author.display_name + ' has used a smoke bomb and is now immune for the next 3 hours!')
            else:
                await ctx.send('Error using smoke bomb.')
        else:
            await ctx.send('You don\'t have a smoke bomb to use!')

    @commands.command(name='set_carepackage', hidden=True)
    @commands.has_role(item="Dev Team")
    async def set_carepackage_cmd(self, ctx: commands.Context, keyword, time, hint):
        await ctx.send(CarePackage.set_carepackage(keyword, time, hint))

    @commands.command(name='get_hint', hidden=True)
    async def get_carepackage_hint(self, ctx: commands.Context):
        await ctx.send(CarePackage.get_hint())

    @commands.command(name='get_rewards', hidden=True)
    @commands.has_role(item="Dev Team")
    async def get_carepackage_rewards(self, ctx: commands.Context):
        rewards = Database.get_rewards()

        sendingStr = ''

        for reward in rewards:
            sendingStr += reward[0] + '\n\t\u2192 ' + reward[1] + '\n'

        await ctx.send('```' + sendingStr + '```')

    @commands.command(name='announce_carepackage', hidden=True)
    @commands.has_role(item="Dev Team")
    async def announce_carepackage(self, ctx: commands.Context):
        channel = ctx.guild.get_channel(self.snipe_channel)
        await channel.send('{} A carepackage is spawning soon!'.format(ctx.guild.default_role))

    @commands.command(name='guess', hidden=True)
    async def guess_keyword(self, ctx: commands.Context, keyword):
        if Database.isRespawning(ctx.author.id):
            await ctx.send('Sorry, you can\'t claim the carepackage if you\'re dead!')
            return

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

    # endregion
