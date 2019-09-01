from enum import Enum

from ._sniping import *
from ._carepackage import *

LIVE_DATABASE = './data/database.db'
DEV_DATABASE = './data/dev_database.db'

DATABASE = DEV_DATABASE


def switchDatabase(env):

    global DATABASE
    global LIVE_DATABASE
    global DEV_DATABASE

    do_change = False
    if env == Environment.live:
        DATABASE = LIVE_DATABASE
        do_change = True
    elif env == Environment.dev:
        DATABASE = DEV_DATABASE
        do_change = True

    return do_change


class Environment (Enum):
    dev = 1
    live = 2
