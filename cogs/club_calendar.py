import calendar
from datetime import datetime

import discord
import discord.ext.commands as commands

from data import api as Database


class ClubCalendar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def try_parse_date(self, text):
        formats = ('%m/%d', '%m/%d/%y')

        for fmt in formats:
            try:
                return datetime.strptime(text, fmt)
            except:
                pass

        raise ValueError('no valid date found')

    @commands.command(name='add_event')
    async def add_event(self, ctx: commands.Context, date, description):
        try:
            parsed_date = self.try_parse_date(date)
        except:
            return await ctx.send('```Error: No valid date found```')

        is_repeating = False

        if parsed_date.year == 1900:
            is_repeating = True
            parsed_date = parsed_date.replace(year=datetime.now().year)

        if Database.insert_event(parsed_date.timestamp(), description, is_repeating):
            output = f'```Event added successfully\nDate: {parsed_date.strftime("%m/%d/%y")}\nDescription: {description}\nRepeating: {is_repeating}```'

            await ctx.send(output)
        else:
            await ctx.send('```Error adding event.```')

    @commands.command(name='month_events')
    async def month_events(self, ctx: commands.Context):

        now = datetime.now()
        end_day = calendar.monthrange(now.year, now.month)[1]

        start_date = now.replace(day=1)
        end_date = now.replace(day=end_day)

        events = Database.get_events(
            start_date.timestamp(), end_date.timestamp())

        list_of_events = []

        for event in events:
            parsed_date = datetime.fromtimestamp(event['Date'])
            list_of_events.append([parsed_date, event['Description']])

        month_name = datetime.now().strftime('%B')

        output = f'Events for {month_name}\n\n'

        for event in list_of_events:
            output += event[0].strftime('%b %d') + ' - ' + event[1] + '\n'

        await ctx.send('```' + output + '```')
