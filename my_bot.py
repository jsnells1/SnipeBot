import discord

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!hello'):
            await message.channel.send('Hello {0.author.mention}'.format(message))

client = MyClient()
client.run('NTY2MDU0MTYzNDk5NDUwMzk5.XK_aKg.-dGUgE3J1JgnJaVrnEJS8gFQDKw')