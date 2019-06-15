import asyncio
from datetime import datetime

import discord
import discord.ext.commands as commands
from tabulate import tabulate

from cogs.utils.soapbox import SoapboxEntry
from data import api as Database
from data.api import Environment

# TODO Fix help info


class Soapbox(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def soapbox(self, ctx):
        subcommands = ctx.command.commands

        general_commands = [
            f'{cmd.name} - {cmd.brief}' for cmd in subcommands if len(cmd.checks) == 0]

        admin_commands = [
            f'{cmd.name} - {cmd.brief}' for cmd in subcommands if len(cmd.checks) > 0]

        embed = discord.Embed(title='List of Subcommands',
                              description='To use these commands, do:\n!soapbox subcommand', color=discord.Color.dark_blue())

        embed.set_author(name='SnipeBot', icon_url=self.bot.user.avatar_url)

        embed.add_field(name='**General Use**',
                        value='\n'.join(general_commands), inline=False)

        embed.add_field(name='**Admin Use**',
                        value='\n'.join(admin_commands), inline=False)

        await ctx.send(embed=embed)

    @soapbox.command(name='schedule', brief="Returns the current soapbox schedule")
    async def soapbox_schedule(self, ctx: commands.Context):

        entries = await SoapboxEntry.get_all()
        table_rows = [['ID', 'Name', 'Date', 'Topic']]

        for entry in entries:
            date = entry.date.strftime('%b. %d')

            table_rows.append([entry.id, entry.name, date, entry.topic])

        output = tabulate(table_rows, headers='firstrow',
                          tablefmt='fancy_grid', colalign=('left',))

        await ctx.send(f'```{output}```')

    @soapbox.command(name='new', usage='"Name" "Date" "Topic"', brief='(Admin-Only) Creates a new soapbox entry in the schedule',
                     help='To create a new entry type:\n!new_soapbox "Name" "Date (Ex. 4/11)" "Topic"\n Quotes are mandatory and all 3 fields are required')
    @commands.has_role("Dev Team")
    async def soapbox_new(self, ctx: commands.Context, name=None, date=None, topic='TBD'):

        if name is None or date is None:
            errMsg = '```Error: This command has 2 required arguments and 1 optional argument. The format is:\n\t"Name" "Date (Month/Day)" "Topic" \nExample:\n\t"Justin S." "4/11" "Video Games"```'
            return await ctx.send(errMsg)

        try:
            parsed_date = datetime.strptime(
                date, '%m/%d').replace(year=datetime.now().year)
        except ValueError:
            return await ctx.send('```Cannot create soapbox: Date should be in the format of Month/Day\nExample:\n\t4/11```')

        new_soapbox = SoapboxEntry(name=name, date=parsed_date, topic=topic)
        await new_soapbox.commit_new()

        await ctx.send('Soapbox created!')

    @soapbox.command(name='delete', aliases=['del'], brief='(Admin-Only) Deletes a soapbox entry', usage='id',
                     help="Deletes the entry specified with the id argument")
    @commands.has_role("Dev Team")
    async def soapbox_delete(self, ctx: commands.Context, id: int):

        soapbox_entry = await SoapboxEntry.from_database(id)

        await ctx.send(f'```{soapbox_entry}```\nAre you sure you want to delete this record? (Y/N)')

        def check(m):
            return m.content in ('Y', 'y', 'N', 'n') and m.channel == ctx.channel and m.author == ctx.author

        try:
            response = await self.bot.wait_for('message', check=check, timeout=10)
        except asyncio.TimeoutError:
            return await ctx.send("Timeout reached. Operation aborted")

        if response.lower() == 'y':
            await soapbox_entry.commit_delete()
            await ctx.send('Record deleted \U0001F44D')
        else:
            await ctx.send('Cancelled.')

    @soapbox.command(name='update', usage='id "Name" "Date" "Topic"', brief='(Admin-Only) Updates a soapbox entry',
                     help='Updates the specified entry given the row id. The entry is updated using the supplied Name, Date, and Topic')
    @commands.has_role("Dev Team")
    async def soapbox_update(self, ctx: commands.Context, id: int, *args):

        try:
            soapbox_to_update = await SoapboxEntry.from_database(id)
        except LookupError as e:
            return await ctx.send(e)

        updates = {
            'name': None,
            'date': None,
            'topic': None
        }

        field = None
        for arg in args:
            if arg.startswith('-'):
                field = arg[1:].lower()
            elif field is not None:
                updates[field] = arg
                field = None

        updates['id'] = id

        try:
            if updates['date'] is not None:
                updates['date'] = datetime.strptime(
                    updates['date'], '%m/%d').replace(year=datetime.now().year)
        except ValueError:
            return await ctx.send('```Date Conversion Error: Date should be in the format of Month/Day\nExample:\n\t4/11```')

        new_soapbox_entry = SoapboxEntry.from_dict(updates)
        soapbox_to_update.update(new_soapbox_entry)

        await ctx.send(f'```Updated Soapbox:\n\n{soapbox_to_update}```\nAre you sure you want to save these changes? (Y/N)')

        def check(m):
            return m.content in ('Y', 'y', 'N', 'n') and m.channel == ctx.channel and m.author == ctx.author

        try:
            response = await self.bot.wait_for('message', check=check, timeout=10)
        except:
            await ctx.send("Timeout reached. Operation aborted")
            return

        if response.content == 'Y' or response.content == 'y':
            await soapbox_to_update.commit_update()
            await ctx.send('Record Updated \U0001F44D')
        else:
            await ctx.send('Operation cancelled.')
