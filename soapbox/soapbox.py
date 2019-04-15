from discord import Embed
from discord.ext.commands import Cog, Context, command, has_permissions
from datetime import datetime

from data.code.bot_database import BotDatabase


class Soapbox(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='soapbox_schedule', brief="Returns the current soapbox schedule")
    async def getSchedule(self, ctx: Context):
        response = BotDatabase().getSoapboxSchedule()

        if not response:
            await ctx.send('Error retrieving Soapbox Schedule.')

        names = ''
        dates = ''
        topics = ''

        for row in response:
            date = datetime.fromtimestamp(row[2]).strftime('%b. %d')
            names += str(row[0]) + ' - ' + row[1] + '\n'
            dates += (date or '-') + '\n'
            topics += (row[3] or '-') + '\n'

        embed = Embed(
            description='Below is the current Soapbox Schedule for club. Admins, use the Row IDs for managing the schedule.', color=0x00ff00)
        embed.set_author(name='Soapbox Schedule',
                         icon_url='https://cdn.discordapp.com/icons/427276681510649866/d58764b8910cbbaeb78f2a327f014a54.png')
        embed.add_field(name='Row ID - Name', value=names, inline=True)
        embed.add_field(name='Date', value=dates, inline=True)
        embed.add_field(name='Topic', value=topics)

        await ctx.send('', embed=embed)

    @command(name='new_soapbox', usage='"Name" "Date" "Topic"', brief='(Admin-Only) Creates a new soapbox entry in the schedule',
             help='To create a new entry type:\n!new_soapbox "Name" "Date (Ex. 4/11)" "Topic"\n Quotes are mandatory and all 3 fields are required')
    @has_permissions(ban_members=True)
    async def newSoapbox(self, ctx: Context, *args):

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

        response = BotDatabase().createSoapbox(name, date, topic)

        if response:
            await ctx.send('Soapbox created!')
        else:
            await ctx.send('Error creating soapbox.')

    @command(name='delete_soapbox_entry', brief='(Admin-Only) Deletes a soapbox entry', usage='id',
             help="Deletes the entry specified with the id argument")
    @has_permissions(ban_members=True)
    async def deleteEntry(self, ctx: Context, id):
        info, row = BotDatabase().getSoapboxEntry(id)

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
            success = BotDatabase().deleteSoapboxEntry(row[0])

            if success:
                await ctx.send('```Record deleted.```')
            else:
                await ctx.send('```Record failed to be deleted.```')

        else:
            await ctx.send('Operation aborted.')

    @command(name='update_soapbox_entry', usage='id "Name" "Date" "Topic"', brief='(Admin-Only) Updates a soapbox entry',
             help='Updates the specified entry given the row id. The entry is updated using the supplied Name, Date, and Topic')
    @has_permissions(ban_members=True)
    async def updateEntry(self, ctx: Context, id=None, *args):

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

        info, row = BotDatabase().getSoapboxEntry(id)

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
            success = BotDatabase().updateSoapboxTopic(
                userInput[0], userInput[1], date, userInput[3])

            if success:
                await ctx.send('```Record Updated.```')
            else:
                await ctx.send('```Record failed to be updated.```')

        else:
            await ctx.send('Operation aborted.')
