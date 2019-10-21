import calendar
import collections
import logging
from datetime import datetime

import discord
import discord.ext.commands as commands
from discord import utils
from discord.ext import tasks

import cogs.utils.db as Database
from cogs.utils.carepackage import Package
from cogs.utils.leaderboard import Leaderboard
from cogs.utils.sniper import Sniper

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

        log.info(f'Whitelisted users: {self.whitelist}')

    @tasks.loop(minutes=1.0)
    async def maintenance(self):
        if Database.DATABASE == Database.DEV_DATABASE:
            channel_name = 'snipebot-testing'
        else:
            channel_name = 'snipebot'

        # Silently remove revenge targets that have expired
        await Sniper.remove_expired_revenges()

        # Get the list of respawns, spud explosions, immunity expiration, and carepackage expirations
        respawns = await Sniper.get_respawns
        explosions = await Sniper.get_exploded_potatoes()
        expirations = await Sniper.get_expired_immunes()
        expired_carepackages = await Package.remove_expired()

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

    # region Register Snipes
    @commands.command(brief='Registers a snipe on all mentioned users', usage='@TargetUser @TargetUser',
                      help='Registers a snipe from the calling user to the mentioned user.\nBoth the calling and mentioned users will be created if not already.')
    async def snipe(self, ctx: commands.Context):

        targets = ctx.message.mentions

        if 'snipebot' not in ctx.channel.name:
            return await ctx.send('Please use the snipebot channel for sniping :)')

        if ctx.author.id in self.whitelist:
            return await ctx.send('You cannot snipe while on the whitelist.')

        today = datetime.now()

        if today.weekday() == self.club_day and today.hour >= self.club_start and today.hour < self.club_end:
            return await ctx.send(f'Sniping disabled during club hours: {calendar.day_name[self.club_day]} from {self.club_start}:00 to {self.club_end}:00 (Military Time)')

        if len(targets) == 0:
            return await ctx.send('To snipe a user, type !snipe <@Target>. You can snipe multiple users by typing !snipe <@Target1> <@Target2> etc..')

        if any(x.id == ctx.author.id for x in targets):
            return await ctx.send('Sorry, you cannot snipe yourself...')

        for target in targets:
            if target.id in self.whitelist:
                member = ctx.guild.get_member(target.id)
                return await ctx.send(f'{member.display_name} has respectfully asked to be on the sniping whitelist. Please refrain from sniping them. Snipe cancelled.')

        # Add 'F' emoji to the snipe
        await ctx.message.add_reaction('\U0001f1eb')

        sniper = await Sniper.from_database(ctx.author.id, ctx.guild.id, ctx.author.display_name, register=True)

        await ctx.send(await sniper.snipe(ctx, targets))

    @commands.command(hidden=True)
    @commands.has_role(item='Dev Team')
    async def admin_snipe(self, ctx: commands.Context, sniper: discord.Member, *targets: discord.Member):
        if len(targets) == 0:
            return await ctx.send('Missing atleast 1 target')

        sniper = await Sniper.from_database(sniper.id, ctx.guild.id, sniper.display_name, register=True)

        await ctx.send(await sniper.snipe(ctx, targets))
    # endregion

    # Returns the current Leaderboard
    @commands.command(brief='Returns the Top 10 users sorted by snipes')
    async def leaderboard(self, ctx: commands.Context):
        output = await Leaderboard(ctx).get_leaderboard()
        await ctx.send(f'```{output}```')

    # Adds are removes the user from the whitelist
    @commands.command(name='sbwhitelist', brief='Toggles the user\'s presence on the sniping whitelist',
                      help='When on the whitelist, you cannot snipe or be sniped')
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
                f.write(f'{i}\n')

    @commands.command(name='getwhitelist', brief='Lists all users currently on the whitelist')
    async def get_whitelist(self, ctx: commands.Context):
        users = [user.display_name for user in (ctx.guild.get_member(id) for id in self.whitelist) if user is not None]

        await ctx.send(f"Whitelisted users: {', '.join(users)}")
