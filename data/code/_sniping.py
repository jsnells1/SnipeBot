import sqlite3

from data import code

def getUserPoints(userId):
    try:
        conn = sqlite3.connect(code.DATABASE)
        c = conn.cursor()

        c.execute(
            'SELECT Snipes FROM Scores WHERE UserID = {}'.format(userId))

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


def addSnipe(winner, loser):
    try:
        conn = sqlite3.connect(code.DATABASE)
        c = conn.cursor()

        c.execute(
            'INSERT OR IGNORE INTO Scores (UserID) VALUES ({})'.format(winner))

        c.execute(
            'INSERT OR IGNORE INTO Scores (UserID) VALUES ({})'.format(loser))

        c.execute(
            'UPDATE Scores SET Snipes = Snipes + 1 WHERE UserID = {}'.format(winner))
        c.execute(
            'UPDATE Scores SET Deaths = Deaths + 1 WHERE UserID = {}'.format(loser))

        conn.commit()

        return True

    except:
        return False

    finally:
        conn.close()


def getLeaderboard():

    try:
        with sqlite3.connect(code.DATABASE) as conn:

            rows = conn.execute(
                'SELECT * FROM Scores ORDER BY Snipes DESC, Deaths ASC LIMIT 10').fetchall()

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
