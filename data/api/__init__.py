from enum import Enum

from ._sniping import *
from ._carepackage import *

LIVE_DATABASE = './data/database.db'
DEV_DATABASE = './data/dev_database.db'

DATABASE = DEV_DATABASE


def switch_database(env):

    global DATABASE
    global LIVE_DATABASE
    global DEV_DATABASE

    do_change = False
    if env == Environment.DEV:
        DATABASE = LIVE_DATABASE
        do_change = True
    elif env == Environment.LIVE:
        DATABASE = DEV_DATABASE
        do_change = True

    return do_change


class Environment (Enum):
    DEV = 1
    LIVE = 2
