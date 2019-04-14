from discord.ext.commands import Bot, Context, has_permissions, MissingPermissions

from sniping.snipe import Snipes
from admin.admin import AdminCommands
from soapbox.soapbox import Soapbox

from data.bot_database import BotDatabase, Environment

TOKEN = 'NTY2MDU0MTYzNDk5NDUwMzk5.XK_aKg.-dGUgE3J1JgnJaVrnEJS8gFQDKw'
BOT_PREFIX = "!"

bot = Bot(command_prefix=BOT_PREFIX, case_insensitive=True)


@bot.command(name='q2', hidden=True)
@has_permissions(ban_members=True)
async def kill(ctx: Context):
    await bot.logout()


@bot.command(name='switchDB', hidden=True)
@has_permissions(ban_members=True)
async def switchDB(ctx: Context, env=None):

    if env is None:
        await ctx.send('Please pass the environment to switch to (live/dev)')
        return

    if env == 'live':
        dbEnv = Environment.live
    elif env == 'dev':
        dbEnv = Environment.dev
    else:
        await ctx.send('Invalid argument.')
        return

    response = BotDatabase().switchDatabase(dbEnv)

    if response:
        await ctx.send('Database successfully changed.')
    else:
        await ctx.send('Error changing database.')


@kill.error
async def kill_error(error, ctx: Context):
    if isinstance(error, MissingPermissions):
        text = "Sorry {}, you do not have permissions to do that!".format(
            ctx.message.author)
        await ctx.send(text)


@bot.event
async def on_ready():
    print('Ready')

bot.add_cog(Soapbox(bot))
bot.add_cog(Snipes(bot))
bot.add_cog(AdminCommands(bot))
bot.run(TOKEN)
