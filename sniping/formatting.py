from tabulate import tabulate


class SnipingFormatter:
    def __init__(self):
        self.sniper = None
        self.hits = []
        self.respawns = None
        self.immune = None
        self.errors = None
        self.hasPotato = None
        self.leaderHit = None
        self.revengeHit = None
        self.potatoName = None
        self.revengeMember = None
        self.totalPoints = None
        self.multiplier = None
        self.killstreak = None

    def joinListWithAnd(self, data):
        if len(data) == 0:
            return None

        if len(data) == 1:
            return data[0]

        return ', '.join(data[:-1]) + ' and ' + data[-1]

    def _getsnipetext(self):
        returnStr = ''

        for hit in self.hits:
            returnStr += '{}   ︻デ═一   {}\n'.format(
                self.sniper.display_name, hit)

        if self.killstreak > 1:
            returnStr += '{} is on a killstreak of {}!\n'.format(
                self.sniper.display_name, self.killstreak)

        if self.hasPotato:
            returnStr += '{} has passed the potato to {}! Get rid of it before it explodes!!!\n'.format(
                self.sniper.display_name, self.potatoName)

        if self.leaderHit:
            returnStr += 'NICE SHOT! The leader has been taken out! Enjoy 3 bonus points!\n'

        if self.revengeHit:
            returnStr += 'Revenge is so sweet! You got revenge on {}! Enjoy 2 bonus points!\n'. format(
                self.revengeMember.display_name)

        if len(self.respawns) > 0:
            returnStr += '{} was/were not hit because they\'re still respawning.\n'.format(
                self.joinListWithAnd(self.respawns))

        if len(self.immune) > 0:
            returnStr += '{} was/were not hit because they\'re immune!\n'.format(
                self.joinListWithAnd(self.immune))

        if len(self.errors) > 0:
            returnStr += 'Error registering hit on {}.\n'.format(
                self.joinListWithAnd(self.errors))

        return returnStr

    def formatSnipeString(self):
        returnStr = ''

        returnStr += self._getsnipetext()

        returnStr += '```Kill Summary:\n\n'

        killsummary = [['Kills', str(len(self.hits))]]

        if self.leaderHit:
            killsummary.append(['Leader Kill Points', '3'])
        if self.revengeHit:
            killsummary.append(['Revenge Kill Points', '2'])

        killsummary.append(
            ['Pre-Multiplier Total', str(int(self.totalPoints / self.multiplier))])
        killsummary.append(['Multiplier', 'x' + str(self.multiplier)])
        killsummary.append(['Total Points', str(self.totalPoints)])

        return returnStr + tabulate(killsummary, tablefmt='plain', colalign=('left', 'right')) + '```'
