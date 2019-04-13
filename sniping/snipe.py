from discord import User, Member, Embed, Guild
from discord.ext import commands
from discord.ext.commands import Context

from data import bot_database


class Snipes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Returns a user's points or snipes

    @commands.command(name='Points', brief='Returns the calling user\'s points (or snipes)', 
        help='Returns the calling user\'s points (or snipes)\nIf the user doesn\'t exists, they will be prompted to register their account')
    async def getPoints(self, ctx: Context):
        channel = ctx.message.channel
        author = ctx.message.author

        points = bot_database.getUserPoints(author.id)

        if not points:
            await ctx.send("Error retrieving points...")

        if points is None:

            def check(m):
                return m.content == 'Y' and m.channel == channel and m.author.id == author.id

            await ctx.send("User has not been registered, would you like to register? (Y/N)")

            try:
                response = await self.bot.wait_for('message', check=check, timeout=20)
            except:
                await ctx.send("Timeout reached. User not registered.")
                return

            if response:
                bot_database.registerUser(ctx.author.id)
                await ctx.send("User registered successfully!")

        else:
            await ctx.send("{} you have {} point(s)".format(author.mention, points))

    # Registers a snipe with snipe bot

    @commands.command(name='Snipe', brief='Registers a snipe from the calling user to the mentioned user', usage='<@TargetUser>',
        help='Registers a snipe from the calling user to the mentioned user.\nBoth the calling and mentioned users will be created if not already.')
    async def snipeUser(self, ctx: Context, loser: Member):
        if bot_database.addSnipe(ctx.author.id, loser.id):
            await ctx.send('SNIPED! {} has sniped {}.'.format(ctx.author.nick, loser.nick))
        else:
            await ctx.send('Snipe failed to register.. Error')

    # Returns the current leaderboard

    @commands.command(name='Leaderboard', brief='Returns the Top 10 users sorted by snipes')
    async def leaderboard(self, ctx: Context):
        rows = bot_database.getLeaderboard()

        names = ''
        snipes = ''
        deaths = ''

        for i, row in enumerate(rows):
            user = ctx.guild.get_member(int(row[0]))

            names += str(i + 1) + '. ' + user.nick + '\n'
            snipes += str(row[1]) + '\n'
            deaths += str(row[2]) + '\n'

        embed = Embed(title='Current Leaderboard (Top 10):', color=0x0000ff)
        embed.set_author(name='Here are the standings...',
                         icon_url='https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Trophy_Flat_Icon.svg/512px-Trophy_Flat_Icon.svg.png')
        embed.add_field(name='Position/Name', value=names, inline=True)
        embed.add_field(name='Snipes', value=snipes, inline=True)
        embed.add_field(name='Deaths', value=deaths)
        await ctx.send('', embed=embed)
