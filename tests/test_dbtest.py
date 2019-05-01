import pytest

import sniping
import data.code as Database


def setup_module(module):
    Database.switchDatabase(Database.Environment.dev)


def setup_function(function):
    if Database.DATABASE != Database.DEV_DATABASE:
        pytest.fail('Database not set to dev')


def test_example():
    assert 1 == 1


def test_example2():
    assert 1 == 1


def test_example3():
    assert 1 == 1
