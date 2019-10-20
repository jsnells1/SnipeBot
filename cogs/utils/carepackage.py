from datetime import datetime

import aiosqlite

from data import api as Database


class Package():
    def __init__(self, guild, keyword, expiration, hint):
        self.guild = guild
        self.expiration = expiration
        self.keyword = keyword
        self.hint = hint

    @classmethod
    async def remove_expired(cls):
        now = datetime.now().timestamp()

        async with aiosqlite.connect(Database.DATABASE) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT Guild, Key FROM CarePackage WHERE Expiration < ?', (now,)) as cursor:
                rows = await cursor.fetchall()

            if len(rows) > 0:
                await db.execute('DELETE FROM CarePackage WHERE Expiration < ?', (now,))
                await db.commit()

            return rows

    @classmethod
    async def get_all(cls, guild):
        async with aiosqlite.connect(Database.DATABASE) as db:
            db.row_factory = aiosqlite.Row

            async with db.execute('SELECT * FROM CarePackage WHERE Guild = ?', (guild,)) as cursor:
                rows = await cursor.fetchall()
                carepackages = [Package(row['Guild'], row['Key'], row['Expiration'], row['Hint']) for row in rows]

                return carepackages

    @classmethod
    async def is_keyword(cls, guess, guild):
        async with aiosqlite.connect(Database.DATABASE) as db:
            async with db.execute('SELECT 1 FROM CarePackage WHERE Key = ? AND Guild = ?', (guess, guild)) as cursor:
                row = await cursor.fetchone()

                if row is None:
                    return False

                await db.execute('DELETE FROM CarePackage WHERE Key = ? AND Guild = ?', (guess, guild))
                await db.commit()

                return True

    async def save(self):
        async with aiosqlite.connect(Database.DATABASE) as db:
            await db.execute('INSERT INTO CarePackage (Guild, Key, Expiration, Hint) VALUES (?,?,?,?)', (self.guild, self.keyword, self.expiration, self.hint))
            await db.commit()

    def get_hint(self):
        return self.hint or 'There is no hint available.'
