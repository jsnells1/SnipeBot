import discord
import discord.ext.commands as commands


class ClubCalendar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='add_event')
    async def add_event(self, ctx: commands.Context):
        return
