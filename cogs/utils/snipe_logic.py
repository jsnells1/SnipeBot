from tabulate import tabulate
from discord.ext import commands

from data import api as Database

from cogs.utils.formatting import formatSnipeString

from cogs.utils.sniper import Sniper
from cogs.utils.leaderboard import Leaderboard

# TODO Test, implementation seems done


async def do_snipe(ctx, sniper, targets):
    hits = []
    immune = []
    respawns = []
    errors = []

    # Convert sniper to Sniper object
    sniper = await Sniper.from_database(sniper.id, ctx.guild.id, sniper.display_name)

    # Convert targets to list of Sniper objects, ignoring bots
    targets = [await Sniper.from_database(target.id, ctx.guild.id, target.display_name) for target in targets if not target.bot]

    leaderboard = await Leaderboard(ctx).get_rows()

    leader_id = None
    if len(leaderboard) > 0:
        leader_id = leaderboard[0]['UserID']

    bonusPoints = 0

    leaderHit = False
    revengeHit = False

    for loser in targets:

        # Ignore immune users
        if loser.is_immune():
            immune.append(loser)
            continue

        # Ignore respawning users
        if loser.is_respawning():
            respawns.append(loser)
            continue

        # Try to register the snipe
        if await sniper.add_snipe(loser):
            if loser.id == leader_id:
                leaderHit = True
                bonusPoints += 3

            if loser.id == sniper.revenge:
                revengeHit = True
                bonusPoints += 2
                await sniper.reset_revenge()

            hits.append(loser)
        else:
            errors.append(loser)

    hasPotato = False
    if len(hits) > 0:
        await sniper.update_killstreak(len(hits))
        hasPotato = await sniper.has_potato()
        if hasPotato:
            await sniper.pass_potato(hits[0])

    killstreak = sniper.killstreak
    # Add the bonus points to the number of hits (1 point per hit) then multiply by the user's multiplier
    totalPoints = (bonusPoints + len(hits)) * sniper.multiplier
    # Add the points to the user in the database
    await sniper.add_points(totalPoints)
    # Get the discord user for the revenge target, will return None if not found or if revenge is None
    revengeMember = ctx.guild.get_member(sniper.revenge)

    output = formatSnipeString(sniper=sniper, hits=hits, respawns=respawns, immune=immune, errors=errors, hasPotato=hasPotato, leaderHit=leaderHit,
                               revengeHit=revengeHit, killstreak=killstreak, revengeMember=revengeMember, totalPoints=totalPoints, multiplier=sniper.multiplier)

    return output
