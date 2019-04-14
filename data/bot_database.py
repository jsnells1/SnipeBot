import sqlite3
from enum import Enum


class Environment (Enum):
    dev = 1
    live = 2


class BotDatabase():

    LIVE_DATABASE = './data/database.db'
    DEV_DATABASE = './data/dev_database.db'

    DATABASE = DEV_DATABASE

    def __init__(self):
        pass

    def switchDatabase(self, env):

        if env == Environment.live:
            BotDatabase.DATABASE = BotDatabase.LIVE_DATABASE
            return True
        elif env == Environment.dev:
            BotDatabase.DATABASE = BotDatabase.DEV_DATABASE
            return True

        return False

    def getUserPoints(self, userId):
        try:
            conn = sqlite3.connect(BotDatabase.DATABASE)
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

    def registerUser(self, userId):
        try:
            conn = sqlite3.connect(BotDatabase.DATABASE)
            c = conn.cursor()

            c.execute('INSERT INTO Scores (UserID) VALUES ({})'.format(userId))
            conn.commit()

            return True

        except:
            return False

        finally:
            conn.close()

    def addSnipe(self, winner, loser):
        try:
            conn = sqlite3.connect(BotDatabase.DATABASE)
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

    def getLeaderboard(self):

        try:
            conn = sqlite3.connect(BotDatabase.DATABASE)
            c = conn.cursor()

            rows = c.execute(
                'SELECT * FROM Scores ORDER BY Snipes DESC, Deaths ASC LIMIT 10').fetchall()

            return rows

        except:
            return False

        finally:
            conn.close()

    def removeUser(self, userId):
        try:
            conn = sqlite3.connect(BotDatabase.DATABASE)
            c = conn.cursor()

            c.execute('DELETE FROM Scores WHERE UserID = {}'.format(userId))
            conn.commit()

            return True

        except:
            return False

        finally:
            conn.close()

    def setSnipes(self, userId, amt):
        try:
            conn = sqlite3.connect(BotDatabase.DATABASE)
            c = conn.cursor()

            c.execute(
                'UPDATE Scores SET Snipes = {} WHERE UserID = {}'.format(amt, userId))
            conn.commit()

            return True

        except:
            return False

        finally:
            conn.close()

    def setDeaths(self, userId, amt):
        try:
            conn = sqlite3.connect(BotDatabase.DATABASE)
            c = conn.cursor()

            c.execute(
                'UPDATE Scores SET Deaths = {} WHERE UserID = {}'.format(amt, userId))
            conn.commit()

            return True

        except:
            return False

        finally:
            conn.close()
