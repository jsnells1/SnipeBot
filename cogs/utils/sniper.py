from datetime import datetime, timedelta

import aiosqlite
import discord

from cogs.utils.db import Database
from cogs.utils.formatting import SnipeFormatter
from cogs.utils.leaderboard import Leaderboard


class Sniper():
    def __init__(self, id, guild, name, **kwargs):
        self.id = id
        self.guild = guild
        self.display_name = name
        self.points = kwargs.get('points', 0)
        self.snipes = kwargs.get('snipes', 0)
        self.deaths = kwargs.get('deaths', 0)
        self.respawn = kwargs.get('respawn')
        self.revenge = kwargs.get('revenge')
        self.revenge_time = kwargs.get('revenge_time')
        self.killstreak = kwargs.get('killstreak', 0)
        self.killstreak_record = kwargs.get('killstreak_record', 0)
        self.multiplier = kwargs.get('multiplier', 1)
        self.multi_expiration = kwargs.get('multi_expiration')
        self.smokebomb = kwargs.get('smokebomb', 0)
        self.immunity = kwargs.get('immunity')

        self.has_potato = False

    @classmethod
    async def exists(cls, id, guild):
        async with aiosqlite.connect(Database.connection_string()) as db:
            async with db.execute('SELECT 1 FROM Scores WHERE UserID = ? AND Guild = ?', (id, guild)) as cursor:
                row = await cursor.fetchone()

                if row is not None:
                    return True

            async with db.execute('SELECT 1 FROM SnipingMods WHERE UserID = ? AND Guild = ?', (id, guild)) as cursor:
                row = await cursor.fetchone()

                return row is not None

    @classmethod
    async def from_database(cls, id, guild, name, register=False):

        if isinstance(guild, discord.Guild):
            guild = guild.id

        sniper = cls(id, guild, name)

        if register:
            await sniper.register_self()

        async with aiosqlite.connect(Database.connection_string()) as db:
            db.row_factory = aiosqlite.Row
            query = 'SELECT * FROM Scores s LEFT JOIN SnipingMods sm ON sm.UserID = s.UserID AND sm.Guild = s.Guild WHERE s.UserID = ? AND s.Guild = ?'
            async with db.execute(query, (id, guild)) as cursor:
                row = await cursor.fetchone()

                if row is None:
                    return None

                sniper.points = row['Points']
                sniper.snipes = row['snipes']
                sniper.deaths = row['Deaths']
                sniper.respawn = row['Respawn']
                sniper.revenge = row['Revenge']
                sniper.revenge_time = row['RevengeTime']
                sniper.killstreak = row['Killstreak']
                sniper.killstreak_record = row['KillstreakRecord']
                sniper.multiplier = row['Multiplier'] or 1
                sniper.multi_expiration = row['MultiExpiration']
                sniper.smokebomb = row['SmokeBomb']
                sniper.immunity = row['Immunity']

            query = 'SELECT 1 FROM HotPotato WHERE Owner = ? AND Guild = ? LIMIT 1'
            async with db.execute(query, (id, guild)) as cursor:
                sniper.has_potato = await cursor.fetchone() is not None

        return sniper

    @classmethod
    async def remove_user(cls, id, guild):
        async with aiosqlite.connect(Database.connection_string()) as db:
            await db.execute('DELETE FROM Scores WHERE UserID = ? AND Guild = ?', (id, guild))
            await db.execute('DELETE FROM SnipingMods WHERE UserID = ? AND Guild = ?', (id, guild))

            await db.commit()

    @classmethod
    async def get_respawns(cls):
        async with aiosqlite.connect(Database.connection_string()) as db:
            date = datetime.now().timestamp()
            async with db.execute('SELECT Guild, UserID FROM Scores WHERE Respawn < ?', (date,)) as cursor:
                rows = await cursor.fetchall()

                await db.execute('UPDATE Scores SET Respawn = ? WHERE Respawn < ?', (None, date))
                await db.commit()

                return rows

    @classmethod
    async def get_expired_immunes(cls):
        now = datetime.now().timestamp()
        async with aiosqlite.connect(Database.connection_string()) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT Guild, UserID FROM SnipingMods WHERE Immunity < ?', (now,)) as cursor:
                rows = await cursor.fetchall()

            if len(rows) > 0:
                await db.execute('UPDATE SnipingMods SET Immunity = ? WHERE Immunity < ?', (None, now, ))
                await db.commit()

            return rows

    @classmethod
    async def get_exploded_potatoes(cls):
        pointDeduction = 3
        now = datetime.now().timestamp()

        async with aiosqlite.connect(Database.connection_string()) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT Guild, Owner FROM HotPotato WHERE Explosion < ?', (now,)) as cursor:
                rows = await cursor.fetchall()

            if len(rows) > 0:
                await db.execute('DELETE FROM HotPotato WHERE Explosion < ?', (now,))

            for row in rows:
                await db.execute('UPDATE Scores SET Points = MAX(0, Points - ?), Deaths = Deaths + 1 WHERE UserID =  ?', (pointDeduction, row['Owner']))

            await db.commit()

            return rows

    @classmethod
    async def remove_expired_revenges(cls):
        now = datetime.now().timestamp()

        async with aiosqlite.connect(Database.connection_string()) as db:
            await db.execute('UPDATE Scores SET Revenge = ?, RevengeTime = ? WHERE RevengeTime < ?', (None, None, now))
            await db.commit()

    async def give_potato(self, explosion):
        async with aiosqlite.connect(Database.connection_string()) as db:
            await db.execute('INSERT INTO HotPotato (Owner, Explosion) VALUES (?, ?)', (self.id, explosion))
            await db.commit()

    async def pass_potato(self, target):
        async with aiosqlite.connect(Database.connection_string()) as db:
            await db.execute('UPDATE HotPotato SET Owner = ? WHERE Owner = ? AND Guild = ?', (target.id, self.id, self.guild))
            await db.commit()

    async def register_self(self):
        async with aiosqlite.connect(Database.connection_string()) as db:
            await db.execute('INSERT OR IGNORE INTO Scores(UserID, Guild, Name) VALUES (?, ?, ?)', (self.id, self.guild, self.display_name))
            await db.execute('INSERT OR IGNORE INTO SnipingMods(UserID, Guild, Name) VALUES (?, ?, ?)', (self.id, self.guild, self.display_name))

            await db.commit()

    async def snipe(self, ctx, targets):
        hits = []
        immune = []
        respawns = []

        # Convert targets to list of Sniper objects, ignoring bots
        targets = [await Sniper.from_database(target.id, ctx.guild.id, target.display_name, register=True) for target in targets if not target.bot]

        leaderboard = await Leaderboard.load()
        leader_id = leaderboard.get_leader_id()

        bonus_points = 0

        leader_hit = False

        respawn = (datetime.now() + timedelta(hours=2)).timestamp()
        revenge = (datetime.now() + timedelta(hours=3, minutes=30)).timestamp()

        revenge_name = None

        for target in targets:

            # Ignore immune users
            if target.is_immune():
                immune.append(target)
                continue

            # Ignore respawning users
            if target.is_respawning():
                respawns.append(target)
                continue

            self.snipes += 1
            self.respawn = None
            target.deaths += 1
            target.killstreak = 0
            target.respawn = respawn
            target.revenge = self.id
            target.revenge_time = revenge

            if target.id == leader_id:
                leader_hit = True
                bonus_points += 3

            if target.id == self.revenge:
                revenge_name = target.display_name
                bonus_points += 2

                # Make sure to reset revenge
                self.revenge = None
                self.revenge_time = None

            hits.append(target)

            await target.update()

        new_potato_owner = None
        num_hits = len(hits)
        if num_hits > 0:
            self.killstreak += num_hits
            self.killstreak_record = max(self.killstreak_record, self.killstreak)

            if self.has_potato:
                await self.pass_potato(hits[0])
                new_potato_owner = hits[0]

        # Add the bonus points to the number of hits (1 point per hit) then multiply by the user's multiplier
        total_points = (bonus_points + len(hits)) * self.multiplier
        # Add the points to the user in the database
        self.points += total_points
        await self.update()

        formatter = SnipeFormatter(sniper=self, hits=hits, respawns=respawns, immunes=immune, new_potato_owner=new_potato_owner,
                                   leader_hit=leader_hit, revenge_member=revenge_name, total_points=total_points)

        output = formatter.formatted_output()

        return output

    async def update(self):
        scores_info = (self.display_name, self.points, self.snipes, self.deaths, self.respawn, self.revenge, self.revenge_time, self.killstreak, self.killstreak_record, self.id, self.guild)
        snipingmods_info = (self.display_name, self.multiplier, self.multi_expiration, self.smokebomb, self.immunity, self.id, self.guild)

        scores_query = 'UPDATE Scores SET Name = ?, Points = ?, Snipes = ?, Deaths = ?, Respawn = ?, Revenge = ?, RevengeTime = ?, Killstreak = ?, KillstreakRecord = ? WHERE UserID = ? AND Guild = ?'
        snipingmods_query = 'UPDATE SnipingMods SET Name = ?, Multiplier = ?, MultiExpiration = ?, SmokeBomb = ?, Immunity = ? WHERE UserID = ? AND Guild = ?'

        async with aiosqlite.connect(Database.connection_string()) as db:
            await db.execute(scores_query, scores_info)
            await db.execute(snipingmods_query, snipingmods_info)
            await db.commit()

    async def use_smokebomb(self):
        if self.smokebomb > 0:
            self.smokebomb -= 1
            expiration = datetime.now() + timedelta(hours=3)
            self.immunity = expiration.timestamp()
            await self.update()

    def is_immune(self):
        return self.immunity and self.immunity > datetime.now().timestamp()

    def is_respawning(self):
        return self.respawn and self.respawn > datetime.now().timestamp()
