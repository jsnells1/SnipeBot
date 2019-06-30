from tabulate import tabulate
from discord.ext import commands

from data import api as Database

from cogs.utils.formatting import formatSnipeString

from cogs.utils.sniper import Sniper


# TODO Fix with new class
async def do_snipe(ctx, sniper, targets):
    hits = []
    immune = []
    respawns = []
    errors = []

    # Convert sniper to Sniper object
    sniper = await Sniper.from_database(sniper.id, ctx.guild.id, sniper.display_name)

    # Convert targets to list of Sniper objects, ignoring bots
    targets = [await Sniper.from_database(target.id, ctx.guild.id, target.display_name) for target in targets if not target.bot]

    leaderId = Database.getLeader()

    bonusPoints = 0

    leaderHit = False
    revengeHit = False

    for loser in targets:

        # Ignore immune users
        if loser.is_immune():
            immune.append(loser.display_name)
            continue

        # Ignore respawning users
        if loser.is_respawning():
            respawns.append(loser.display_name)
            continue

        # Try to register the snipe
        if await sniper.add_snipe(loser):
            if loser.id == leaderId:
                leaderHit = True
                bonusPoints += 3

            if loser.id == sniper.revenge:
                revengeHit = True
                bonusPoints += 2
                Database.resetRevenge(sniper.id)

            hits.append(loser.display_name)
        else:
            errors.append(loser.display_name)

    killstreak = len(hits)
    hasPotato = False
    if len(hits) > 0:
        killstreak = Database.update_killstreak(sniper.id, len(hits))
        hasPotato = Database.has_potato(sniper.id)
        if hasPotato:
            Database.pass_potato(sniper.id, hits[0])

    bonusPoints = (bonusPoints + len(hits)) * sniper.multiplier

    Database.addPoints(sniper.id, bonusPoints)

    totalPoints = bonusPoints

    revengeMember = ctx.guild.get_member(sniper.revenge)

    output = formatSnipeString(sniper=sniper, hits=hits, respawns=respawns, immune=immune, errors=errors, hasPotato=hasPotato, leaderHit=leaderHit,
                               revengeHit=revengeHit, killstreak=killstreak, revengeMember=revengeMember, totalPoints=totalPoints, multiplier=sniper.multiplier)

    return output


async def get_leaderboard(ctx):
    outputRows = [['Name', 'P', 'S', 'D']]

    rows = Database.getLeaderboard()
    killstreakHiScore = Database.get_highest_killstreak()

    if not rows or killstreakHiScore is None:
        return 'Error retrieving leaderboard'

    killstreakHolder = ctx.guild.get_member(killstreakHiScore.user_id)

    for row in rows:
        user = await commands.MemberConverter().convert(ctx, str(row.user_id))

        outputRows.append([user.display_name[0:8], str(
            row.points), str(row.snipes), str(row.deaths)])

    records = [['Record', 'User', '']]

    records.append(
        ['Streak', killstreakHolder.display_name[0:8], str(killstreakHiScore.killstreak_record)])

    output = tabulate(records, headers='firstrow',
                      tablefmt='fancy_grid') + '\n\n'
    output += tabulate(outputRows, headers='firstrow', tablefmt='fancy_grid')
    return output
