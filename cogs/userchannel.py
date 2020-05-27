import discord
from discord.ext import commands
from database.mongo import SriftUser
from concurrent.futures._base import TimeoutError
from utils.riot import RiotConnection
from discord.utils import get


class UserChannel(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.riot_api = RiotConnection()

    async def sendMessageOnCreation(self, payload, channel):
        self.payload = payload
        self.channel = channel
        try:
            data = SriftUser.objects(
                discord_id__contains=self.payload.user_id).get()
        except Exception as ex:
            data = None

        if data is None:
            # Create a user
            welcome_embed = discord.Embed(
                title='Welcome to the Srift Bot!',
                description='It looks like it\'s your first time using this bot.\nWould you write me your summoner name here so that I can create a profile for you?',
                color=0x0cc2b7)

            # Ask user for summoner name
            await self.channel.send(embed=welcome_embed)
            try:
                name_message = await self.client.wait_for('message', timeout=30.0)
                if name_message.channel.id != self.channel.id:
                    return
                if f'{name_message.author.name}#{name_message.author.discriminator}' != f'{name_message.channel.topic}':
                    return
            except TimeoutError as toe:
                await self.channel.send('You needed too long, please recreate your channel')
                return
            regions = {
                'BR1': '0\U000020E3',
                'EUN1': '1\U000020E3',
                'EUW1': '2\U000020E3',
                'JP1': '3\U000020E3',
                'KR': '4\U000020E3',
                'LA1': '5\U000020E3',
                'LA2': '6\U000020E3',
                'NA1': '7\U000020E3',
                'OC1': '8\U000020E3',
                'RU': '9\U000020E3',
                'TR1': '\U0001F51F'
            }

            # Ask user for the summoner region
            region_embed = discord.Embed(
                title='Please select the reagion your summoner is playing in', color=0x0cc2b7)
            for i in range(len(regions)):
                region_embed.add_field(name=list(regions.keys())[i],
                                       value=list(regions.values())[i], inline=True)

            # - Add reactions to embed
            region_message = await self.channel.send(embed=region_embed)
            for i in range(len(regions)):
                await region_message.add_reaction(list(regions.values())[i])

            # - Wait and check for user reacting

            def check(reaction, user):
                return user.id == self.payload.user_id

            try:
                region_reaction, region_reaction_user = await self.client.wait_for('reaction_add', check=check, timeout=30.0)
                await region_reaction.remove(region_reaction_user)

                user_region = list(regions.keys())[
                    list(regions.values()).index(f'{region_reaction.emoji[:1]}\U000020E3')]

                # -- Check if summoner name exists
                if self.riot_api.verifySummonerName(name_message.content, user_region.lower()):
                    await self.channel.send(f'Looks like your summoner name is valid in {user_region}!')
                else:
                    await self.channel.send('Invalid summoner name, please recreate your channel!')
                    return
            except TimeoutError as toe:
                await self.channel.send('You needed too long, please recreate your channel')

        else:
            # TODO: User existing
            await self.channel.send('Hello existing user!')


def setup(client):
    client.add_cog(UserChannel(client))
