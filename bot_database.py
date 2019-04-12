import sqlite3


def getUserPoints(userId):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('SELECT Snipes FROM Scores WHERE UserID = {}'.format(userId))

    row = c.fetchone()

    if row is None:
        return None
    else:
        return row[0]


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
