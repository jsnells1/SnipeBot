import collections
import asyncio
import calendar
import logging
from datetime import datetime

import discord
import discord.ext.commands as commands
from discord.ext import tasks
from discord import utils

import cogs.utils.carepackage as CarePackage
import cogs.utils.rewards as Rewards
from data import api as Database

from cogs.utils.snipe_logic import do_snipe, get_leaderboard

from cogs.utils.leaderboard import Leaderboard

log = logging.getLogger(__name__)


class Snipes(commands.Cog):
    def __init__(self, bot, day, begin, end):
        self.bot = bot
        self.club_day = day
        self.club_start = begin
        self.club_end = end
        self.maintenance.start()

        with open('whitelist', 'r') as f:
            self.whitelist = [int(line.rstrip('\n')) for line in f]

        log.info('Whitelisted users: {}'.format(self.whitelist))

    @tasks.loop(minutes=1.0)
    async def maintenance(self):
        if Database.DATABASE == Database.DEV_DATABASE:
            channel_name = 'snipebot-testing'
        else:
            channel_name = 'snipebot'

        # Silently remove revenge targets that have expired
        Database.remove_expired_revenges()

        # Get the list of respawns, spud explosions, immunity expiration, and carepackage expirations
        respawns = await Database.get_all_respawns()
        explosions = await Database.check_exploded_potatoes()
        expirations = await Database.get_expired_immunes()
        expired_carepackages = await Database.remove_expired_carepackage()

        # Dictionary of guild_id, messages_to_send pairs
        message_dict = collections.defaultdict(list)

        for guild_id, user_id in expirations:
            guild = self.bot.get_guild(guild_id)

            if guild:
                member = guild.get_member(user_id)

                if member:
                    message_dict[guild_id].append(f'Immunity has expired for {member.display_name}')

        for guild_id, user_id in explosions:
            guild = self.bot.get_guild(guild_id)

            if guild:
                member = guild.get_member(user_id)

                if member:
                    message_dict[guild_id].append(f'BOOM! A potatoe exploded and {member.display_name} lost a life and 3 points')

        for guild_id, key in expired_carepackages:
            message_dict[guild_id].append(f'A carepackage has expired without anyone claiming it. The key was: {key}')

        respawns_dict = collections.defaultdict(list)

        for guild_id, user_id in respawns:
            guild = self.bot.get_guild(guild_id)

            if guild:
                member = guild.get_member(user_id)

                if member:
                    respawns_dict[guild_id].append(member.display_name)

        for guild_id, user_list in respawns_dict.items():
            message_dict[guild_id].append(f"The following user(s) have respawned: {', '.join(user_list)}")

        for guild_id, message_list in message_dict.items():
            guild = self.bot.get_guild(guild_id)

            if guild:
                channel = utils.get(guild.channels, name=channel_name)

                if channel:
                    await channel.send('\n'.join(message_list))

    @maintenance.before_loop
    async def before_maintenance(self):
        await self.bot.wait_until_ready()

    # Returns a user's points or snipes

    @commands.command(brief='Returns the calling user\'s points (or snipes)',
                      help='Returns the calling user\'s points (or snipes)\nIf the user doesn\'t exists, they will be prompted to register their account')
    async def points(self, ctx: commands.Context):
        points = await Database.get_points(ctx.author.id)

        if not points:
            await ctx.send('You have not yet been registered. Snipe or get sniped to be registered.')
        else:
            await ctx.send(f'{ctx.author.mention} you have {points} point(s)')

    # region Register Snipes
    @commands.command(brief='Registers a snipe from the calling user to the mentioned user', usage='@TargetUser @TargetUser',
                      help='Registers a snipe from the calling user to the mentioned user.\nBoth the calling and mentioned users will be created if not already.')
    async def snipe(self, ctx: commands.Context):

        targets = ctx.message.mentions

        if 'snipebot' not in ctx.channel.name:
            return await ctx.send('Please use the snipebot channel for sniping :)')

        today = datetime.now()

        if today.weekday() == self.club_day and today.hour >= self.club_start and today.hour < self.club_end:
            return await ctx.send('```Sniping disabled during club hours: {} from {}:00 to {}:00 (Military Time)```'.format(calendar.day_name[self.club_day], self.club_start, self.club_end))

        if len(targets) == 0:
            return await ctx.send('To snipe a user, type !snipe <@Target>. You can snipe multiple users by typing !snipe <@Target1> <@Target2> etc..')

        if any(x.id == ctx.author.id for x in targets):
            return await ctx.send('Sorry, you cannot snipe yourself...')

        for target in targets:
            if target.id in self.whitelist:
                member = ctx.guild.get_member(target.id)
                return await ctx.send('```{} has respectfully asked to be on the sniping whitelist. Please refrain from sniping them. Resubmit your snipe without that user.```'.format(member.display_name))

        # Add 'F' emoji to the snipe
        await ctx.message.add_reaction('\U0001f1eb')

        await ctx.send(await do_snipe(ctx, ctx.author, targets))

    @commands.command(hidden=True)
    @commands.has_role(item='Dev Team')
    async def admin_snipe(self, ctx: commands.Context, sniper: discord.Member, *targets: discord.Member):
        if len(targets) == 0:
            return await ctx.send('Missing atleast 1 target')

        await ctx.send(await do_snipe(ctx, sniper, targets))
    # endregion

    # Returns the current Leaderboard
    @commands.command(brief='Returns the Top 10 users sorted by snipes')
    async def leaderboard(self, ctx: commands.Context):
        output = await Leaderboard(ctx).get_leaderboard()
        await ctx.send(f'```{output}```')

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
