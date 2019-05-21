import asyncio
import calendar
import logging
from datetime import datetime

import discord
import discord.ext.commands as commands
from discord.ext import tasks

import sniping.carepackage as CarePackage
from data import code as Database

from .snipe_logic import do_snipe, get_leaderboard

log = logging.getLogger(__name__)


class Snipes(commands.Cog):
    def __init__(self, bot, day, begin, end):
        self.bot = bot
        self.club_day = day
        self.club_start = begin
        self.club_end = end
        self.test_channel_id = 566076016825597972
        self.test_channel = bot.get_channel(self.test_channel_id)
        self.snipe_channel_id = 568115558206406656
        self.snipe_channel = bot.get_channel(self.snipe_channel_id)
        self.indies_guild_id = 427276681510649866
        self.indies_guild = bot.get_channel(self.indies_guild_id)
        self.maintenance.start()

        with open('whitelist', 'r') as f:
            self.whitelist = [int(line.rstrip('\n')) for line in f]

        log.info('Whitelisted users: {}'.format(self.whitelist))

    @tasks.loop(minutes=1.0)
    async def maintenance(self):
        if Database.DATABASE == Database.DEV_DATABASE:
            channel = self.test_channel
        else:
            channel = self.snipe_channel

        respawns = Database.getAllRespawns()
        Database.removeExpiredRevenges()
        explosions = Database.check_exploded_potatoes()
        expirations = Database.get_expired_immunes()

        expirations = [self.indies_guild.get_member(
            user).display_name for user in expirations]

        if expirations and len(expirations) > 0:
            await channel.send('```It\'s hunting season! Immunity has expired for: {}```'.format(', '.join(expirations)))

        explosions = [self.indies_guild.get_member(
            user).display_name for user in explosions]

        if explosions and len(explosions) > 0:
            await channel.send('```BOOM! One or more potatoes exploded and the following players lost a life and 3 points: {}```'.format(', '.join(explosions)))

        if Database.remove_expired_carepackage():
            await channel.send('```A carepackage has expired without anyone claiming it. Better luck next time.```')

        if len(respawns) > 0:
            users = []
            for user in respawns:
                users.append(self.indies_guild.get_member(int(user)).nick)

            await channel.send('```The following user(s) have respawned: {}```'.format(', '.join(users)))

    @maintenance.before_loop
    async def before_maintenance(self):
        await self.bot.wait_until_ready()

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

        if ctx.message.channel.id != self.snipe_channel_id and ctx.message.channel.id != self.test_channel_id:
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

        for loser in losers:
            if loser.id in self.whitelist:
                member = ctx.guild.get_member(loser.id)
                await ctx.send('```{} has respectfully asked to be on the sniping whitelist. Please refrain from sniping them. Resubmit your snipe without that user.```'.format(member.display_name))
                return

        await ctx.message.add_reaction('🇫')

        await ctx.send(do_snipe(ctx, ctx.author, losers))

    @snipeUser.error
    async def sniperUser_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            error = 'Command failed(Bad Arguments): Please resubmit your snipe\n'
            error += 'Ensure you write the command as !snipe @Target1 @Target2 etc..\n'
            error += 'Be sure not to write any other text like: \n'
            error += '\t!snipe @Justin Got you Justin!\n'
            error += 'This will fail.'

            await ctx.send('```' + error + '```')

    @commands.command(name='admin_snipe', hidden=True)
    @commands.has_role(item='Dev Team')
    async def admin_snipe(self, ctx: commands.Context, *members: discord.Member):
        if len(members) <= 1:
            await ctx.send('```Need atleast 2 arguments.```')
            return

        sniper = members[0]

        await ctx.send(do_snipe(ctx, sniper, members[1:]))
    # endregion

    # Returns the current Leaderboard
    @commands.command(name='Leaderboard', brief='Returns the Top 10 users sorted by snipes')
    async def leaderboard(self, ctx: commands.Context):
        rows = Database.getLeaderboard()
        killstreakHiScore = Database.get_highest_killstreak()

        if not rows or not killstreakHiScore:
            await ctx.send('```Error retrieving leaderboard```')
            return

        killstreakHolder = ctx.guild.get_member(killstreakHiScore[0])

        output = get_leaderboard(
            rows, ctx.guild, killstreakHolder, killstreakHiScore)

        await ctx.send('```' + output + '```')

    # Adds are removes the user from the whitelist
    @commands.command(name='sbwhitelist')
    async def toggle_whitelist(self, ctx: commands.Context):
        user = ctx.author.id

        if user in self.whitelist:
            self.whitelist.remove(user)
            await ctx.send('```You\'ve been removed from the whitelist```')
        else:
            self.whitelist.append(user)
            await ctx.send('```You\'ve been added to the whitelist```')

        with open('whitelist', 'w') as f:
            for i in self.whitelist:
                f.write(str(i) + '\n')

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
        await self.snipe_channel.send('{} A carepackage is spawning soon!'.format(ctx.guild.default_role))

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

    @commands.command(name='give_carepackage', hidden=True)
    @commands.has_role(item='Dev Team')
    async def give_carepackage(self, ctx: commands.Context, member):

        reward = Database.get_random_reward()
        msg = CarePackage.get_reward(reward[0], ctx.author.id)

        await ctx.send('{} opens the care package and earn {}!'.format(member.display_name, msg))

    # endregion
