import argparse
import configparser
import logging
import logging.handlers
import os
import sys
from datetime import datetime, timedelta

import discord
import discord.ext.commands as commands

from admin.admin import AdminCommands
from data import code
from data.code import Environment
from sniping.snipe import Snipes
from soapbox.soapbox import Soapbox

# Create logger
logging.getLogger('discord').setLevel(logging.WARNING)
log = logging.getLogger()
log.setLevel(level=logging.INFO)
handler = logging.handlers.RotatingFileHandler(
    filename='./log/snipebot.log', encoding='utf-8', maxBytes=10485760, backupCount=5)
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
log.addHandler(handler)

# Create log directory if it doesn't exist
if not os.path.exists('./log'):
    try:
        os.makedirs('./log')
    except:
        log.fatal('Log directory does not exist and cannot be created')
        sys.exit('Log directory does not exist and cannot be created')


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
        code.switchDatabase(Environment.dev)
    elif args.env == 'live':
        code.switchDatabase(Environment.live)


bot = commands.Bot(command_prefix=BOT_PREFIX, case_insensitive=True,
                   activity=discord.Activity(type=discord.ActivityType.listening, name='Logan\'s SI Session'))


@bot.command(name='q2', hidden=True)
@commands.has_role(item='Dev Team')
async def kill(ctx: commands.Context):
    await bot.logout()


@bot.event
async def on_ready():
    log.info('Bot started: Database: ' + code.DATABASE)
    print('Ready. Database: ' + code.DATABASE)


bot.add_cog(Soapbox(bot))
bot.add_cog(Snipes(bot, day, start, end))
bot.add_cog(AdminCommands(bot))
bot.run(TOKEN)
