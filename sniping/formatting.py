
class SnipingFormatter:
    def __init__(self):
        self.author = None
        self.hits = None
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

    def joinListWithAnd(self, data):
        if len(data) == 0:
            return None

        if len(data) == 1:
            return data[0]

        return ', '.join(data[:-1]) + ' and ' + data[-1]

    def formatSnipeString(self):
        returnStr = ''

        if len(self.hits) > 0:
            returnStr += 'SNIPED! {} has sniped {}!\n'.format(
                self.author.display_name, self.joinListWithAnd(self.hits))

        if self.hasPotato:
            returnStr += '{} has passed the potato to {}! Get rid of it before it explodes!!!\n'.format(
                self.author.display_name, self.potatoName)

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

        returnStr += '\n```Kill Summary:\n\n'
        returnStr += 'Kills:                {}\n'.format(len(self.hits))
        if self.leaderHit:
            returnStr += 'Leader Kill Points:   3\n'
        if self.revengeHit:
            returnStr += 'Revenge Kill Points:  2\n'
        returnStr += 'Multiplier:          x{}\n'.format(self.multiplier)
        returnStr += 'Total Points:         {}```'.format(
            self.totalPoints + len(self.hits))

        return returnStr
