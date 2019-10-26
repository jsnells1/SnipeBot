import aiosqlite

from tabulate import tabulate
from discord.ext import commands

import cogs.utils.db as Database


class NotLoadedException(Exception):
    pass


class Leaderboard():
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        self.killstreak_record_holder = 'None'
        self.killstreak_record = 'None'
        self.users = 0
        self.rows = None

        self._loaded = False

    @classmethod
    async def load(cls, ctx: commands.Context):
        leaderboard = cls(ctx)

        await leaderboard._load_rows()
        await leaderboard._load_killstreak_record()
        await leaderboard._load_user_count()

        leaderboard._loaded = True

        return leaderboard

    async def _load_user_count(self):
        async with aiosqlite.connect(Database.DATABASE) as db:
            async with db.execute('SELECT COUNT(rowid) FROM Scores') as cursor:
                row = await cursor.fetchone()

                self.users = row[0]

    async def _load_killstreak_record(self):
        async with aiosqlite.connect(Database.DATABASE) as db:
            db.row_factory = aiosqlite.Row
            query = 'SELECT UserID, KillstreakRecord FROM Scores ORDER BY KillstreakRecord DESC LIMIT 1'
            async with db.execute(query) as cursor:
                row = await cursor.fetchone()

                if row:
                    user = self.ctx.guild.get_member(row['UserID'])

                    self.killstreak_record_holder = user.display_name[0:8]
                    self.killstreak_record = row['KillstreakRecord']

    async def _load_rows(self):
        async with aiosqlite.connect(Database.DATABASE) as db:
            db.row_factory = aiosqlite.Row
            query = 'SELECT UserID, Name, Points, Snipes, Deaths FROM Scores ORDER BY Points DESC, Snipes DESC, Deaths ASC LIMIT 10'
            async with db.execute(query) as cursor:
                self.rows = await cursor.fetchall()

    def get_leader_id(self):
        if not self._loaded:
            raise NotLoadedException('load method not called')

        if self.users == 0:
            return None

        possible_leader = self.rows[0]

        if possible_leader['snipes'] == 0 and possible_leader['deaths'] == 0 and possible_leader['points'] != 0:
            return None

        return self.rows[0]['UserID']

    async def display_leaderboard(self):
        if not self._loaded:
            raise NotLoadedException('load method not yet called')

        outputRows = [['Name', 'P', 'S', 'D']]

        for row in self.rows:
            user = await commands.MemberConverter().convert(self.ctx, str(row['UserID']))

            outputRows.append([user.display_name[0:8], str(row['Points']), str(row['Snipes']), str(row['Deaths'])])

        records = [['Record', 'User', '']]

        records.append(['Streak', self.killstreak_record_holder, self.killstreak_record])

        output = tabulate(records, headers='firstrow', tablefmt='fancy_grid') + '\n\n'
        output += 'P=Points, S=Snipes, D=Deaths\n'
        output += tabulate(outputRows, headers='firstrow', tablefmt='fancy_grid')
        return output
