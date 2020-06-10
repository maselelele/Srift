import discord
from discord.ext import commands
from database.mongo import SriftUser
from concurrent.futures._base import TimeoutError
from utils.riot import RiotConnection
from discord.utils import get
from discord.errors import NotFound
from uuid import uuid4


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
            # Set some permissions
            everyone_overwrite = discord.PermissionOverwrite()
            everyone_overwrite.read_messages = False
            await self.channel.set_permissions(self.payload.member.guild.default_role, overwrite=everyone_overwrite)

            user_overwrite = discord.PermissionOverwrite()
            user_overwrite.read_messages = True
            user_overwrite.send_messages = True
            user_overwrite.add_reactions = False
            user_overwrite.create_instant_invite = False
            await self.channel.set_permissions(self.client.get_user(self.payload.user_id), overwrite=user_overwrite)

            # Create a user
            welcome_embed = discord.Embed(
                title='Welcome to the Srift Bot!',
                description='It looks like it\'s your first time using this bot.\nWould you write me your summoner name here so that I can create a profile for you?',
                color=0x0cc2b7)

            tooLong_embed = discord.Embed(
                title='You needed too long', description='Please recreate your channel', color=0xbf6900)

            # Ask user for summoner name
            await self.channel.send(embed=welcome_embed)
            try:
                name_message = await self.client.wait_for('message', timeout=30.0)

                user_overwrite.send_messages = False
                await self.channel.set_permissions(self.client.get_user(self.payload.user_id), overwrite=user_overwrite)

                if name_message.channel.id != self.channel.id:
                    return
                if f'{name_message.author.name}#{name_message.author.discriminator}' != f'{name_message.channel.topic}':
                    return
            except TimeoutError as toe:
                try:
                    await self.channel.send(embed=tooLong_embed)
                    user_overwrite.send_messages = False
                    await self.channel.set_permissions(self.client.get_user(self.payload.user_id), overwrite=user_overwrite)
                except NotFound as nfe:
                    return
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
                title='Please select the region your summoner is playing in', color=0x0cc2b7)
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
                await region_message.clear_reactions()
                user_region = list(regions.keys())[
                    list(regions.values()).index(f'{region_reaction.emoji[:1]}\U000020E3')]

                # -- Check if summoner name exists
                if self.riot_api.verifySummonerName(name_message.content, user_region.lower()):
                    user_overwrite.send_messages = False
                    await self.channel.set_permissions(self.client.get_user(self.payload.user_id), overwrite=user_overwrite)
                else:
                    invalidSummoner_embed = discord.Embed(
                        title='Invalid summoner name', description='Please recreate your channel!', color=0xc10600)
                    await self.channel.send(embed=invalidSummoner_embed)
                    user_overwrite.send_messages = False
                    await self.channel.set_permissions(self.client.get_user(self.payload.user_id), overwrite=user_overwrite)
                    return
            except TimeoutError as toe:
                try:
                    await self.channel.send(embed=tooLong_embed)
                    await region_message.clear_reactions()
                    user_overwrite.send_messages = False
                    await self.channel.set_permissions(self.client.get_user(self.payload.user_id), overwrite=user_overwrite)
                except NotFound as nfe:
                    return
                return
            except NotFound as nfe:
                return

            # Verification process
            verification_code = uuid4().hex[:8].upper()
            verification_embed = discord.Embed(
                title='Verification', url='https://srift.github.io/', description='To ensure that this username belongs to you, please follow the steps below...', color=0x0cc2b7)
            verification_embed.set_image(url='https://i.imgur.com/cSfkmp6.gif')
            verification_embed.add_field(
                name='Step 1:', value='Open your League of Legends Client', inline=False)
            verification_embed.add_field(
                name='Step 2:', value='Go to your settings, scroll down and select \'Verification\'', inline=False)
            verification_embed.add_field(
                name='Step 3:', value=f'Paste in `` {verification_code} `` and hit \'Save\'', inline=False)
            verification_embed.add_field(
                name='Step 4:', value='When done, react with :white_check_mark: to this message', inline=False)

            verification_message = await self.channel.send(embed=verification_embed)
            await verification_message.add_reaction('\U00002705')

            try:
                verification_reaction, verification_reaction_user = await self.client.wait_for('reaction_add', check=check, timeout=120.0)
                await verification_reaction.remove(verification_reaction_user)
                user_summonerId = self.riot_api.getEncryptedSummonerIdByName(
                    name_message.content, user_region)

                await verification_message.clear_reactions()

                if self.riot_api.verifySummonerCode(user_summonerId, user_region, verification_code):
                    verified_embed = discord.Embed(
                        title='Verified', color=0X0cc200)
                    await self.channel.send(embed=verified_embed)
                    await verification_message.clear_reactions()

                    # Save user to database
                    SriftUser(
                        discord_id=self.payload.user_id,
                        summoner_id=user_summonerId,
                        summoner_region=user_region,
                        summoner_accountId=self.riot_api.getAccountIdByExistingUser(),
                        summoner_puuid=self.riot_api.getPuuidByExistingUser(),
                        summoner_name=self.riot_api.getNameByExistingUser()
                    ).save()

                else:
                    notVerified_embed = discord.Embed(
                        title='Not Verified', color=0xc10600)
                    await self.channel.send(embed=notVerified_embed)
                    await verification_message.clear_reactions()

            except TimeoutError as toe:
                await self.channel.send(embed=tooLong_embed)
                await verification_message.clear_reactions()
                user_overwrite.send_messages = False
                await self.channel.set_permissions(self.client.get_user(self.payload.user_id), overwrite=user_overwrite)

        else:
            # TODO: User existing
            await self.channel.send('Hello existing user!')


def setup(client):
    client.add_cog(UserChannel(client))
