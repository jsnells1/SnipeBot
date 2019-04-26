from datetime import datetime

import discord
import discord.ext.commands as commands

from data import code as Database
from data.code import Environment


class Soapbox(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='soapbox_schedule', brief="Returns the current soapbox schedule")
    async def getSchedule(self, ctx: commands.Context):
        response = Database.getSoapboxSchedule()

        if not response:
            await ctx.send('Error retrieving Soapbox Schedule.')

        _padding = 2
        _paddingString = ' ' * _padding
        _idColName = 'ID'
        _nameColName = 'Name'
        _dateColName = 'Date'
        _topicColName = 'Topic'

        idColLength = len(_idColName)
        nameColLength = len(_nameColName)
        dateColLength = len(_dateColName)
        topicColLength = len(_topicColName)

        for row in response:
            idColLength = max(idColLength, len(str(row[0])))
            nameColLength = max(nameColLength, len(row[1]))

            date = datetime.fromtimestamp(row[2]).strftime('%b. %d')

            dateColLength = max(dateColLength, len(date))
            topicColLength = max(topicColLength, len(row[3]))

        returnStr = _idColName + \
            (idColLength - len(_idColName)) * ' ' + _paddingString
        returnStr += _nameColName + \
            (nameColLength - len(_nameColName)) * ' ' + _paddingString
        returnStr += _dateColName + \
            (dateColLength - len(_dateColName)) * ' ' + _paddingString
        returnStr += _topicColName + '\n'
        returnStr += '-' * (idColLength + nameColLength +
                            dateColLength + topicColLength + (3*_padding)) + '\n'

        for row in response:
            returnStr += str(row[0]) + _paddingString + \
                (idColLength - len(str(row[0]))) * ' '
            returnStr += row[1] + _paddingString + \
                (nameColLength - len(str(row[1]))) * ' '

            date = datetime.fromtimestamp(row[2]).strftime('%b. %d')

            returnStr += (date or '-') + _paddingString + \
                (dateColLength - len(date)) * ' '
            returnStr += (row[3] or '-') + _paddingString + \
                (topicColLength - len(str(row[3]))) * ' ' + '\n'

        await ctx.send('```' + returnStr + '```')

    @commands.command(name='new_soapbox', usage='"Name" "Date" "Topic"', brief='(Admin-Only) Creates a new soapbox entry in the schedule',
                      help='To create a new entry type:\n!new_soapbox "Name" "Date (Ex. 4/11)" "Topic"\n Quotes are mandatory and all 3 fields are required')
    @commands.has_permissions(ban_members=True)
    async def newSoapbox(self, ctx: commands.Context, *args):

        if len(args) != 3:
            errMsg = '```Error: Incompatible arguments\nThis command requires 3 arguments. The format is:\n\t"Name" "Date (Month/Day)" "Topic" \nExample:\n\t"Justin S." "4/11" "Video Games"```'
            await ctx.send(errMsg)
            return

        name = args[0]
        topic = args[2]

        try:
            date = datetime.strptime(
                args[1], '%m/%d').replace(year=datetime.now().year).timestamp()
        except ValueError:
            await ctx.send('```Cannot create soapbox: Date should be in the format of Month/Day\nExample:\n\t4/11```')
            return

        response = Database.createSoapbox(name, date, topic)

        if response:
            await ctx.send('Soapbox created!')
        else:
            await ctx.send('Error creating soapbox.')

    @commands.command(name='delete_soapbox_entry', brief='(Admin-Only) Deletes a soapbox entry', usage='id',
                      help="Deletes the entry specified with the id argument")
    @commands.has_permissions(ban_members=True)
    async def deleteEntry(self, ctx: commands.Context, id):
        info, row = Database.getSoapboxEntry(id)

        if row is None or not row:
            await ctx.send('```Could not find entry with id {}```'.format(id))
            return

        author = ctx.message.author
        channel = ctx.message.channel

        returnStr = '```Found entry:\n'

        for key, column in zip(info, row):
            returnStr += ' ' + key + ': ' + str(column) + '\n'

        returnStr += '```'
        await ctx.send(returnStr + '\n' + 'Are you sure you want to delete this record? (Y/N)')

        def check(m):
            return (m.content == 'Y' or m.content == 'N' or m.content == 'n' or m.content == 'y') and m.channel == channel and m.author.id == author.id

        try:
            response = await self.bot.wait_for('message', check=check, timeout=10)
        except:
            await ctx.send("Timeout reached. Operation aborted")
            return

        if response.content == 'Y' or response.content == 'y':
            success = Database.deleteSoapboxEntry(row[0])

            if success:
                await ctx.send('```Record deleted.```')
            else:
                await ctx.send('```Record failed to be deleted.```')

        else:
            await ctx.send('Operation aborted.')

    @commands.command(name='update_soapbox_entry', usage='id "Name" "Date" "Topic"', brief='(Admin-Only) Updates a soapbox entry',
                      help='Updates the specified entry given the row id. The entry is updated using the supplied Name, Date, and Topic')
    @commands.has_permissions(ban_members=True)
    async def updateEntry(self, ctx: commands.Context, id=None, *args):

        try:
            id = int(id)
        except:
            await ctx.send('```ID should be an integer.```')
            return

        author = ctx.message.author
        channel = ctx.message.channel

        if id is None or len(args) != 3 or not isinstance(id, int):
            errMsg = '```Error: Incompatible arguments\nThis command requires 4 arguments. The format is:\n\tid "Name" "Date (Month/Day)" "Topic"\nExample:\n\t1 "Justin S." "4/11" "Video Games"```'
            await ctx.send(errMsg)
            return

        try:
            date = datetime.strptime(
                args[1], '%m/%d').replace(year=datetime.now().year).timestamp()
        except ValueError:
            await ctx.send('```Cannot update soapbox: Date should be in the format of Month/Day\nExample:\n\t4/11```')
            return

        info, row = Database.getSoapboxEntry(id)

        if row is None or not row:
            await ctx.send('```Could not find entry with id {}```'.format(id))
            return

        userInput = list(args)
        userInput.insert(0, id)

        returnStr = '```Found entry:\n'
        updateStr = 'Updated entry:\n'

        for i, (key, column) in enumerate(zip(info, row)):
            returnStr += ' ' + key + ': ' + str(column) + '\n'
            updateStr += ' ' + key + ': ' + str(userInput[i]) + '\n'

        updateStr += '```'
        await ctx.send(returnStr + '\n' + updateStr + '\n' + 'Are you sure you want to update this record? (Y/N)')

        def check(m):
            return (m.content == 'Y' or m.content == 'N' or m.content == 'n' or m.content == 'y') and m.channel == channel and m.author.id == author.id

        try:
            response = await self.bot.wait_for('message', check=check, timeout=10)
        except:
            await ctx.send("Timeout reached. Operation aborted")
            return

        if response.content == 'Y' or response.content == 'y':
            success = Database.updateSoapboxTopic(
                userInput[0], userInput[1], date, userInput[3])

            if success:
                await ctx.send('```Record Updated.```')
            else:
                await ctx.send('```Record failed to be updated.```')

        else:
            await ctx.send('Operation aborted.')
