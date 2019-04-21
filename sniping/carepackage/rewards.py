import random

from data import code as Database

# id 1
def get_bonus_points(userId):
    return


# id 2
def set_multiplier(userId):
    return


# id 3
def set_smoke_bomb(userId):
    print('Smoke Bomb')


function_map = {
    1: get_bonus_points,
    2: set_multiplier,
    3: set_smoke_bomb
}


def get_reward(id, userId):
    function_map[id](userId)
