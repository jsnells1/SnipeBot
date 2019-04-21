from datetime import datetime

from data import code as Database


def set_carepackage(keyword, time, hint):
    try:
        expiration = datetime.strptime(time, '%m/%d/%y %H:%M')
    except Exception as e:
        return str(e)

    response = Database.set_carepackage(keyword, expiration.timestamp(), hint)

    if not response:
        return '```Care Package failed to be set```'

    return '```Care Package set, Expires at {}```'.format(expiration)


def get_hint():
    hint = Database.get_carepackage_hint()

    if hint is None:
        return 'There is no hint available.'

    if not hint:
        return '```Error retrieving hint.```'

    return 'The hint is: ' + str(hint)


def isKeyword(keyword):
    key = Database.getKeyword()

    if key is None:
        return False, 'There is no carepackage available.'

    if not key:
        return False, '```Error retrieving key.```'

    if key.lower() == keyword.lower():
        Database.reset_carepackage()
        return True, None
    else:
        return False, None
