import pytest

import data.code as Database

OWNER_ID = 273946109896818701


def setup_module(module):
    Database.switchDatabase(Database.Environment.dev)


def setup_function(function):
    if Database.DATABASE != Database.DEV_DATABASE:
        pytest.fail('Database not set to dev')


def test_example():
    assert Database.addPoints(OWNER_ID, 1)
    assert Database.addPoints(OWNER_ID, -1)
