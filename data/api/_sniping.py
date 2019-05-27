import logging
import sqlite3
from datetime import datetime, timedelta
from peewee import fn

import discord

from data import api
from data.models.data_models import Scores, SnipingMods, database

log = logging.getLogger(__name__)


def registerUser(userId):
    with database.atomic() as transaction:
        try:
            Scores.insert(user_id=userId).on_conflict_ignore().execute()
            SnipingMods.insert(user_id=userId).on_conflict_ignore().execute()

            log.info('User registered with ID: %s', userId)

            return True
        except:
            log.exception('Error registering user_id: %s', userId)
            transaction.rollback()
            return False


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


def resetRevenge(userId):
    try:
        Scores.get(userId).update(revenge=None, revenge_time=None).execute()
        log.info('Revenge reset for: %s', userId)
        return True
    except Scores.DoesNotExist:
        return True
    except:
        log.exception('Error resetting revenge for user_id: %s', userId)
        return False


def removeExpiredRevenges():
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


def getUserPoints(userId):
    try:
        query = Scores.select(Scores.points).where(
            Scores.user_id == userId).limit(1).namedtuples()

        if len(query) > 0:
            return query[0].points

        return None
    except:
        log.exception('Error getting points for userid: %s', userId)
        return None


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


def getRevengeUser(userId):
    try:
        return Scores.get(userId).revenge
    except Scores.DoesNotExist:
        return None
    except:
        log.exception('Error getting revenge user for user_id: %s', userId)
        return None


def getAllRespawns():
    try:
        date = datetime.now().timestamp()

        respawns = Scores.select(Scores.user_id).where(
            Scores.respawn < date).namedtuples().execute()

        if len(respawns) == 0:
            return []

        respawns = [x.user_id for x in respawns]

        Scores.update({Scores.respawn: None}).where(
            Scores.respawn < date).execute()

        return respawns
    except:
        return False

# TODO Convert to peewee


def addSnipe(winner, loser):
    try:
        with sqlite3.connect(api.DATABASE) as conn:
            c = conn.cursor()

            # Ensure both the sniper and snipee are inserted into the database
            c.execute(
                'INSERT OR IGNORE INTO Scores (UserID) VALUES ({}), ({})'.format(winner, loser))

            c.execute(
                'INSERT OR IGNORE INTO SnipingMods (UserID) VALUES ({}), ({})'.format(winner, loser))

            # For the sniper, add 1 to their snipes and points and remove their respawn
            c.execute(
                'UPDATE Scores SET Snipes = Snipes + 1, Points = Points + 1, Respawn = NULL WHERE UserID = {}'.format(winner))

            # For the loser, add 1 to deaths, reset their killstreak, set their Respawn to 2 hours, and set the revenge id
            respawn = datetime.now() + timedelta(hours=2)
            revenge = datetime.now() + timedelta(hours=3, minutes=30)
            c.execute('UPDATE Scores SET Deaths = Deaths + 1, Killstreak = 0, Respawn = ?, Revenge = ?, RevengeTime = ? WHERE UserID = ?',
                      (respawn.timestamp(), winner, revenge.timestamp(), loser))

            conn.commit()

        return True

    except:
        return False


def getLeaderboard():
    try:
        rows = Scores.select(Scores.user_id, Scores.points, Scores.snipes, Scores.deaths).order_by(
            Scores.points.desc(), Scores.snipes.desc(), Scores.deaths).limit(10).namedtuples().execute()

        return rows
    except:
        return False


def getLeader():
    leaderboard = getLeaderboard()

    if not leaderboard or len(leaderboard) == 0:
        return None

    return leaderboard[0].user_id


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


def isImmune(userId):
    try:
        now = datetime.now().timestamp()
        user = SnipingMods.get(userId)

        return user.immunity > now
    except:
        log.exception('Error checking for immunity for user_id: %s', userId)
        return False


def get_multiplier(userId):
    try:
        now = datetime.now().timestamp()

        SnipingMods.update(multiplier=None, multi_expiration=None).where(
            (SnipingMods.multi_expiration == None) | (SnipingMods.multi_expiration < now)).execute()

        multi = SnipingMods.get(userId).multiplier

        if multi is None:
            return 1

        return multi
    except SnipingMods.DoesNotExist:
        return 1
    except:
        return -1


def update_killstreak(userId, kills):
    try:
        user = Scores.get(userId)
        user.killstreak += kills
        user.killstreak_record = max(user.killstreak, user.killstreak_record)
        user.save()

        return user.killstreak
    except Scores.DoesNotExist:
        return 0
    except:
        log.exception(
            'Error updating killstreak for %s with %s kills', userId, kills)
        return False


def get_highest_killstreak():
    try:
        # where(True) is unneeded but included for pylint to be happy
        record = Scores.select(Scores.user_id, Scores.killstreak_record).where(
            True).order_by(Scores.killstreak_record.desc()).namedtuples().limit(1).execute()

        if len(record) == 0:
            return None

        return record[0]

    except:
        log.exception('Error getting highest killstreak')
        return None
