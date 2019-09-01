import logging
import sqlite3
from datetime import datetime, timedelta

import aiosqlite

from data import api

log = logging.getLogger(__name__)


def _executeStmt_noReturn(cmds):
    try:
        # Input validation
        for cmd in cmds:
            if not isinstance(cmd, tuple) or len(cmd) != 2:
                raise ValueError('cmds must be a list of tuples of size 2')

            if not isinstance(cmd[0], str) or not isinstance(cmd[1], tuple):
                raise ValueError(
                    'Each command must be a tuple of size 2 with the string command and the parameter tuple')

        with sqlite3.connect(api.DATABASE) as conn:
            for cmd in cmds:
                stmt = cmd[0]
                params = cmd[1]

                conn.execute(stmt, params)

            conn.commit()

        return True

    except Exception as e:
        log.critical('Error executing statement(s): %s', cmds, exc_info=e)
        return False


# region Inserting and Updating

def set_user_multiplier(userId, multiplier):
    expiration = datetime.now() + timedelta(hours=24)

    commands = [('INSERT or IGNORE INTO SnipingMods (UserID) VALUES (?)', (userId,)),
                ('UPDATE SnipingMods SET Multiplier = ?, MultiExpiration = ? WHERE UserID = ?', (multiplier, expiration.timestamp(), userId,))]

    return _executeStmt_noReturn(commands)


def set_user_immunity(userId, expiration):

    commands = [('INSERT or IGNORE INTO SnipingMods (UserID) VALUES (?)', (userId,)),
                ('UPDATE SnipingMods SET Immunity = ? WHERE UserID = ?', (expiration, userId,))]

    return _executeStmt_noReturn(commands)


def pass_potato(sender, receiver):
    commands = [
        ('UPDATE HotPotato SET Owner = ? WHERE Owner = ?', (receiver, sender,))]

    return _executeStmt_noReturn(commands)

# endregion Inserting and Updating


async def remove_expired_carepackage():
    now = datetime.now().timestamp()

    async with aiosqlite.connect(api.DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT Guild, Key FROM CarePackage WHERE Expiration < ?', (now,)) as cursor:
            rows = await cursor.fetchall()

        if len(rows) > 0:
            await db.execute('DELETE FROM CarePackage WHERE Expiration < ?', (now,))
            await db.commit()

        return rows


def get_random_reward():
    try:
        with sqlite3.connect(api.DATABASE) as conn:

            row = conn.execute(
                'SELECT id, Name FROM CarePackageRwds ORDER BY RANDOM() LIMIT 1').fetchone()

            return row

    except Exception as e:
        print(e)
        return False


def set_user_smokebomb(userId):
    try:
        with sqlite3.connect(api.DATABASE) as conn:
            conn.execute(
                'INSERT or IGNORE INTO SnipingMods (UserID) VALUES (?)', (userId,))

            conn.execute(
                'UPDATE SnipingMods SET SmokeBomb = ? WHERE UserID = ?', (1, userId,))

            conn.commit()

        return True

    except Exception as e:
        print(e)
        return False


def set_user_potato(userId, expiration):
    try:
        with sqlite3.connect(api.DATABASE) as conn:
            conn.execute(
                'INSERT INTO HotPotato (Owner, Explosion) VALUES (?, ?)', (userId, expiration,))

            conn.commit()

        return True

    except Exception as e:
        print(e)
        return False


def has_potato(userId):
    try:
        with sqlite3.connect(api.DATABASE) as conn:
            hasPotato = conn.execute(
                'SELECT * FROM HotPotato WHERE Owner = ?', (userId,)).fetchone()

            if hasPotato is None:
                return False

        return True

    except Exception as e:
        print(e)
        return False


def has_smoke_bomb(userId):
    try:
        with sqlite3.connect(api.DATABASE) as conn:
            hasPotato = conn.execute(
                'SELECT * FROM SnipingMods WHERE UserID = ? AND SmokeBomb = 1', (userId,)).fetchone()

            if hasPotato is None:
                return False

        return True

    except Exception as e:
        print(e)
        return False


def use_smoke_bomb(userId):
    try:
        with sqlite3.connect(api.DATABASE) as conn:
            conn.execute(
                'UPDATE SnipingMods SET SmokeBomb = 0 WHERE UserID = ?', (userId,))

            conn.commit()

        expiration = datetime.now() + timedelta(hours=3)

        return set_user_immunity(userId, expiration.timestamp())

    except Exception as e:
        print(e)
        return False


async def check_exploded_potatoes():
    pointDeduction = 3
    now = datetime.now().timestamp()

    async with aiosqlite.connect(api.DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT Guild, Owner FROM HotPotato WHERE Explosion < ?', (now,)) as cursor:
            rows = await cursor.fetchall()

        if len(rows) > 0:
            await db.execute('DELETE FROM HotPotato WHERE Explosion < ?', (now,))

        for row in rows:
            await db.execute('UPDATE Scores SET Points = MAX(0, Points - ?), Deaths = Deaths + 1 WHERE UserID =  ?', (pointDeduction, row['Owner']))

        await db.commit()

        return rows


async def get_expired_immunes():
    now = datetime.now().timestamp()
    async with aiosqlite.connect(api.DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT Guild, UserID FROM SnipingMods WHERE Immunity < ?', (now,)) as cursor:
            rows = await cursor.fetchall()

        if len(rows) > 0:
            await db.execute('UPDATE SnipingMods SET Immunity = ? WHERE Immunity < ?', (None, now, ))
            await db.commit()

        return rows


def get_rewards():
    try:
        with sqlite3.connect(api.DATABASE) as conn:
            rows = conn.execute(
                'SELECT Name, Description FROM CarePackageRwds').fetchall()

            return rows

    except Exception as e:
        print(e)
        return False