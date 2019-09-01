import aiosqlite

from datetime import datetime, timedelta

from cogs.utils.leaderboard import Leaderboard
from cogs.utils.formatting import formatSnipeString

import data.api as Database


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

    @classmethod
    async def exists(cls, id, guild):
        async with aiosqlite.connect(Database.DATABASE) as db:
            async with db.execute('SELECT 1 FROM Scores WHERE UserID = ? AND Guild = ?', (id, guild)) as cursor:
                row = await cursor.fetchone()

                if row is not None:
                    return True

            async with db.execute('SELECT 1 FROM SnipingMods WHERE UserID = ? AND Guild = ?', (id, guild)) as cursor:
                row = await cursor.fetchone()

                return row is not None

    @classmethod
    async def from_database(cls, id, guild, name, register=False):
        sniper = cls(id, guild, name)

        if register:
            await sniper.register_self()

        async with aiosqlite.connect(Database.DATABASE) as db:
            db.row_factory = aiosqlite.Row
            query = 'SELECT * FROM Scores s LEFT JOIN SnipingMods sm ON sm.UserID = s.UserID AND sm.Guild = s.Guild WHERE s.UserID = ? AND s.Guild = ?'
            async with db.execute(query, (id, guild)) as cursor:
                row = await cursor.fetchone()

                if row is None:
                    return sniper

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

        return sniper

    @classmethod
    async def remove_user(cls, id, guild):
        async with aiosqlite.connect(Database.DATABASE) as db:
            await db.execute('DELETE FROM Scores WHERE UserID = ? AND Guild = ?', (id, guild))
            await db.execute('DELETE FROM SnipingMods WHERE UserID = ? AND Guild = ?', (id, guild))

            await db.commit()

    async def add_points(self, points):
        async with aiosqlite.connect(Database.DATABASE) as db:
            await db.execute('UPDATE Scores SET Points = Points + ? WHERE UserID = ?', (points, self.id))
            await db.commit()

        self.points += points

    async def add_snipe(self, target):
        try:
            await self.register_self()
            await target.register_self()
        except:
            return False

        try:
            async with aiosqlite.connect(Database.DATABASE) as db:
                await db.execute('UPDATE Scores SET Snipes = Snipes + 1, Respawn = ? WHERE UserID = ?', (None, self.id))

                respawn = datetime.now() + timedelta(hours=2)
                revenge = datetime.now() + timedelta(hours=3, minutes=30)

                await db.execute('UPDATE Scores SET Deaths = Deaths + 1, Killstreak = 0, Respawn = ?, Revenge = ?, RevengeTime = ? WHERE UserID = ?',
                                 (respawn.timestamp(), self.id, revenge.timestamp(), target.id))

                await db.commit()

                self.snipes += 1
                self.respawn = None
                target.deaths += 1
                target.killstreak = 0
                target.respawn = respawn
                target.revenge = self.id
                target.revenge_time = revenge

            return True

        except:
            return False

    async def has_potato(self):
        async with aiosqlite.connect(Database.DATABASE) as db:
            query = 'SELECT 1 FROM HotPotato WHERE Owner = ? AND Guild = ? LIMIT 1'
            async with db.execute(query, (self.id, self.guild)) as cursor:
                return await cursor.fetchone() is not None

    async def pass_potato(self, target):
        async with aiosqlite.connect(Database.DATABASE) as db:
            await db.execute('UPDATE HotPotato SET Owner = ? WHERE Owner = ? AND Guild = ?', (self.id, target.id, self.guild))
            await db.commit()

    async def register_self(self):
        async with aiosqlite.connect(Database.DATABASE) as db:
            await db.execute('INSERT OR IGNORE INTO Scores(UserID, Guild, Name) VALUES (?, ?, ?)', (self.id, self.guild, self.display_name))
            await db.execute('INSERT OR IGNORE INTO SnipingMods(UserID, Guild, Name) VALUES (?, ?, ?)', (self.id, self.guild, self.display_name))

            await db.commit()

    async def reset_revenge(self):
        async with aiosqlite.connect(Database.DATABASE) as db:
            await db.execute('UPDATE Scores SET Revenge = ?, RevengeTime = ? WHERE UserID = ?', (None, None, self.id))
            await db.commit()

            self.revenge = None
            self.revenge_time = None

    async def set_multiplier(self, multiplier, expiration=None):
        async with aiosqlite.connect(Database.DATABASE) as db:
            await db.execute('UPDATE SnipingMods SET Multiplier = ?, MultiExpiration = ? WHERE UserID = ? AND Guild = ?', (multiplier, expiration, self.id, self.guild))
            await db.commit()

    async def snipe(self, ctx, targets):
        hits = []
        immune = []
        respawns = []
        errors = []

        # Convert targets to list of Sniper objects, ignoring bots
        targets = [await Sniper.from_database(target.id, ctx.guild.id, target.display_name, register=True) for target in targets if not target.bot]

        leaderboard = await Leaderboard(ctx).get_rows()

        leader_id = None
        if len(leaderboard) > 0:
            leader_id = leaderboard[0]['UserID']

        bonusPoints = 0

        leaderHit = False
        revengeHit = False

        for loser in targets:

            # Ignore immune users
            if loser.is_immune():
                immune.append(loser)
                continue

            # Ignore respawning users
            if loser.is_respawning():
                respawns.append(loser)
                continue

            # Try to register the snipe
            if await self.add_snipe(loser):
                if loser.id == leader_id:
                    leaderHit = True
                    bonusPoints += 3

                if loser.id == self.revenge:
                    revengeHit = True
                    bonusPoints += 2
                    await self.reset_revenge()

                hits.append(loser)
            else:
                errors.append(loser)

            hasPotato = False
            if len(hits) > 0:
                await self.update_killstreak(len(hits))
                hasPotato = await self.has_potato()
                if hasPotato:
                    await self.pass_potato(hits[0])

            killstreak = self.killstreak
            # Add the bonus points to the number of hits (1 point per hit) then multiply by the user's multiplier
            totalPoints = (bonusPoints + len(hits)) * self.multiplier
            # Add the points to the user in the database
            await self.add_points(totalPoints)
            # Get the discord user for the revenge target, will return None if not found or if revenge is None
            revengeMember = ctx.guild.get_member(self.revenge)

            output = formatSnipeString(sniper=self, hits=hits, respawns=respawns, immune=immune, errors=errors, hasPotato=hasPotato, leaderHit=leaderHit,
                                       revengeHit=revengeHit, killstreak=killstreak, revengeMember=revengeMember, totalPoints=totalPoints, multiplier=self.multiplier)

            return output

    async def update_killstreak(self, kills):
        killstreak_record = max(self.killstreak + kills, self.killstreak_record)
        async with aiosqlite.connect(Database.DATABASE) as db:
            await db.execute('UPDATE Scores SET Killstreak = Killstreak + ?, KillstreakRecord = ? WHERE UserID = ?', (kills, killstreak_record, self.id))
            await db.commit()

        self.killstreak_record = killstreak_record
        self.killstreak += kills

    def is_immune(self):
        return self.immunity and self.immunity > datetime.now().timestamp()

    def is_respawning(self):
        return self.respawn and self.respawn > datetime.now().timestamp()
