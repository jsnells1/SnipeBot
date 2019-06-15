import logging
import sqlite3
import aiosqlite
from datetime import datetime

from data import api

log = logging.getLogger(__name__)


async def insert_soapbox(name, date: datetime, topic):
    async with aiosqlite.connect(api.DATABASE) as db:
        await db.execute('INSERT INTO Soapbox (Presenter, Topic, Date) VALUES (?, ?, ?)', (name, topic, date.timestamp()))
        await db.commit()


async def delete_soapbox(id):
    async with aiosqlite.connect(api.DATABASE) as db:
        await db.execute('DELETE FROM Soapbox WHERE id = ?', (id,))
        await db.commit()


async def update_soapbox(id, name, date, topic):
    async with aiosqlite.connect(api.DATABASE) as db:
        await db.execute('UPDATE Soapbox SET Presenter = ?, date = ?, topic = ? WHERE id = ?', (name, date, topic, id))
        await db.commit()


async def get_schedule():
    async with aiosqlite.connect(api.DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM Soapbox ORDER BY Date ASC') as cursor:
            rows = await cursor.fetchall()

            return rows


async def get_soapbox(id):
    async with aiosqlite.connect(api.DATABASE) as db:

        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM Soapbox WHERE id = ?', (id,)) as cursor:
            row = await cursor.fetchone()

            return row
