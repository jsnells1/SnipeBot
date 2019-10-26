from enum import Enum

LIVE_DATABASE = './data/database.db'
DEV_DATABASE = './data/dev_database.db'

DATABASE = DEV_DATABASE


def switch_database(env):

    global DATABASE
    global LIVE_DATABASE
    global DEV_DATABASE

    if env == Environment.LIVE:
        DATABASE = LIVE_DATABASE
    elif env == Environment.DEV:
        DATABASE = DEV_DATABASE


class Environment (Enum):
    DEV = 'dev'
    LIVE = 'live'
