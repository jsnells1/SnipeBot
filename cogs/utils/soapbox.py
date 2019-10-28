import aiosqlite
from datetime import datetime

from cogs.utils.db import Database


class SoapboxEntry:
    def __init__(self, id=None, guild=None, name=None, date=None, topic=None):
        self.id = id
        self.guild = guild
        self.name = name
        self.date = date
        self.topic = topic

    def __str__(self):
        date = self.date.strftime('%m/%d')

        return f'id: {self.id}\nName: {self.name}\nDate: {date}\nTopic: {self.topic}'

    def __repr__(self):
        return str(self)

    @classmethod
    def from_dict(cls, dictionary: dict):
        instance = cls()

        for key, value in dictionary.items():
            setattr(instance, key, value)

        return instance

    @classmethod
    async def from_database(cls, id: int):
        instance = cls()
        instance.id = id

        async with aiosqlite.connect(Database.connection_string()) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM Soapbox WHERE id = ?', (id,)) as cursor:
                row = await cursor.fetchone()

        if row is None:
            return None

        instance.name = row['Presenter']
        instance.date = datetime.fromtimestamp(row['Date'])
        instance.topic = row['Topic']
        instance.guild = row['Guild']

        return instance

    @classmethod
    async def get_all(cls, guild):
        async with aiosqlite.connect(Database.connection_string()) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM Soapbox WHERE Guild = ? ORDER BY Date ASC', (guild,)) as cursor:
                rows = await cursor.fetchall()

        soapbox_entries = []

        for row in rows:
            soapbox_entry = cls(id=row['ID'], name=row['Presenter'], date=datetime.fromtimestamp(
                row['Date']), topic=row['Topic'])

            soapbox_entries.append(soapbox_entry)

        return soapbox_entries

    def update(self, soapbox):
        self.name = self.name if soapbox.name is None else soapbox.name
        self.date = self.date if soapbox.date is None else soapbox.date
        self.topic = self.topic if soapbox.topic is None else soapbox.topic

    async def commit_update(self):
        async with aiosqlite.connect(Database.connection_string()) as db:
            await db.execute('UPDATE Soapbox SET Presenter = ?, date = ?, topic = ? WHERE id = ? AND Guild = ?', (self.name, self.date.timestamp(), self.topic, self.id, self.guild))
            await db.commit()

    async def commit_delete(self):
        async with aiosqlite.connect(Database.connection_string()) as db:
            await db.execute('DELETE FROM Soapbox WHERE id = ?', (self.id,))
            await db.commit()

    async def commit_new(self):
        async with aiosqlite.connect(Database.connection_string()) as db:
            await db.execute('INSERT INTO Soapbox (Guild, Presenter, Topic, Date) VALUES (?, ?, ?, ?)', (self.guild, self.name, self.topic, self.date.timestamp()))
            await db.commit()
