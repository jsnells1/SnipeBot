import argparse

import discord
from discord.ext.commands import Bot, Context, has_permissions, MissingPermissions

from sniping.snipe import Snipes
from admin.admin import AdminCommands
from soapbox.soapbox import Soapbox

from data import code
from data.code import Environment

TOKEN = 'NTY2MDU0MTYzNDk5NDUwMzk5.XK_aKg.-dGUgE3J1JgnJaVrnEJS8gFQDKw'
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
bot.add_cog(Snipes(bot))
bot.add_cog(AdminCommands(bot))
bot.run(TOKEN)
