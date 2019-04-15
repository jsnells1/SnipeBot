from discord import User, Member, Embed, Guild
from discord.ext.commands import Context, Cog, command, has_permissions

from data import code
from data.code import Environment


class Snipes(Cog):
    def __init__(self, bot):
        self.bot = bot

    # Returns a user's points or snipes

    @command(name='Points', brief='Returns the calling user\'s points (or snipes)',
             help='Returns the calling user\'s points (or snipes)\nIf the user doesn\'t exists, they will be prompted to register their account')
    async def getPoints(self, ctx: Context):
        author = ctx.message.author
        points = code.getUserPoints(author.id)
        
        if not points:
            await ctx.send("Error retrieving points...")

        if points is None:
            success = code.registerUser(ctx.author.id)

            if not success:
                await ctx.send('User was not found and failed to be registered.')
                return
            else:
                points = code.getUserPoints(author.id)

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

            if code.addSnipe(ctx.author.id, loser.id):
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
        rows = code.getLeaderboard()
        if not rows:
            await ctx.send('```Error retrieving leaderboard```')
            return

        _padding = 3
        _paddingString = ' ' * _padding
        _userColName = 'Name'
        _snipesColName = 'S'
        _deathsColName = 'D'

        nameColLength = len(_userColName)
        snipeColLength = len(_snipesColName)
        deathColLength = len(_deathsColName)

        for i, row in enumerate(rows):
            user = ctx.guild.get_member(int(row[0]))

            nameColLength = max(nameColLength, len(
                str(i + 1) + '. ' + user.nick[0:10]))

            snipeColLength = max(snipeColLength, len(str(row[1])))
            deathColLength = max(deathColLength, len(str(row[2])))

        output = _userColName + _paddingString + \
            ((nameColLength - len(_userColName)) * ' ')
        output += _snipesColName + _paddingString + \
            ((snipeColLength - len(_snipesColName)) * ' ')
        output += _deathsColName + _paddingString + \
            ((deathColLength - len(_deathsColName)) * ' ') + '\n'
        output += '-' * (_padding * 2 + nameColLength +
                         snipeColLength + deathColLength) + '\n'

        for i, row in enumerate(rows):
            user = ctx.guild.get_member(int(row[0]))

            name = str(i + 1) + '. ' + user.nick[0:10]

            output += name + _paddingString + \
                ((nameColLength - len(name)) * ' ')
            output += str(row[1]) + _paddingString + \
                ((snipeColLength - len(str(row[1]))) * ' ')
            output += str(row[2]) + _paddingString + \
                ((deathColLength - len(str(row[2]))) * ' ') + '\n'

        await ctx.send('```' + output + '```')
