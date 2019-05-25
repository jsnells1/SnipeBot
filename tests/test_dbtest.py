import pytest
# from peewee import SqliteDatabase
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


def test_revenge():
    Scores.create(user_id=1, revenge=123, revenge_time=1)

    assert Database.getRevengeUser(1) == 123

    assert Database.resetRevenge(1)

    assert Database.getRevengeUser(1) == None
    assert Scores.get(1).revenge_time == None
    assert Database.getRevengeUser(2) == None


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


def test_leaderboard():

    assert Database.getLeader() == None

    Scores.create(user_id=1, points=5, snipes=4)
    Scores.create(user_id=2, points=5, snipes=4, deaths=1)
    Scores.create(user_id=3, points=4)
    Scores.create(user_id=4, points=3)

    rows = Database.getLeaderboard()

    assert rows != False

    assert rows[0].user_id == 1
    assert rows[1].user_id == 2
    assert rows[2].user_id == 3
    assert rows[3].user_id == 4

    assert Database.getLeader() == 1


def test_immune():
    assert Database.isImmune(1) == False

    SnipingMods.create(user_id=2, immunity=1)
    assert Database.isImmune(2) == False

    SnipingMods.create(user_id=3, immunity=9999999999)
    assert Database.isImmune(3)


def test_multiplier_killstreak():
    assert Database.get_multiplier(1) == 1

    SnipingMods.create(user_id=1, multiplier=3)
    SnipingMods.create(user_id=2, multiplier=3, multi_expiration=1)
    SnipingMods.create(user_id=3, multiplier=3, multi_expiration=99999999999)

    assert Database.get_multiplier(1) == 1
    assert Database.get_multiplier(2) == 1
    assert Database.get_multiplier(3) == 3
