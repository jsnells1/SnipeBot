from datetime import datetime

from data import code

def set_carepackage(keyword, time, hint):
    try:
        expiration = datetime.strptime(time, '%m/%d/%y %H:%M')
    except Exception as e:
        return str(e)

    response = code.set_carepackage(keyword, expiration.timestamp(), hint)

    if not response:
        return '```Care Package failed to be set```'

    return '```Care Package set, Expires at {}```'.format(expiration)

