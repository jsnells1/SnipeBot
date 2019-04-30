import logging
import sqlite3
from datetime import datetime, timedelta

import discord

from data import code

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

        with sqlite3.connect(code.DATABASE) as conn:
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


def registerUser(userId):
    commands = [('INSERT INTO Scores (UserID) VALUES ?', (userId,)),
                ('INSERT INTO SnipingMods (UserID) VALUES ?', (userId,))]

    response = _executeStmt_noReturn(commands)

    if response:
        log.info('User registered with ID: %s', userId)

    return response


def removeUser(userId):
    commands = [('DELETE FROM Scores WHERE UserID = ?', (userId,)),
                ('DELETE FROM SnipingMods WHERE UserID = ?', (userId,))]

    response = _executeStmt_noReturn(commands)

    if response:
        log.info('User deleted with ID: %s', userId)

    return response


def resetRevenge(userID):

    commands = [
        ('UPDATE Scores SET Revenge = ? WHERE UserId = ?', (None, userID,))]

    response = _executeStmt_noReturn(commands)

    if response:
        log.info('Revenge reset for: %s', userID)

    return response


def removeExpiredRevenges():
    today = datetime.now().timestamp()

    commands = [
        ('UPDATE Scores SET Revenge = ?, RevengeTime = ? WHERE RevengeTime < ?', (None, None, today,))]

    return _executeStmt_noReturn(commands)


def setRespawn(userID, conn):
    RESPAWN_TIME = 2

    date = datetime.now() + timedelta(hours=RESPAWN_TIME)
    commands = [('UPDATE Scores SET Respawn = ? WHERE UserID = ?',
                 (date.timestamp(), userID))]

    return _executeStmt_noReturn(commands)


def addPoints(userId, points):
    commands = [
        ('UPDATE Scores SET Points = Points + ? WHERE UserID = ?', (points, userId))]

    return _executeStmt_noReturn(commands)

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


def getRevengeUser(userID):
    try:
        with sqlite3.connect(code.DATABASE) as conn:
            c = conn.cursor()

            row = c.execute(
                'SELECT Revenge FROM Scores WHERE UserID = {}'.format(userID)).fetchone()

            return row[0]

    except Exception as e:
        print(e)
        return False


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

            c.execute(
                'INSERT OR IGNORE INTO Scores (UserID) VALUES ({})'.format(winner))

            c.execute(
                'INSERT OR IGNORE INTO Scores (UserID) VALUES ({})'.format(loser))

            c.execute(
                'INSERT OR IGNORE INTO SnipingMods (UserID) VALUES ({})'.format(winner))

            c.execute(
                'INSERT OR IGNORE INTO SnipingMods (UserID) VALUES ({})'.format(loser))

            c.execute(
                'UPDATE Scores SET Snipes = Snipes + 1, Points = Points + 1 WHERE UserID = {}'.format(winner))
            c.execute(
                'UPDATE Scores SET Deaths = Deaths + 1, Killstreak = 0 WHERE UserID = {}'.format(loser))

            c.execute(
                'UPDATE Scores SET Respawn = NULL WHERE UserID = {}'.format(winner))

            date = datetime.now() + timedelta(hours=3, minutes=30)

            c.execute(
                'UPDATE Scores SET Revenge = {}, RevengeTime = {} WHERE UserID = {}'.format(winner, date.timestamp(), loser))

            if not setRespawn(loser, conn):
                return False

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


def setSnipes(userId, amt):
    try:
        conn = sqlite3.connect(code.DATABASE)
        c = conn.cursor()

        c.execute(
            'UPDATE Scores SET Snipes = {} WHERE UserID = {}'.format(amt, userId))
        conn.commit()

        return True

    except:
        return False

    finally:
        conn.close()


def setPoints(userId, amt):
    try:
        conn = sqlite3.connect(code.DATABASE)
        c = conn.cursor()

        c.execute(
            'UPDATE Scores SET Points = {} WHERE UserID = {}'.format(amt, userId))
        conn.commit()

        return True

    except:
        return False

    finally:
        conn.close()


def setDeaths(userId, amt):
    try:
        conn = sqlite3.connect(code.DATABASE)
        c = conn.cursor()

        c.execute(
            'UPDATE Scores SET Deaths = {} WHERE UserID = {}'.format(amt, userId))
        conn.commit()

        return True

    except:
        return False

    finally:
        conn.close()


def update_scores_names(members):
    try:
        with sqlite3.connect(code.DATABASE) as conn:

            for member in members:
                conn.execute('UPDATE Scores SET Name = ? WHERE UserID = ?',
                             (member.display_name, member.id))

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
        return False


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
