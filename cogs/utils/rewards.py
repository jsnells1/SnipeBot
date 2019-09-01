from datetime import datetime, timedelta

from data import api as Database

from cogs.utils.sniper import Sniper


async def set_bonus_points(user):
    # id 1
    bonus_points = 8
    sniper = await Sniper.from_database(user.id, user.guild.id, user.display_name)
    await sniper.add_points(bonus_points)

    return f'{bonus_points} bonus points immediately'


def set_multiplier(user):
    # id 2
    multiplier = 3

    Database.set_user_multiplier(user.id, multiplier)

    return f'a x{multiplier} point multiplier for 24 hours'


def set_smoke_bomb(user):
    # id 3
    Database.set_user_smokebomb(user.id)

    return 'a smoke bomb! Use it whenever you\'d like for 3 hours of immunity!'


def set_hot_potato(user):
    # id 4
    expiration = datetime.now() + timedelta(hours=24)

    Database.set_user_potato(user.id, expiration.timestamp())

    return 'a... Hot Potato Bomb! Uh Oh! Snipe someone else to pass it to someone else before it explodes'


function_map = {
    1: set_bonus_points,
    2: set_multiplier,
    3: set_smoke_bomb,
    4: set_hot_potato
}


def get_reward(id, user):
    return function_map[id](user)
