import unittest

from data import code as Database
from data.code import Environment


class DatabaseTests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        response = Database.switchDatabase(Environment.dev)

        self.ownerId = 273946109896818701
        self.dbflag = response

    def setUp(self):
        if not self.dbflag:
            self.fail('Database failed to switch to Dev')

    def test_addPoints(self):
        self.assertTrue(Database.addPoints(self.dbflag, 1))
        self.assertTrue(Database.addPoints(self.dbflag, -1))

    def test_registerUser(self):
        self.assertFalse(Database.registerUser(None))
        self.assertFalse(Database.registerUser(self.ownerId))
