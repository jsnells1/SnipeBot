from discord.ext.commands import Bot
from discord.ext.commands import Context

from snipe import Snipes


TOKEN = 'NTY2MDU0MTYzNDk5NDUwMzk5.XK_aKg.-dGUgE3J1JgnJaVrnEJS8gFQDKw'
BOT_PREFIX = "!"

bot = Bot(command_prefix=BOT_PREFIX, case_insensitive=True)


@bot.command(name='q2')
async def kill(ctx: Context):
    await bot.logout()



@bot.command(name='GoodBot')
async def mrgoodiegood(ctx: Context):
    await ctx.send(':)')


@bot.event
async def on_ready():
    print('Ready')

bot.add_cog(Snipes(bot))
bot.run(TOKEN)
