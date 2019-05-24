import pytest
#from peewee import SqliteDatabase
from data.models.data_models import database, Calendar, CarePackage, CarePackageRwds, HotPotato, Scores, SnipingMods, Soapbox, SqliteSequence

import data.code as Database

OWNER_ID = 273946109896818701


def setup_module(module):
    database.init(':memory:')
    database.create_tables([Calendar, CarePackage, CarePackageRwds,
                            HotPotato, Scores, SnipingMods, Soapbox])


def teardown_function():
    # Empty Scores and SnipingMods tables after each test
    Scores.delete().where(True).execute()
    SnipingMods.delete().where(True).execute()


def test_add__remove_user():
    assert Database.registerUser(1)
    Scores.get(1)

    assert Database.removeUser(1)

    with pytest.raises(Scores.DoesNotExist):
        Scores.get(1)


def test_reset_revenge():
    Scores.create(user_id=1, revenge=1)
    Database.resetRevenge(1)

    assert Scores.get(1).revenge == None


def test_add_points():
    Scores.create(user_id=1)

    assert Database.addPoints(1, 5)
    assert Database.getUserPoints(1) == 5


def test_set_points_snipes_deaths():
    Scores.create(user_id=1)

    assert Database.setPoints(1, 5)
    assert Database.setSnipes(1, 5)
    assert Database.setDeaths(1, 5)

    user = Scores.get(1)

    assert user.points == 5
    assert user.snipes == 5
    assert user.deaths == 5


def test_respawning():
    Scores.create(user_id=1, respawn=1)
    Scores.create(user_id=2, respawn=99999999999)
    Scores.create(user_id=3, respawn=5)
    Scores.create(user_id=4, respawn=99999999999)

    assert Database.isRespawning(1) == False
    assert Database.isRespawning(2)

    respawns = Database.getAllRespawns()

    assert len(respawns) == 2
    assert 1 in respawns
    assert 3 in respawns

    assert Scores.get(1).respawn == None
    assert Scores.get(3).respawn == None

    assert Database.getAllRespawns() == []
    