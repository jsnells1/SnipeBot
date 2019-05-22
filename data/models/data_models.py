from peewee import SqliteDatabase, Model, SQL
from peewee import FloatField, TextField, BooleanField, AutoField, IntegerField, BareField

database = SqliteDatabase(None)

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Calendar(BaseModel):
    date = FloatField(column_name='Date')
    description = TextField(column_name='Description', null=True)
    repeating = BooleanField(column_name='Repeating', constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name = 'Calendar'

class CarePackage(BaseModel):
    expiration = FloatField(column_name='Expiration', null=True)
    hint = TextField(column_name='Hint', null=True)
    key = TextField(column_name='Key', null=True, primary_key=True)

    class Meta:
        table_name = 'CarePackage'

class CarePackageRwds(BaseModel):
    description = TextField(column_name='Description', null=True)
    name = TextField(column_name='Name')

    class Meta:
        table_name = 'CarePackageRwds'

class HotPotato(BaseModel):
    explosion = IntegerField(column_name='Explosion', null=True)
    id = AutoField(column_name='Id', null=True)
    owner = IntegerField(column_name='Owner', null=True)

    class Meta:
        table_name = 'HotPotato'

class Scores(BaseModel):
    deaths = IntegerField(column_name='Deaths', constraints=[SQL("DEFAULT 0")])
    killstreak = IntegerField(column_name='Killstreak', constraints=[SQL("DEFAULT 0")])
    killstreak_record = IntegerField(column_name='KillstreakRecord', constraints=[SQL("DEFAULT 0")])
    name = TextField(column_name='Name', null=True)
    points = IntegerField(column_name='Points', constraints=[SQL("DEFAULT 0")])
    respawn = FloatField(column_name='Respawn', null=True)
    revenge = IntegerField(column_name='Revenge', null=True)
    revenge_time = FloatField(column_name='RevengeTime', null=True)
    snipes = IntegerField(column_name='Snipes', constraints=[SQL("DEFAULT 0")])
    user_id = AutoField(column_name='UserID')

    class Meta:
        table_name = 'Scores'

class SnipingMods(BaseModel):
    immunity = FloatField(column_name='Immunity', null=True)
    multi_expiration = FloatField(column_name='MultiExpiration', null=True)
    multiplier = IntegerField(column_name='Multiplier', null=True)
    name = TextField(column_name='Name', null=True)
    smoke_bomb = IntegerField(column_name='SmokeBomb', constraints=[SQL("DEFAULT 0")])
    user_id = AutoField(column_name='UserID')

    class Meta:
        table_name = 'SnipingMods'

class Soapbox(BaseModel):
    date = FloatField(column_name='Date', null=True)
    presenter = TextField(column_name='Presenter', null=True)
    topic = TextField(column_name='Topic', null=True)

    class Meta:
        table_name = 'Soapbox'

class SqliteSequence(BaseModel):
    name = BareField(null=True)
    seq = BareField(null=True)

    class Meta:
        table_name = 'sqlite_sequence'
        primary_key = False

