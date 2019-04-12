from discord import User
from discord import Member
from discord.ext import commands
from discord.ext.commands import Context

import bot_database

class Snipes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='points')
    async def getPoints(self, ctx: Context):
        channel = ctx.message.channel
        author = ctx.message.author

        points = bot_database.getUserPoints(author.id)

        if points is None:

            def check(m):
                return m.content == 'Y' and m.channel == channel and m.author.id == author.id

            await ctx.send("User has not been registered, would you like to register? (Y/N)")
            response = await self.bot.wait_for('message', check=check)

            if response:
                bot_database.registerUser(ctx.author.id)
                await ctx.send("User registered hopefully")

        else:
            await ctx.send("{} you have {} point(s)".format(author.mention, points))

    @commands.command(name='snipe')
    async def snipeUser(self, ctx: Context, winner: Member, loser: Member):
        if bot_database.addSnipe(winner.id, loser.id):
            await ctx.send('SNIPED! {} has sniped {}.'.format(winner.nick, loser.nick))
        else:
            await ctx.send('Snipe failed to register.. Error')


    @commands.command(name='Leaderboard')
    async def leaderboard(self, ctx: Context):
        rows = bot_database.getLeaderboard()
        returnStr = '```Current Leaderboard: \n' + 'Name                Snipes         Deaths\n'

        for row in rows:
            user = await self.bot.fetch_user(row[0])

            spaces = 20 - len(user.display_name)

            returnStr += user.display_name
            for _ in range(spaces):
                returnStr += ' '

            returnStr += str(row[1])

            for _ in range(14):
                returnStr += ' '

            returnStr += str(row[2]) + '\n'

        await ctx.send(returnStr + '```')

