import discord
import discord.ext.commands as commands

from cogs.utils.db import Database, Environment


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
        dev_db = discord.File(fp=Database.dev_database())
        live_db = discord.File(fp=Database.live_database())

        await ctx.author.send('', files=[dev_db, live_db])

    @commands.command(name='switchDB', usage='{dev | live}', hidden=True)
    @commands.is_owner()
    async def switchDB(self, ctx: commands.Context, env: Environment):
        Database.switch_database(env)

        await ctx.send('Database successfully changed.')
        print('Database: ' + Database.connection_string())
