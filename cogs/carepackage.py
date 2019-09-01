import logging
from datetime import datetime

import discord.ext.commands as commands

import cogs.utils.rewards as Rewards
from cogs.utils.carepackage import Package
from cogs.utils.sniper import Sniper
from data import api as Database

log = logging.getLogger(__name__)


class CarePackage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        rewards = Database.get_rewards()

        sendingStr = ''

        for reward in rewards:
            sendingStr += reward[0] + '\n\t\u2192 ' + reward[1] + '\n'

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

        reward = Database.get_random_reward()
        msg = Rewards.get_reward(reward[0], ctx.author)

        await ctx.send(f'{ctx.author.display_name} guessed the keyword correctly! You open the care package and earn {msg}!')

    @commands.command(name='give_carepackage', hidden=True)
    @commands.has_role(item='Dev Team')
    async def give_carepackage(self, ctx: commands.Context, member):

        reward = Database.get_random_reward()
        msg = Rewards.get_reward(reward[0], ctx.author)

        await ctx.send(f'{member.display_name} opens the care package and earn {msg}!')
