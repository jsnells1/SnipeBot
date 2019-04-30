import logging
import sqlite3

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


def createSoapbox(name, timestamp, topic):
    commands = [
        ('INSERT INTO Soapbox (Presenter, Topic, Date) VALUES (?, ?, ?)', (name, topic, timestamp))]

    return _executeStmt_noReturn(commands)


def deleteSoapboxEntry(id):
    commands = [('DELETE FROM Soapbox WHERE id = ?', (id,))]

    return _executeStmt_noReturn(commands)


def updateSoapboxTopic(id, name, date, topic):

    commands = [('UPDATE Soapbox SET Presenter = ?, date = ?, topic = ? WHERE id = ?',
                 (name, date, topic, id))]

    return _executeStmt_noReturn(commands)

# endregion Inserting and Updating


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
