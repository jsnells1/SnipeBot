import discord
import discord.ext.commands as commands

import cogs.utils.db as Database


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        await self.bot.logout()

    @commands.command(name='backup_db', hidden=True)
    @commands.is_owner()
    async def backup_db(self, ctx: commands.Context):
        dev_db = discord.File(fp='./data/dev_database.db')
        live_db = discord.File(fp='./data/database.db')

        await ctx.author.send('', files=[dev_db, live_db])

    @commands.command(name='switchDB', hidden=True)
    @commands.is_owner()
    async def switchDB(self, ctx: commands.Context, env=None):
        if env is None:
            await ctx.send('Please pass the environment to switch to (live/dev)')
            return

        if env == 'live':
            dbEnv = Database.Environment.LIVE
        elif env == 'dev':
            dbEnv = Database.Environment.DEV
        else:
            await ctx.send('Invalid argument.')
            return

        Database.switch_database(dbEnv)

        await ctx.send('Database successfully changed.')
        print('Database: ' + Database.DATABASE)
