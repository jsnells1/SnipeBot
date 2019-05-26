import argparse
import configparser
import logging
import logging.handlers
import os
import sys
import traceback
from datetime import datetime, timedelta

import discord
import discord.ext.commands as commands

from cogs.admin import AdminCommands
from cogs.snipe import Snipes
from cogs.soapbox import Soapbox
from cogs.club_calendar import ClubCalendar
from data import api
from data.api import Environment

# Create log directory if it doesn't exist
if not os.path.exists('./log'):
    try:
        os.makedirs('./log')
    except:
        sys.exit('Log directory does not exist and cannot be created')

# Create logger
logging.getLogger('discord').setLevel(logging.WARNING)
log = logging.getLogger()
log.setLevel(level=logging.INFO)
handler = logging.handlers.RotatingFileHandler(
    filename='./log/snipebot.log', encoding='utf-8', maxBytes=10485760, backupCount=5)
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
log.addHandler(handler)

# Read and Verify config
config = configparser.ConfigParser()
config.sections()

config.read('config.cfg')

if 'TOKEN' not in config or 'Token' not in config['TOKEN']:
    log.fatal('Token not found in config file')
    sys.exit('Token not found in config file')

if 'SnipingExceptions' not in config:
    log.fatal('SnipingExceptions not found in config file')
    sys.exit('SnipingExceptions section not found in config file')

try:
    day = int(config['SnipingExceptions']['ClubDay'])
    start = int(config['SnipingExceptions']['ClubTimeStart'])
    end = int(config['SnipingExceptions']['ClubTimeStop'])
except:
    log.fatal('Could not resolve club day, start, and/or stop in config')
    sys.exit('Cannot resolve club day, start, and stop in config')

TOKEN = str(config['TOKEN']['Token'])
BOT_PREFIX = "!"

# Setup
parser = argparse.ArgumentParser()
parser.add_argument('-env')
args = parser.parse_args()

if args.env is not None:
    if args.env == 'dev':
        api.switchDatabase(Environment.dev)
    elif args.env == 'live':
        api.switchDatabase(Environment.live)


bot = commands.Bot(command_prefix=BOT_PREFIX, case_insensitive=True,
                   activity=discord.Activity(type=discord.ActivityType.listening, name='Logan\'s SI Session'))


@bot.command(name='q2', hidden=True)
@commands.has_role(item='Dev Team')
async def kill(ctx: commands.Context):
    await bot.logout()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    log.info("Error caused by message: `{}`".format(ctx.message.content))
    log.info(''.join(traceback.format_exception_only(type(error), error)))

    if isinstance(error, (commands.MissingPermissions, commands.CheckFailure)):
        return await ctx.send('```You don\'t have permissions to use that command.```')


@bot.event
async def on_ready():
    log.info('Bot started: Database: ' + api.DATABASE)
    print('Ready. Database: ' + api.DATABASE)

bot.add_cog(Soapbox(bot))
bot.add_cog(Snipes(bot, day, start, end))
bot.add_cog(AdminCommands(bot))
bot.add_cog(ClubCalendar(bot))
bot.run(TOKEN)
