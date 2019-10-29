import logging
import traceback

import discord
import discord.ext.commands as commands

from cogs.admin import Admin
from cogs.carepackage import CarePackage
from cogs.help import CustomHelpCommand, Help
from cogs.owner import Owner
from cogs.snipe import Snipes
from cogs.soapbox import Soapbox
from cogs.utils.db import Database

log = logging.getLogger(__name__)


class SnipeBot(commands.Bot):
    def __init__(self, config):
        prefix = '!'
        description = 'NEW USERS: Use !overview for a basic rundown on how to snipe someone'
        super().__init__(command_prefix=prefix, case_insensitive=True, help_command=CustomHelpCommand(), description=description,
                         activity=discord.Activity(type=discord.ActivityType.watching, name='!snipebot for help'))

        self.config = config

        self.add_cog(Soapbox(self))
        self.add_cog(Snipes(self))
        self.add_cog(Admin(self))
        self.add_cog(Owner(self))
        self.add_cog(CarePackage(self))
        self.add_cog(Help(self))

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
            error_string = f'BadArgument: {error}'
            if ctx.command.usage:
                error_string += f'\nUsage: {ctx.prefix}{ctx.invoked_with} {ctx.command.usage}'
            return await ctx.send(error_string)
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f'MissingRequiredArgument: {error}')

    async def on_ready(self):
        log.info('Bot started: Database: ' + Database.connection_string())
        print('Ready. Database: ' + Database.connection_string())

    @commands.command()
    async def overview(self, ctx):
        await ctx.send('Overview')

    def run(self):
        super().run(self.config['token'])
