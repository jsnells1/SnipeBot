import discord
import discord.ext.commands as commands


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        await self.bot.logout()

    @commands.command(name='backup_db')
    @commands.is_owner()
    async def backup_db(self, ctx: commands.Context):
        dev_db = discord.File(fp='./data/dev_database.db')
        live_db = discord.File(fp='./data/database.db')

        await ctx.author.send('', files=[dev_db, live_db])
