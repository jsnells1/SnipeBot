import sqlite3
from datetime import datetime, timedelta

import discord

from data import code


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


def registerUser(userId):
    try:
        conn = sqlite3.connect(code.DATABASE)
        c = conn.cursor()

        c.execute('INSERT INTO Scores (UserID) VALUES ({})'.format(userId))
        conn.commit()

        return True

    except:
        return False

    finally:
        conn.close()


def removeUser(userId):
    try:
        with sqlite3.connect(code.DATABASE) as conn:
            c = conn.cursor()

            c.execute('DELETE FROM Scores WHERE UserID = {}'.format(userId))
            conn.commit()

        return True

    except:
        return False


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


def resetRevenge(userID):
    try:
        with sqlite3.connect(code.DATABASE) as conn:

            conn.execute(
                'UPDATE Scores SET Revenge = ? WHERE UserId = ?', (None, userID,))

    except Exception as e:
        print(e)
        return False


def removeExpiredRevenges():
    try:
        today = datetime.now().timestamp()
        with sqlite3.connect(code.DATABASE) as conn:

            conn.execute(
                'UPDATE Scores SET Revenge = ?, RevengeTime = ? WHERE RevengeTime < ?', (None, None, today,))

    except Exception as e:
        print(e)
        return False


def setRespawn(userID, conn):
    try:

        respawnTime = 2

        date = datetime.now() + timedelta(hours=respawnTime)
        conn.execute('UPDATE Scores SET Respawn = {} WHERE UserID = {}'.format(
            date.timestamp(), userID))

        return True
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


def addPoints(userId, points):
    try:
        with sqlite3.connect(code.DATABASE) as conn:
            conn.execute(
                'UPDATE Scores SET Points = Points + ? WHERE UserID = ?', (points, userId))

            conn.commit()

        return True

    except Exception as e:
        print(e)
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
                'UPDATE Scores SET Snipes = Snipes + 1, Points = Points + 1 WHERE UserID = {}'.format(winner))
            c.execute(
                'UPDATE Scores SET Deaths = Deaths + 1 WHERE UserID = {}'.format(loser))

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


def set_carepackage(keyword, expiration, hint):
    try:
        with sqlite3.connect(code.DATABASE) as conn:

            conn.execute(
                'UPDATE CarePackage SET Key = ?, Expiration = ?, Hint = ?', (keyword, expiration, hint,))
            conn.commit()

        return True

    except Exception as e:
        print(e)
        return False
