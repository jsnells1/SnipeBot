import random
from datetime import datetime, timedelta

from data import api as Database

# id 1


def set_bonus_points(userId):
    bonusPoints = 8

    Database.addPoints(userId, bonusPoints)

    return '{} bonus points immediately'.format(bonusPoints)


# id 2
def set_multiplier(userId):
    multiplier = 3

    Database.set_user_multiplier(userId, multiplier)

    return 'a x{} point multiplier for 24 hours'.format(multiplier)


# id 3
def set_smoke_bomb(userId):
    Database.set_user_smokebomb(userId)

    return 'a smoke bomb! Use it whenever you\'d like for 3 hours of immunity!'

# id 4


def set_hot_potato(userId):
    expiration = datetime.now() + timedelta(hours=24)

    Database.set_user_potato(userId, expiration.timestamp())

    return 'a... Hot Potato Bomb! Uh Oh! Snipe someone else to pass it to someone else before it explodes'


function_map = {
    1: set_bonus_points,
    2: set_multiplier,
    3: set_smoke_bomb,
    4: set_hot_potato
}


def get_reward(id, userId):
    return function_map[id](userId)
