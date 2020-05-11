import discord
import json
from discord.ext import commands
from discord import abc


class Reaction(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.client.user.id:
            return
        with open('data/data.json', 'r') as f:
            data = json.load(f)
        if str(payload.guild_id) not in data.keys():
            return
        if payload.message_id == data[f'{payload.guild_id}']['message_id']:
            reaction_guild = self.client.get_guild(payload.guild_id)
            reaction_channel = self.client.get_channel(payload.channel_id)
            reaction_message = await reaction_channel.fetch_message(payload.message_id)
            reaction_category = self.client.get_channel(
                data[f'{payload.guild_id}']['channel_ids'][0])
            await reaction_message.remove_reaction(payload.emoji, payload.member)

            # TODO: Manage channel names using the channel topic, too
            if payload.emoji.name == '\U0001F7E2':
                print('Create Channel...')
                # Channel creation here
                user_channel = await reaction_guild.create_text_channel(name=f'{self.client.get_user(payload.user_id).name}', category=reaction_category)
                with open('data/data.json', 'r') as f:
                    data = json.load(f)
                with open('data/data.json', 'w') as f:
                    data[f'{reaction_guild.id}']['channel_ids'].append(
                        user_channel.id)
                    json.dump(data, f, indent=4)

            elif payload.emoji.name == '\U0001F534':
                print('Delete Channel...')
                # Channel deletion here
                with open('data/data.json', 'r') as f:
                    data = json.load(f)
                try:
                    for channel in reaction_guild.channels:
                        if channel.id in data[f'{reaction_guild.id}']['channel_ids']:
                            if channel.name == self.client.get_user(payload.user_id).name.lower():
                                await channel.delete()
                                with open('data/data.json', 'w') as f:
                                    data[f'{reaction_guild.id}']['channel_ids'].remove(
                                        channel.id)
                                    json.dump(data, f, indent=4)
                except KeyError as err:
                    print('Channel not found')


def setup(client):
    client.add_cog(Reaction(client))
