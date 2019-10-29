from enum import Enum


class Environment(Enum):
    DEV = 'dev'
    LIVE = 'live'


class Database():
    current_database = Environment.DEV

    @staticmethod
    def connection_string():
        if Database.current_database == Environment.DEV:
            return Database.dev_database()
        elif Database.current_database == Environment.LIVE:
            return Database.live_database()

    @staticmethod
    def live_database():
        return './data/database.db'

    @staticmethod
    def dev_database():
        return './data/dev_database.db'

    @staticmethod
    def switch_database(env):
        if env == Environment.LIVE:
            Database.current_database = Environment.LIVE
        elif env == Environment.DEV:
            Database.current_database = Environment.DEV
