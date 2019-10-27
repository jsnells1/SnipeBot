import logging
from datetime import datetime

import aiosqlite
import discord
import discord.ext.commands as commands

import cogs.utils.db as Database
from cogs.utils.carepackage import Package
from cogs.utils.rewards import Reward
from cogs.utils.sniper import Sniper

log = logging.getLogger(__name__)


class CarePackage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='smoke_bomb', hidden=True)
    async def use_smoke_bomb(self, ctx: commands.Context):
        sniper = await Sniper.from_database(ctx.author.id, ctx.guild.id, ctx.author.display_name)

        if sniper:
            if sniper.smokebomb > 0:
                await sniper.use_smokebomb()
                return await ctx.send(f'{ctx.author.display_name} has used a smoke bomb and is now immune for the next 3 hours!')

        return await ctx.send('You don\'t have a smoke bomb to use!')

    @commands.command(name='set_carepackage', hidden=True)
    @commands.has_role(item="Dev Team")
    async def set_carepackage_cmd(self, ctx: commands.Context, keyword, time, hint=None):
        expiration = datetime.strptime(time, '%m/%d/%y %H:%M')
        carepackage = Package(ctx.guild.id, keyword, expiration.timestamp(), hint)

        try:
            await carepackage.save()
            await ctx.send('Carepackage saved.')
        except:
            await ctx.send('Carepackage failed to be saved.')

    @commands.command(name='get_hint', hidden=True)
    async def get_carepackage_hint(self, ctx: commands.Context):
        carepackages = await Package.get_all(ctx.guild.id)

        if len(carepackages) == 0:
            await ctx.send('There are no active carepackages')
        else:
            formatted = '\n'.join(f'CarePackage {i + 1}. {p.get_hint()}' for i, p in enumerate(carepackages))
            await ctx.send(f'```Current hints:\n\n{formatted}```')

    @commands.command(name='get_rewards')
    async def get_carepackage_rewards(self, ctx: commands.Context):
        rewards = []
        async with aiosqlite.connect(Database.DATABASE) as db:
            async with db.execute('SELECT Name, Description FROM CarePackageRwds') as cursor:
                rewards = await cursor.fetchall()

        sendingStr = ''

        for reward in rewards:
            sendingStr += f'{reward[0]}\n\t\u2192 {reward[1]}\n'

        await ctx.send('```' + sendingStr + '```')

    @commands.command()
    @commands.has_role(item="Dev Team")
    async def announce_carepackage(self, ctx: commands.Context):
        channel = await commands.TextChannelConverter().convert(ctx, 'snipebot')

        if channel:
            role = await commands.RoleConverter().convert(ctx, 'Sniper Team')

            if role:
                await channel.send(f'{role.mention} A carepackage is spawning soon!')
            else:
                await channel.send('This command requires a role "Sniper Team" to use.')
        else:
            await ctx.send('No channel named "SnipeBot" found')

    @commands.command()
    async def guess(self, ctx: commands.Context, keyword):
        guesser = await Sniper.from_database(ctx.author.id, ctx.guild.id, ctx.author.name, register=True)

        if guesser.is_respawning():
            return await ctx.send('Sorry, you can\'t claim the carepackage if you\'re dead!')

        success = await Package.is_keyword(keyword, ctx.guild.id)

        if not success:
            return await ctx.send(f'Sorry {ctx.author.display_name}, that is not the keyword.')

        reward = await Reward.get_random()
        msg = await reward.redeem(ctx.author)

        await ctx.send(f'{ctx.author.display_name} guessed the keyword correctly! You open the care package and earn {msg}!')

    @commands.command(name='give_carepackage', hidden=True)
    @commands.has_role(item='Dev Team')
    async def give_carepackage(self, ctx: commands.Context, member: discord.Member):
        reward = await Reward.get_random()
        msg = await reward.redeem(member)

        await ctx.send(f'{member.display_name} opens the care package and earn {msg}!')
