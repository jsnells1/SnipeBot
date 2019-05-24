import logging
import sqlite3
from datetime import datetime, timedelta

import discord

from data import code
from data.models.data_models import *

log = logging.getLogger(__name__)


def registerUser(userId):
    with database.atomic() as transaction:
        try:
            Scores.insert(user_id=userId).on_conflict_ignore().execute()
            SnipingMods.insert(user_id=userId).on_conflict_ignore().execute()

            log.info('User registered with ID: %s', userId)

            return True
        except Exception as e:
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
        Scores.get(userId).update(revenge=None).execute()
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

# endregion Inserting and Updating


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
        query = Scores.select(Scores.respawn).where(
            Scores.user_id == userId).limit(1).namedtuples()

        if len(query) < 1:
            return False

        return datetime.now().timestamp() < query[0].respawn

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


def addSnipe(winner, loser):
    try:
        with sqlite3.connect(code.DATABASE) as conn:
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
        with sqlite3.connect(code.DATABASE) as conn:

            rows = conn.execute(
                'SELECT UserID, Points, Snipes, Deaths FROM Scores ORDER BY Points DESC, Snipes DESC, Deaths ASC LIMIT 10').fetchall()

            return rows

    except Exception as e:
        print(e)
        return False


def getLeader():
    try:
        with sqlite3.connect(code.DATABASE) as conn:

            row = conn.execute(
                'SELECT UserID FROM Scores ORDER BY Points DESC, Snipes DESC, Deaths ASC LIMIT 1').fetchone()

            return row[0]

    except Exception as e:
        print(e)
        return False


def update_scores_names(members):
    try:
        params = [(member.display_name, member.id) for member in members]

        with sqlite3.connect(code.DATABASE) as conn:

            conn.executemany('UPDATE SnipingMods SET Name = ? WHERE UserID = ?',
                             params)
            conn.executemany('UPDATE Scores SET Name = ? WHERE UserID = ?',
                             params)

            conn.commit()

        return True

    except:
        return False


def isImmune(userId):
    try:
        with sqlite3.connect(code.DATABASE) as conn:

            now = datetime.now().timestamp()

            immune = conn.execute(
                'SELECT Immunity FROM SnipingMods WHERE UserID = ? and Immunity > ?', (userId, now)).fetchone()

            conn.commit()

            if immune is None:
                return False

        return True

    except:
        return False


def get_multiplier(userId):
    try:
        with sqlite3.connect(code.DATABASE) as conn:

            now = datetime.now().timestamp()

            conn.execute(
                'UPDATE SnipingMods SET Multiplier = ?, MultiExpiration = ? WHERE MultiExpiration < ?', (None, None, now))
            multi = conn.execute(
                'SELECT Multiplier FROM SnipingMods WHERE UserID = ? AND MultiExpiration > ?', (userId, now)).fetchone()

            conn.commit()

            if multi is None:
                return 1

            return int(multi[0])

    except:
        return -1


def update_killstreak(userId, kills):
    try:
        with sqlite3.connect(code.DATABASE) as conn:

            conn.execute(
                'UPDATE Scores SET Killstreak = Killstreak + ?, KillstreakRecord = MAX(KillstreakRecord, Killstreak + ?) WHERE UserID = ?', (kills, kills, userId))

            conn.commit()

            killstreak = conn.execute(
                'SELECT Killstreak FROM Scores WHERE UserID = ?', (userId,)).fetchone()

            if killstreak is None:
                return 0

            return int(killstreak[0])

    except Exception as e:
        print(e)
        return False


def get_highest_killstreak():
    try:
        with sqlite3.connect(code.DATABASE) as conn:

            killstreak = conn.execute(
                'SELECT UserID, KillstreakRecord FROM Scores ORDER BY KillstreakRecord DESC LIMIT 1').fetchone()

            if killstreak is None:
                return None

            return killstreak

    except Exception as e:
        print(e)
        return False
