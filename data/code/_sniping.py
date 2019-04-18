import sqlite3
from datetime import datetime, timedelta

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
                'SELECT * FROM Scores ORDER BY Points DESC, Snipes DESC, Deaths ASC LIMIT 10').fetchall()

            return rows

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
