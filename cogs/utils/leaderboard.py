import aiosqlite

from tabulate import tabulate
from discord.ext import commands

import cogs.utils.db as Database


class Leaderboard():
    def __init__(self, ctx):
        self.ctx = ctx

    async def get_highest_killstreak(self):
        async with aiosqlite.connect(Database.DATABASE) as db:
            db.row_factory = aiosqlite.Row
            query = 'SELECT UserID, KillstreakRecord FROM Scores ORDER BY KillstreakRecord DESC LIMIT 1'
            async with db.execute(query) as cursor:
                return await cursor.fetchone()

    async def get_leaderboard(self):
        outputRows = [['Name', 'P', 'S', 'D']]

        rows = await self.get_rows()
        killstreak_info = await self.get_highest_killstreak()

        killstreak_holder = 'None'
        killstreak_record = 'None'

        if killstreak_info is not None:
            killstreak_holder = self.ctx.guild.get_member(killstreak_info['UserID']).display_name[0:8]
            killstreak_record = str(killstreak_info['KillstreakRecord'])

        for row in rows:
            user = await commands.MemberConverter().convert(self.ctx, str(row['UserID']))

            outputRows.append([user.display_name[0:8], str(row['Points']), str(row['Snipes']), str(row['Deaths'])])

        records = [['Record', 'User', '']]

        records.append(['Streak', killstreak_holder, killstreak_record])

        output = tabulate(records, headers='firstrow', tablefmt='fancy_grid') + '\n\n'
        output += 'P=Points, S=Snipes, D=Deaths\n'
        output += tabulate(outputRows, headers='firstrow', tablefmt='fancy_grid')
        return output

    async def get_rows(self):
        async with aiosqlite.connect(Database.DATABASE) as db:
            db.row_factory = aiosqlite.Row
            query = 'SELECT UserID, Points, Snipes, Deaths FROM Scores ORDER BY Points DESC, Snipes DESC, Deaths ASC LIMIT 10'
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
                return rows
