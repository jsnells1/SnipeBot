from tabulate import tabulate


def _joinListWithAnd(data):
    if len(data) == 0:
        return None

    if len(data) == 1:
        return data[0]

    return ', '.join(data[:-1]) + ' and ' + data[-1]


def _getsnipetext(sniper=None, hits=[], respawns=[], immune=[], errors=[], hasPotato=False, leaderHit=False,
                  revengeHit=False, revengeMember=None, killstreak=0):
    returnStr = ''

    for hit in hits:
        returnStr += sniper.display_name + '   ︻デ═一   ' + hit + '\n'

    if killstreak > 1:
        returnStr += '%s is on a killstreak of %s!\n' % (
            sniper.display_name, killstreak)

    if hasPotato and len(hits) > 0:
        returnStr += '%s has passed the potato to %s! Get rid of it before it explodes!!!\n' % (
            sniper.display_name, hit[0])

    if leaderHit:
        returnStr += 'NICE SHOT! The leader has been taken out! Enjoy 3 bonus points!\n'

    if revengeHit:
        returnStr += 'Revenge is so sweet! You got revenge on ' + \
            revengeMember.display_name + '! Enjoy 2 bonus points!\n'

    if len(respawns) > 0:
        returnStr += _joinListWithAnd(respawns) + \
            ' was/were not hit because they\'re still respawning.\n'

    if len(immune) > 0:
        returnStr += _joinListWithAnd(immune) + \
            ' was/were not hit because they\'re immune!\n'

    if len(errors) > 0:
        returnStr += 'Error registering hit on ' + \
            _joinListWithAnd(errors) + '.\n'

    return returnStr


def _getKillSummary(hits=[], leaderHit=False, revengeHit=False, totalPoints=0, multiplier=1):
    output = '```Kill Summary:\n\n'

    killsummary = [['Kills', str(len(hits))]]

    if leaderHit:
        killsummary.append(['Leader Kill Points', '3'])
    if revengeHit:
        killsummary.append(['Revenge Kill Points', '2'])

    killsummary.append(
        ['Pre-Multiplier Total', str(int(totalPoints / multiplier))])
    killsummary.append(['Multiplier', 'x' + str(multiplier)])
    killsummary.append(['Total Points', str(totalPoints)])

    return output + tabulate(killsummary, tablefmt='plain', colalign=('left', 'right')) + '```'


def formatSnipeString(sniper=None, hits=[], respawns=[], immune=[], errors=[], hasPotato=False, leaderHit=False,
                      revengeHit=False, revengeMember=None, totalPoints=0, multiplier=1, killstreak=0):
    output = ''

    output += _getsnipetext(sniper, hits, respawns, immune, errors, hasPotato, leaderHit,
                            revengeHit, revengeMember, killstreak)

    output += _getKillSummary(hits, leaderHit,
                              revengeHit, totalPoints, multiplier)

    return output
