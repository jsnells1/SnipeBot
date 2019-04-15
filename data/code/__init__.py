from enum import Enum

from ._sniping import *
from ._soapbox import *

LIVE_DATABASE = './data/database.db'
DEV_DATABASE = './data/dev_database.db'

DATABASE = DEV_DATABASE


def switchDatabase(env):

    global DATABASE
    global LIVE_DATABASE
    global DEV_DATABASE

    if env == Environment.live:
        DATABASE = LIVE_DATABASE
        return True
    elif env == Environment.dev:
        DATABASE = DEV_DATABASE
        return True

    return False


class Environment (Enum):
    dev = 1
    live = 2
