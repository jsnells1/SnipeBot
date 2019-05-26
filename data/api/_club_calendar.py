import logging
import sqlite3
from datetime import datetime, timedelta

from data import api

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

        with sqlite3.connect(api.DATABASE) as conn:
            for cmd in cmds:
                stmt = cmd[0]
                params = cmd[1]

                conn.execute(stmt, params)

            conn.commit()

        return True

    except Exception as e:
        log.critical('Error executing statement(s): %s', cmds, exc_info=e)
        return False


def insert_event(date, description, repeating):
    commands = [
        ('INSERT INTO Calendar (Date, Description, Repeating) VALUES (?, ?, ?)', (date, description, repeating))]

    return _executeStmt_noReturn(commands)


def get_events(start, end):

    try:
        with sqlite3.connect(api.DATABASE) as conn:
            conn.row_factory = sqlite3.Row

            r = conn.execute(
                'SELECT Date, Description, Repeating FROM Calendar WHERE Date >= ? AND Date <= ?', (start, end)).fetchall()

            return r
    except:
        return None