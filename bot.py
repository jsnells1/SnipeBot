import logging
import traceback

import discord
import discord.ext.commands as commands

from cogs.admin import Admin
from cogs.carepackage import CarePackage
from cogs.owner import Owner
from cogs.snipe import Snipes
from cogs.soapbox import Soapbox
from cogs.utils import db
from cogs.utils.help import CustomHelpCommand

log = logging.getLogger(__name__)


class SnipeBot(commands.Bot):
    def __init__(self, config):
        prefix = '!'
        super().__init__(command_prefix=prefix, case_insensitive=True, help_command=CustomHelpCommand(),
                         activity=discord.Activity(type=discord.ActivityType.watching, name='!snipebot for help'))

        self.config = config

        club_info = config['club_time']

        day = club_info.get('day_of_week', -1)
        start = club_info.get('start_hour', -1)
        end = club_info.get('stop_hour', -1)

        self.add_cog(Soapbox(self))
        self.add_cog(Snipes(self, day, start, end))
        self.add_cog(Admin(self))
        self.add_cog(Owner(self))
        self.add_cog(CarePackage(self))

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return

        log.info(f"Error caused by message: `{ctx.message.content}`")
        log.info(''.join(traceback.format_exception_only(type(error), error)))

        if isinstance(error, commands.CommandInvokeError):
            return await ctx.send(f'CommandInvokeError: {error}')
        elif isinstance(error, (commands.MissingPermissions, commands.CheckFailure)):
            return await ctx.send(error)
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(f'BadArgument: {error}')
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f'MissingRequiredArgument: {error}')

    async def on_ready(self):
        log.info('Bot started: Database: ' + db.DATABASE)
        print('Ready. Database: ' + db.DATABASE)

    def run(self):
        super().run(self.config['token'])
