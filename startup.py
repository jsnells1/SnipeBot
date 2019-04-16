import argparse
import configparser
import sys
from datetime import datetime, timedelta

import discord
from discord.ext.commands import Bot, Context, has_permissions, MissingPermissions

from sniping.snipe import Snipes
from admin.admin import AdminCommands
from soapbox.soapbox import Soapbox

from data import code
from data.code import Environment

# Read and Verify config

config = configparser.ConfigParser()
config.sections()

config.read('config.ini')

if 'TOKEN' not in config or 'Token' not in config['TOKEN']:
    sys.exit('Token not found in config file')

if 'SnipingExceptions' not in config:
    sys.exit('SnipingExceptions section not found in config file')

try:
    day = int(config['SnipingExceptions']['ClubDay'])
    start = int(config['SnipingExceptions']['ClubTimeStart'])
    end = int(config['SnipingExceptions']['ClubTimeStop'])
except:
    sys.exit('Cannot resolve club day, start, and stop in config')

TOKEN = str(config['TOKEN']['Token'])
BOT_PREFIX = "!"

bot = Bot(command_prefix=BOT_PREFIX, case_insensitive=True,
          activity=discord.Activity(type=discord.ActivityType.watching, name='Nathan\'s snap story'))


@bot.command(name='q2', hidden=True)
@has_permissions(ban_members=True)
async def kill(ctx: Context):
    await bot.logout()


@kill.error
async def kill_error(error, ctx: Context):
    if isinstance(error, MissingPermissions):
        text = "Sorry {}, you do not have permissions to do that!".format(
            ctx.message.author)
        await ctx.send(text)


@bot.event
async def on_ready():
    print('Ready. Database: ' + code.DATABASE)


# Setup
parser = argparse.ArgumentParser()
parser.add_argument('-env')
args = parser.parse_args()

if args.env is not None:
    if args.env == 'dev':
        code.switchDatabase(Environment.dev)
    elif args.env == 'live':
        code.switchDatabase(Environment.live)

bot.add_cog(Soapbox(bot))
bot.add_cog(Snipes(bot, day, start, end))
bot.add_cog(AdminCommands(bot))
bot.run(TOKEN)
