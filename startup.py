from discord.ext.commands import Bot, Context, has_permissions, MissingPermissions

from sniping.snipe import Snipes
from admin.admin import AdminCommands
from soapbox.soapbox import Soapbox

TOKEN = 'NTY2MDU0MTYzNDk5NDUwMzk5.XK_aKg.-dGUgE3J1JgnJaVrnEJS8gFQDKw'
BOT_PREFIX = "!"

bot = Bot(command_prefix=BOT_PREFIX, case_insensitive=True)


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
    print('Ready')

bot.add_cog(Soapbox(bot))
bot.add_cog(Snipes(bot))
bot.add_cog(AdminCommands(bot))
bot.run(TOKEN)
