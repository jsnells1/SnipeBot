import aiosqlite
import logging

from datetime import datetime

from data import api

log = logging.getLogger(__name__)


async def remove_expired_revenges():
    today = datetime.now().timestamp()

    try:
        async with aiosqlite.connect(api.DATABASE) as db:
            await db.execute('UPDATE Scores SET Revenge = ?, RevengeTime = ? WHERE RevengeTime < ?', (None, None, today))
            await db.commit()

        return True
    except:
        log.exception('Error removing expired revenges')
        return False


async def setSnipes(userId, amt):
    try:
        async with aiosqlite.connect(api.DATABASE) as db:
            await db.execute('UPDATE Scores SET Snipes = ? WHERE UserID = ?', (amt, userId))
            await db.commit()

        return True
    except:
        return False


async def setPoints(userId, amt):
    try:
        async with aiosqlite.connect(api.DATABASE) as db:
            await db.execute('UPDATE Scores SET Points = ? WHERE UserID = ?', (amt, userId))
            await db.commit()

        return True
    except:
        return False


async def setDeaths(userId, amt):

    try:
        async with aiosqlite.connect(api.DATABASE) as db:
            await db.execute('UPDATE Scores SET Deaths = ? WHERE UserID = ?', (amt, userId))
            await db.commit()

        return True
    except:
        return False


async def get_all_respawns():
    async with aiosqlite.connect(api.DATABASE) as db:
        date = datetime.now().timestamp()
        async with db.execute('SELECT Guild, UserID FROM Scores WHERE Respawn < ?', (date,)) as cursor:
            rows = await cursor.fetchall()

            await db.execute('UPDATE Scores SET Respawn = ? WHERE Respawn < ?', (None, date))
            await db.commit()

            return rows


async def update_scores_names(members):
    try:
        for member in members:
            async with aiosqlite.connect(api.DATABASE) as db:
                await db.execute('UPDATE Scores SET Name = ? WHERE UserID = ?', (member.display_name, member.id))
                await db.execute('UPDATE SnipingMods SET Name = ? WHERE UserID < ?', (member.display_name, member.id))
                await db.commit()

        return True

    except:
        return False
