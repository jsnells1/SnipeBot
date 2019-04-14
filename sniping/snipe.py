from discord import User, Member, Embed, Guild
from discord.ext.commands import Context, Cog, command

from data.bot_database import BotDatabase


class Snipes(Cog):
    def __init__(self, bot):
        self.bot = bot

    # Returns a user's points or snipes

    @command(name='Points', brief='Returns the calling user\'s points (or snipes)',
             help='Returns the calling user\'s points (or snipes)\nIf the user doesn\'t exists, they will be prompted to register their account')
    async def getPoints(self, ctx: Context):
        channel = ctx.message.channel
        author = ctx.message.author

        points = BotDatabase().getUserPoints(author.id)

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
                BotDatabase().registerUser(ctx.author.id)
                await ctx.send("User registered successfully!")

        else:
            await ctx.send("{} you have {} point(s)".format(author.mention, points))

    # Registers a snipe with snipe bot

    @command(name='Snipe', brief='Registers a snipe from the calling user to the mentioned user', usage='<@TargetUser>',
             help='Registers a snipe from the calling user to the mentioned user.\nBoth the calling and mentioned users will be created if not already.')
    async def snipeUser(self, ctx: Context, *losers: Member):

        if len(losers) == 0:
            await ctx.send('To snipe a user, type !snipe <@Target>. You can snipe multiple users by typing !snipe <@Target1> <@Target2> etc..')
            return

        hits = []
        errors = []

        for loser in losers:

            if BotDatabase().addSnipe(ctx.author.id, loser.id):
                hits.append(loser.nick)
            else:
                errors.append(loser.nick)
                await ctx.send('Snipe failed to register.. Error')

        returnStr = ''

        if len(hits) == 1:
            returnStr = 'SNIPED! {} has sniped {}! '.format(
                ctx.author.nick, hits[0])
        elif len(hits) > 1:
            returnStr = 'SNIPED! {} has sniped {}! '.format(
                ctx.author.nick, ', '.join(hits[:-1]) + ' and ' + hits[-1])

        if len(errors) == 1:
            returnStr += 'Error registering hit on {}.'.format(errors[0])
        elif len(errors) > 1:
            returnStr += 'Error registering hit on {}.'.format(
                ', '.join(errors[:-1]) + ' and ' + errors[-1])

        await ctx.send(returnStr)

    # Returns the current leaderboard

    @command(name='Leaderboard', brief='Returns the Top 10 users sorted by snipes')
    async def leaderboard(self, ctx: Context):
        rows = BotDatabase().getLeaderboard()

        if not rows:
            await ctx.send('```Error retrieving leaderboard```')
            return

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
