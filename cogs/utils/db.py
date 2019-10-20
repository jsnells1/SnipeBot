from enum import Enum

LIVE_DATABASE = './data/database.db'
DEV_DATABASE = './data/dev_database.db'

DATABASE = DEV_DATABASE


def switch_database(env):

    global DATABASE
    global LIVE_DATABASE
    global DEV_DATABASE

    changed = False
    if env == Environment.LIVE:
        DATABASE = LIVE_DATABASE
        changed = True
    elif env == Environment.DEV:
        DATABASE = DEV_DATABASE
        changed = True

    return changed


class Environment (Enum):
    DEV = 1
    LIVE = 2
