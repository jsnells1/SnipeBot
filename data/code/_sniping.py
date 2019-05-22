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
        except:
            log.exception('Error registering user')
            transaction.rollback()
            return False


def removeUser(userId):
    try:
        user = Scores.select().where(Scores.user_id == 1).limit(1)
        user = user[0] if len(user) > 0 else None

        if user:
            user.delete_instance()

        user = SnipingMods.select().where(SnipingMods.user_id == 1).limit(1)
        user = user[0] if len(user) > 0 else None

        if user:
            user.delete_instance()

        log.info('User deleted with ID: %s', userId)
        return True

    except:
        log.exception('Error removing user')
        return False


def resetRevenge(userID):
    try:
        Scores.update(revenge=None).where(Scores.user_id == userID).execute()
        log.info('Revenge reset for: %s', userID)
        return True
    except:
        log.exception('Error resetting revenge')
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
        log.exception('Error adding points')
        return False


def setSnipes(userId, amt):

    try:
        Scores.update({Scores.snipes: amt}).where(
            Scores.user_id == userId).execute()

        return True
    except:
        log.exception('Error setting snipes')
        return False


def setPoints(userId, amt):

    try:
        Scores.update(points=amt).where(Scores.user_id == userId).execute()
        return True
    except:
        log.exception('Error setting points')
        return False


def setDeaths(userId, amt):

    try:
        Scores.update(deaths=amt).where(Scores.user_id == userId).execute()
        return True
    except:
        log.exception('Error setting deaths')
        return False

# endregion Inserting and Updating


def getUserPoints(userId):
    try:
        conn = sqlite3.connect(code.DATABASE)
        c = conn.cursor()

        c.execute(
            'SELECT Points FROM Scores WHERE UserID = {}'.format(userId))

        row = c.fetchone()

        if row is None:
            return None
        else:
            return row[0]

    except:
        return False

    finally:
        conn.close()


def isRespawning(userID):
    try:
        with sqlite3.connect(code.DATABASE) as conn:
            c = conn.cursor()

            row = c.execute(
                'SELECT Respawn FROM Scores WHERE UserID = {}'.format(userID)).fetchone()

            if row is not None:
                if row[0] is not None:
                    respawn = datetime.fromtimestamp(row[0])

                    return datetime.now() < respawn

            return False
    except Exception as e:
        print(e)
        return False


def getAllUsers():
    try:
        with sqlite3.connect(code.DATABASE) as conn:
            row = conn.execute(
                'SELECT UserID FROM Scores').fetchall()

            return row
    except Exception as e:
        print(e)
        return False


def getRevengeUser(userID):
    try:
        with sqlite3.connect(code.DATABASE) as conn:
            c = conn.cursor()

            row = c.execute(
                'SELECT Revenge FROM Scores WHERE UserID = {}'.format(userID)).fetchone()

            return row[0]

    except:
        return None


def getAllRespawns():
    try:
        with sqlite3.connect(code.DATABASE) as conn:

            date = datetime.now().timestamp()
            rows = conn.execute(
                'SELECT UserID FROM Scores WHERE Respawn < {}'.format(date)).fetchall()

            rows = [x[0] for x in rows]

            conn.execute(
                'UPDATE Scores SET Respawn = ? WHERE Respawn < {}'.format(date), (None,))

            conn.commit()

        return rows
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
