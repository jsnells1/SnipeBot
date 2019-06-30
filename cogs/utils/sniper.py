import aiosqlite

from datetime import datetime, timedelta

from data import api


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
    async def from_database(cls, id, guild, name):
        sniper = cls(id, guild, name)

        async with aiosqlite.connect(api.DATABASE) as db:
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

    async def register_self(self):
        async with aiosqlite.connect(api.DATABASE) as db:
            await db.execute('INSERT OR IGNORE INTO Scores(UserID, Guild, Name) VALUES (?, ?, ?)', (self.id, self.guild, self.display_name))
            await db.execute('INSERT OR IGNORE INTO SnipingMods(UserID, Guild, Name) VALUES (?, ?, ?)', (self.id, self.guild, self.display_name))

            await db.commit()

    async def add_snipe(self, target):
        try:
            await self.register_self()
            await target.register_self()
        except:
            return False

        try:
            async with aiosqlite.connect(api.DATABASE) as db:
                await db.execute('UPDATE Scores SET Snipes = Snipes + 1, Respawn = ? WHERE UserID = ?', (None, self.id))

                respawn = datetime.now() + timedelta(hours=2)
                revenge = datetime.now() + timedelta(hours=3, minutes=30)

                await db.execute('UPDATE Scores SET Deaths = Deaths + 1, Killstreak = 0, Respawn = ?, Revenge = ?, RevengeTime = ? WHERE UserID = ?',
                                 (respawn.timestamp(), self.id, revenge.timestamp(), target.id))

                await db.commit()

            return True

        except:
            return False

    def is_immunue(self):
        return self.immunity and self.immunity > datetime.now().timestamp()

    def is_respawning(self):
        return self.respawn and self.respawn > datetime.now().timestamp()
