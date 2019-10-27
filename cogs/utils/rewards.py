from datetime import datetime, timedelta

import aiosqlite

import cogs.utils.db as Database
from cogs.utils.sniper import Sniper


class Reward():
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    @classmethod
    async def from_database(cls, id: int):
        async with aiosqlite.connect(Database.DATABASE) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM CarePackageRwds WHERE id = ?', (id,)) as cursor:
                row = await cursor.fetchone()

                if row:
                    return cls(row['id'], row['Name'], row['Description'])

    @classmethod
    async def get_random(cls):
        async with aiosqlite.connect(Database.DATABASE) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM CarePackageRwds ORDER BY RANDOM() LIMIT 1') as cursor:
                row = await cursor.fetchone()

                if row:
                    return cls(row['id'], row['Name'], row['Description'])

    async def redeem(self, user):
        if not isinstance(user, Sniper):
            user = await Sniper.from_database(user.id, user.guild.id, user.display_name, register=True)

        # 8 Bonus Points
        if self.id == 1:
            bonus_points = 8

            user.points += bonus_points
            await user.update()

            return f'{bonus_points} bonus points immediately'
        # x3 Multiplier for 24 Hours
        elif self.id == 2:
            multiplier = 3
            expiration = (datetime.now() + timedelta(hours=24)).timestamp()

            user.multiplier = multiplier
            user.multi_expiration = expiration
            await user.update()

            return f'a x{multiplier} point multiplier for 24 hours'
        # Smoke Bomb
        elif self.id == 3:
            user.smokebomb += 1
            await user.update()

            return 'a smoke bomb! Use it whenever you\'d like for 3 hours of immunity!'
        # Hot Potato
        elif self.id == 4:
            expiration = (datetime.now() + timedelta(hours=24)).timestamp()

            await user.give_potato(expiration)

            return 'a... Hot Potato Bomb! Uh Oh! Snipe someone else to pass it to someone else before it explodes'
