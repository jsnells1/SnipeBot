import discord.ext.commands as commands


class CustomHelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__(command_attrs={"name": "snipebot"})


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.overview_text = ('"Sniping" was originally created when an Indie spotted a fellow Indie in a public place like the library and commons without being noticed back. '
                              'The spotter snapped a picture of the person and then posted it in the Discord. It was a fun way to say "hi!". '
                              'Eventually SnipeBot was created as a way to keep score of snipes.\n'
                              'Here\'s how to use SnipeBot\'s core feature: "sniping".\n\n'
                              'NOTE: Sniping is only for fun and we ask everyone to respect people\'s privacy when posting pictures.\n'
                              'You can use the command !sbwhitelist to remove yourself from sniping and being sniped. You can use the same command again to re-add yourself.\n\n'
                              'To snipe someone, take a picture of the Indie in the wild without being noticed. Then, post the picture in the "snipebot" channel in the discord.\n'
                              'Before hitting send, enter the !snipe command in the comment box that pops up.\n'
                              'The snipe command is used like this:\n\n'
                              '\t!snipe @user\n\n'
                              'Where user is the discord username for the person that was sniped.\n'
                              'You can snipe multiple users at once by just mentioning more users in the command like this:\n\n'
                              '\t!snipe @user1 @user2\n\n'
                              'You don\'t have to worry about registering yourself with SnipeBot, it is done automatically.\n\n'
                              'That\'s the basic idea.\n'
                              'Use !leaderboard to get the current leaderboard.\n'
                              'Use !rules to better look at rules and scoring.\n')

        self.rules_text = ('Basic Rules for Sniping\n\n'
                           '1.  You can only snipe someone if they have not seen you yet.\n'
                           '2.  If someone spots you in an area, you\'re not allowed to snipe them until both of you leave that area.\n\n'
                           '\t For example, if Tom sees Billy in Commons, then Billy can\'t snipe Tom until they both leave Commons.\n'
                           '\t You are not allowed to just walk away for a few minutes and then come back and snipe that person.\n\n'
                           '3.  A player can\'t be sniped again for 2 hours after they sniped. An announcement will be made when they respawn.\n'
                           '4.  A player will instantly respawn if they snipe someone.\n'
                           '5.  When a player is sniped, the sniper is set as their revenge target for 3.5 hours\n'
                           '5a. Sniping the revenge target grants bonus points\n'
                           '5b. A player can\'t have more than one revenge target, getting sniped again would update their revenge target.\n'
                           '6.  Sniping the leader (first player on the leaderboard) grants bonus points.\n'
                           '7.  Sniping is disabled a hour before club through a hour after club.\n'
                           '8.  You cannot snipe anyone on the whitelist\n'
                           '\n'
                           'Scoring\n\n'
                           'Regular Snipe: 1 Point\n'
                           'Revenge Snipe: 2 Points\n'
                           'Leader Snipe:  3 Points\n')

    @commands.command(help='Gives a basic rundown on how to snipe someone')
    async def overview(self, ctx):
        await ctx.send(f'```{self.overview_text}```')

    @commands.command(help='Gives the basic rules for sniping')
    async def rules(self, ctx):
        await ctx.send(f'```{self.rules_text}```')
