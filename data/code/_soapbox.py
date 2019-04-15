import sqlite3

from data import code

def createSoapbox(name, timestamp, topic):
    try:
        with sqlite3.connect(code.DATABASE) as conn:
            conn.execute(
                'INSERT INTO Soapbox (Presenter, Topic, Date) VALUES (\'{}\', \'{}\', {})'.format(name, topic, timestamp))
            conn.commit()
            return True
    except:
        return False


def getSoapboxSchedule():
    try:
        with sqlite3.connect(code.DATABASE) as conn:
            rows = conn.execute(
                'SELECT * FROM Soapbox ORDER BY Date ASC').fetchall()
            conn.commit()
            return rows
    except:
        return False


def getSoapboxEntry(id):
    try:
        with sqlite3.connect(code.DATABASE) as conn:
            row = conn.execute(
                'SELECT * FROM Soapbox WHERE id = {}'.format(id))

            info = list(map(lambda x: x[0], row.description))
            row = row.fetchone()

            return info, row
    except:
        return False


def deleteSoapboxEntry(id):
    try:
        with sqlite3.connect(code.DATABASE) as conn:
            conn.execute('DELETE FROM Soapbox WHERE id = {}'.format(id))

            return True
    except:
        return False


def updateSoapboxTopic(id, name, date, topic):
    try:
        with sqlite3.connect(code.DATABASE) as conn:
            conn.execute('UPDATE Soapbox SET Presenter = \'{}\', date = {}, topic = \'{}\' WHERE id = {}'.format(
                name, date, topic, id))

            return True
    except:
        return False
