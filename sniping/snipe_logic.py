from tabulate import tabulate
from discord.ext import commands

from data import code as Database

from .formatting import formatSnipeString


def do_snipe(ctx, sniper, targets):
    hits = []
    immune = []
    respawns = []
    errors = []

    leaderId = Database.getLeader()
    revengeId = Database.getRevengeUser(sniper.id)
    multiplier = Database.get_multiplier(sniper.id)

    bonusPoints = 0

    leaderHit = False
    revengeHit = False

    if multiplier == -1:
        multiplier = 1

    for loser in targets:

        # Ignore bots
        if loser.bot:
            continue

        # Ignore immune users
        if Database.isImmune(loser.id):
            immune.append(loser.display_name)
            continue

        # Ignore respawning users
        if Database.isRespawning(loser.id):
            respawns.append(loser.display_name)
            continue

        # Try to register the snipe
        if Database.addSnipe(sniper.id, loser.id):
            if loser.id == leaderId:
                leaderHit = True
                bonusPoints += 3

            if loser.id == revengeId:
                revengeHit = True
                bonusPoints += 2
                Database.resetRevenge(sniper.id)

            hits.append(loser.nick)
        else:
            errors.append(loser.nick)

    killstreak = len(hits)
    hasPotato = False
    if len(hits) > 0:
        killstreak = Database.update_killstreak(sniper.id, len(hits))
        hasPotato = Database.has_potato(sniper.id)
        if hasPotato:
            Database.pass_potato(sniper.id, hits[0])

    bonusPoints = bonusPoints * multiplier + \
        (len(hits) * multiplier - len(hits))

    Database.addPoints(sniper.id, bonusPoints)

    totalPoints = bonusPoints + len(hits)

    revengeMember = commands.MemberConverter().convert(ctx, revengeId)

    output = formatSnipeString(sniper=sniper, hits=hits, respawns=respawns, immune=immune, errors=errors, hasPotato=hasPotato, leaderHit=leaderHit,
                               revengeHit=revengeHit, killstreak=killstreak, revengeMember=revengeMember, totalPoints=totalPoints, multiplier=multiplier)

    return output


def get_leaderboard(rows, guild, killstreakHolder, killstreakHiScore):
    outputRows = [['Name', 'P', 'S', 'D']]

    for row in rows:
        user = guild.get_member(int(row[0]))

        outputRows.append([user.display_name[0:8], str(
            row[1]), str(row[2]), str(row[3])])

    records = [['Record', 'User', '']]

    records.append(
        ['Streak', killstreakHolder.display_name[0:8], str(killstreakHiScore[1])])

    output = tabulate(records, headers='firstrow',
                      tablefmt='fancy_grid') + '\n\n'
    output += tabulate(outputRows, headers='firstrow', tablefmt='fancy_grid')
    return output
