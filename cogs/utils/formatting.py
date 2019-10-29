from tabulate import tabulate


class SnipeFormatter():
    def __init__(self, **kwargs):
        self.sniper = kwargs.get('sniper')
        self.hits = kwargs.get('hits', [])
        self.respawns = kwargs.get('respawns', [])
        self.immunes = kwargs.get('immunes', [])
        self.new_potato_owner = kwargs.get('new_potato_owner')
        self.leader_hit = kwargs.get('leader_hit', False)
        self.revenge_member = kwargs.get('revenge_member')
        self.total_points = kwargs.get('total_points', 0)

    @staticmethod
    def _join_list_with_and(data):
        if len(data) == 0:
            return ''

        if len(data) == 1:
            return data[0]

        return f'{", ".join(data[:-1])} and {data[-1]}'

    def _get_snipe_text(self):
        result_string = ''

        hits = [hit.display_name for hit in self.hits]
        respawns = [respawn.display_name for respawn in self.respawns]
        immunes = [immune.display_name for immune in self.immunes]

        for hit in hits:
            result_string += f'{self.sniper.display_name}   ︻デ═一   {hit}\n'

        if self.sniper.killstreak > 1:
            result_string += f'{self.sniper.display_name} is on a killstreak of {self.sniper.killstreak}!\n'

        if self.new_potato_owner:
            result_string += f'{self.sniper.display_name} has passed the potato to {self.new_potato_owner}! Get rid of it before it explodes!!!\n'

        if self.leader_hit:
            result_string += 'NICE SHOT! The leader has been taken out! Enjoy 3 bonus points!\n'

        if self.revenge_member:
            result_string += f'Revenge is so sweet! You got revenge on {self.revenge_member}! Enjoy 2 bonus points!\n'

        if len(respawns) > 0:
            result_string += f'{SnipeFormatter._join_list_with_and(respawns)} was/were not hit because they\'re still respawning.\n'

        if len(immunes) > 0:
            result_string += f'{SnipeFormatter._join_list_with_and(immunes)} was/were not hit because they\'re immune!\n'

        return result_string

    def _get_kill_summary(self):
        killsummary = [['Kills', len(self.hits)]]

        if self.leader_hit:
            killsummary.append(['Leader Kill Points', '3'])
        if self.revenge_member:
            killsummary.append(['Revenge Kill Points', '2'])

        killsummary.append(['Pre-Multiplier Total', self.total_points // self.sniper.multiplier])
        killsummary.append(['Multiplier', f'x{self.sniper.multiplier}'])
        killsummary.append(['Total Points', self.total_points])

        return f'```Kill Summary:\n\n{tabulate(killsummary, tablefmt="plain", colalign=("left", "right"))}```'

    def formatted_output(self):
        return f'{self._get_snipe_text()}{self._get_kill_summary()}'
