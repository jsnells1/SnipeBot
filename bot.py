import logging
import traceback

import discord
import discord.ext.commands as commands

from cogs.admin import Admin
from cogs.carepackage import CarePackage
from cogs.club_calendar import ClubCalendar
from cogs.snipe import Snipes
from cogs.soapbox import Soapbox
from data import api

log = logging.getLogger(__name__)
BOT_PREFIX = '!'


class SnipeBot(commands.Bot):
    def __init__(self, day, start, end):
        super().__init__(command_prefix=BOT_PREFIX, case_insensitive=True,
                         activity=discord.Activity(type=discord.ActivityType.listening, name='Logan\'s SI Session'))

        self.add_cog(Soapbox(self))
        self.add_cog(Snipes(self, day, start, end))
        self.add_cog(Admin(self))
        self.add_cog(ClubCalendar(self))
        self.add_cog(CarePackage(self))

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return

        log.info("Error caused by message: `{}`".format(ctx.message.content))
        log.info(''.join(traceback.format_exception_only(type(error), error)))

        if isinstance(error, (commands.MissingPermissions, commands.CheckFailure)):
            return await ctx.send('```You don\'t have permissions to use that command.```')
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(f'BadArgument: {error}')
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f'MissingRequiredArgument: {error}')

    async def on_ready(self):
        log.info('Bot started: Database: ' + api.DATABASE)
        print('Ready. Database: ' + api.DATABASE)
