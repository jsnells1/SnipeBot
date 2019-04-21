import random

from data import code as Database

# id 1


def get_bonus_points(userId):
    Database.addPoints(userId, 8)

    return '8 bonus points immediately'


# id 2
def set_multiplier(userId):
    Database.set_user_multiplier(userId, 3)

    return 'a x3 point multiplier for 24 hours'


# id 3
def set_smoke_bomb(userId):
    Database.set_user_immunity(userId)

    return 'immunity for 24 hours'


function_map = {
    1: get_bonus_points,
    2: set_multiplier,
    3: set_smoke_bomb
}


def get_reward(id, userId):
    return function_map[id](userId)
