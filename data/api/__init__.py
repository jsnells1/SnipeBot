from enum import Enum

from ._sniping import *
from ._soapbox import *
from ._carepackage import *
from ._club_calendar import *

from data.models.data_models import database

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

    if do_change:
        database.init(DATABASE)

    return do_change


class Environment (Enum):
    dev = 1
    live = 2
