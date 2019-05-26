import pytest
from data.models.data_models import database, Calendar, CarePackage, CarePackageRwds, HotPotato, Scores, SnipingMods, Soapbox, SqliteSequence

import data.code as Database


def teardown_function():
    # Empty Scores and SnipingMods tables after each test
    CarePackage.delete().where(True).execute()


def test_set_carepackage():
    assert Database.set_carepackage('MyKey', 999, 'MyHint')

    carepackage = CarePackage.get(key='MyKey')
    assert carepackage.expiration == 999
    assert carepackage.hint == 'MyHint'

    assert Database.set_carepackage('MyKey', 999, 'MyHint') == False

def test_check_remove_carepackage():

    carepackage = CarePackage(key='1', expiration=9, hint='test')
    carepackage.save(force_insert=True)
    carepackage = CarePackage(key='2', expiration=10, hint='test2')
    carepackage.save(force_insert=True)

    assert Database.check_keyword('test') == False
    assert Database.check_keyword('1')
    assert Database.check_keyword('2')

    assert Database.reset_carepackage('test') == False
    assert Database.reset_carepackage('1')

    assert Database.check_keyword('1') == False
    assert Database.check_keyword('2')