import aiosqlite
from datetime import datetime

import data.api._soapbox as soapbox


class SoapboxEntry:
    def __init__(self, id=None, name=None, date=None, topic=None):
        self.id = id
        self.name = name
        self.date = date
        self.topic = topic

    def __str__(self):

        date = self.date.strftime('%m/%d')

        return f'id: {self.id}\nName: {self.name}\nDate: {date}\nTopic: {self.topic}'

    def __repr__(self):
        return self.__str__()

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

        row = await soapbox.get_soapbox(id)

        if row is None:
            raise LookupError(f'Soapbox not found with id={id}')

        instance.name = row['Presenter']
        instance.date = datetime.fromtimestamp(row['Date'])
        instance.topic = row['Topic']

        return instance

    @classmethod
    async def get_all(cls):
        rows = await soapbox.get_schedule()

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
        await soapbox.update_soapbox(self.id, self.name, self.date.timestamp(), self.topic)

    async def commit_delete(self):
        await soapbox.delete_soapbox(self.id)

    async def commit_new(self):
        await soapbox.insert_soapbox(self.name, self.date, self.topic)
