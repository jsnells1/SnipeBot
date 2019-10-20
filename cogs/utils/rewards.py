from datetime import datetime, timedelta

import aiosqlite

from cogs.utils.sniper import Sniper
from data import api as Database


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

async def set_bonus_points(user):
    # id 1
    bonus_points = 8
    sniper = await Sniper.from_database(user.id, user.guild.id, user.display_name)
    sniper.points += bonus_points
    await sniper.update()

    return f'{bonus_points} bonus points immediately'


async def set_multiplier(user):
    # id 2
    multiplier = 3
    expiration = datetime.now() + timedelta(hours=24)

    sniper = await Sniper.from_database(user.id, user.guild.id, user.display_name, register=True)
    await sniper.set_multiplier(multiplier, expiration=expiration.timestamp())

    return f'a x{multiplier} point multiplier for 24 hours'


async def set_smoke_bomb(user):
    # id 3
    sniper = await Sniper.from_database(user.id, user.guild.id, user.display_name, register=True)
    sniper.smokebomb += 1
    await sniper.update()

    return 'a smoke bomb! Use it whenever you\'d like for 3 hours of immunity!'


async def set_hot_potato(user):
    # id 4
    expiration = datetime.now() + timedelta(hours=24)

    sniper = await Sniper.from_database(user.id, user.guild.id, user.display_name, register=True)
    await sniper.give_potato(expiration.timestamp())

    return 'a... Hot Potato Bomb! Uh Oh! Snipe someone else to pass it to someone else before it explodes'


function_map = {
    1: set_bonus_points,
    2: set_multiplier,
    3: set_smoke_bomb,
    4: set_hot_potato
}


async def get_reward(id, user):
    return await function_map[id](user)
