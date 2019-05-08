from datetime import datetime

import discord
import discord.ext.commands as commands


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
            await ctx.send('```Error: No valid date found```')
            return             
            
        await ctx.send('Date found: %s' % parsed_date)
