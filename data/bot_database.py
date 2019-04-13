import sqlite3


def getUserPoints(userId):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute('SELECT Snipes FROM Scores WHERE UserID = {}'.format(userId))

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
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute('INSERT INTO Scores (UserID) VALUES ({})'.format(userId))
        conn.commit()

        return True

    except:
        return False

    finally:
        conn.close()


def addSnipe(winner, loser):
    try:
        conn = sqlite3.connect('database.db')
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
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        rows = c.execute('SELECT * FROM Scores LIMIT 10').fetchall()

        return rows

    except:
        return False

    finally:
        conn.close()


def removeUser(userId):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute('DELETE FROM Scores WHERE UserID = {}'.format(userId))
        conn.commit()

        return True

    except:
        return False

    finally:
        conn.close()


def setSnipes(userId, amt):
    try:
        conn = sqlite3.connect('database.db')
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
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute(
            'UPDATE Scores SET Deaths = {} WHERE UserID = {}'.format(amt, userId))
        conn.commit()

        return True

    except:
        return False

    finally:
        conn.close()
