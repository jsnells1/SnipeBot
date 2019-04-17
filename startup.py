import argparse
import configparser
import sys
from datetime import datetime, timedelta

import discord
import discord.ext.commands as commands

from sniping.snipe import Snipes
from admin.admin import AdminCommands
from soapbox.soapbox import Soapbox

from data import code
from data.code import Environment

# Read and Verify config

config = configparser.ConfigParser()
config.sections()

config.read('config.cfg')

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

bot = commands.Bot(command_prefix=BOT_PREFIX, case_insensitive=True,
          activity=discord.Activity(type=discord.ActivityType.listening, name='Logan\'s SI Session'))


@bot.command(name='q2', hidden=True)
@commands.has_permissions(ban_members=True)
async def kill(ctx: commands.Context):
    await bot.logout()


@kill.error
async def kill_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingPermissions):
        text = "Sorry {}, you do not have permissions to do that!".format(
            ctx.message.author.mention)
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
