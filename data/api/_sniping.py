import aiosqlite
import logging
import sqlite3
from datetime import datetime, timedelta
from peewee import fn

import discord

from data import api
from data.models.data_models import Scores, SnipingMods, database

log = logging.getLogger(__name__)


def removeUser(userId):
    try:
        user = Scores.get(userId)
        user.delete_instance()

        log.info('User deleted with ID: %s', userId)
    except Scores.DoesNotExist:
        pass
    except:
        log.exception('Error removing user_id: %s', userId)
        return False

    try:
        user = SnipingMods.get(userId)
        user.delete_instance()

        log.info('User deleted with ID: %s', userId)
        return True

    except SnipingMods.DoesNotExist:
        return True
    except:
        log.exception('Error removing user_id: %s', userId)
        return False


def remove_expired_revenges():
    today = datetime.now().timestamp()

    try:
        Scores.update(revenge=None, revenge_time=None).where(
            Scores.revenge_time < today).execute()
        return True
    except:
        log.exception('Error removing expired revenges')
        return False


def addPoints(userId, amt):
    try:
        Scores.update({Scores.points: Scores.points + amt}
                      ).where(Scores.user_id == userId).execute()
        return True
    except:
        log.exception('Error adding points (%s) for user_id: %s', amt, userId)
        return False


def setSnipes(userId, amt):

    try:
        Scores.update({Scores.snipes: amt}).where(
            Scores.user_id == userId).execute()

        return True
    except:
        log.exception('Error setting snipes (%s) for user_id: %s', amt, userId)
        return False


def setPoints(userId, amt):

    try:
        Scores.update(points=amt).where(Scores.user_id == userId).execute()
        return True
    except:
        log.exception('Error setting points (%s) for user_id: %s', amt, userId)
        return False


def setDeaths(userId, amt):

    try:
        Scores.update(deaths=amt).where(Scores.user_id == userId).execute()
        return True
    except:
        log.exception('Error setting deaths (%s) for user_id: %s', amt, userId)
        return False


def isRespawning(userId):
    try:
        user = Scores.get(user_id=userId)

        if user.respawn is None:
            return False

        return datetime.now().timestamp() < user.respawn

    except Scores.DoesNotExist:
        return False
    except:
        log.exception('Error checking for respawn for user_id: %s', userId)
        return False


def getAllUsers():
    try:
        users = Scores.select(Scores.user_id)
        return [user.user_id for user in users]
    except:
        log.exception('Error retrieving users')
        return []


async def get_all_respawns():
    async with aiosqlite.connect(api.DATABASE) as db:
        date = datetime.now().timestamp()
        async with db.execute('SELECT Guild, UserID FROM Scores WHERE Respawn < ?', (date,)) as cursor:
            rows = await cursor.fetchall()

            await db.execute('UPDATE Scores SET Respawn = ? WHERE Respawn < ?', (None, date))
            await db.commit()

            return rows


def update_scores_names(members):
    try:
        params = [(member.display_name, member.id) for member in members]

        for param in params:
            Scores.update(name=param[0]).where(
                Scores.user_id == param[1]).execute()
            SnipingMods.update(name=param[0]).where(
                SnipingMods.user_id == param[1]).execute()

        return True

    except:
        return False
