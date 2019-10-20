import discord.ext.commands as commands


class CustomHelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__(command_attrs={"name": "snipebot"})
