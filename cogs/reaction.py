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
            user_full_name = f'{self.client.get_user(payload.user_id).name}#{self.client.get_user(payload.user_id).discriminator}'
            await reaction_message.remove_reaction(payload.emoji, payload.member)

            if payload.emoji.name == '\U0001F7E2':
                for channel in reaction_guild.channels:
                    if type(channel) == discord.channel.TextChannel:
                        if channel.topic == user_full_name:
                            return
                user_channel = await reaction_guild.create_text_channel(name=f'{reaction_guild.get_member(payload.user_id).nick}', category=reaction_category)
                await user_channel.edit(topic=user_full_name)
                with open('data/data.json', 'r') as f:
                    data = json.load(f)
                with open('data/data.json', 'w') as f:
                    data[f'{reaction_guild.id}']['channel_ids'].append(
                        user_channel.id)
                    json.dump(data, f, indent=4)

            elif payload.emoji.name == '\U0001F534':
                with open('data/data.json', 'r') as f:
                    data = json.load(f)
                try:
                    for channel in reaction_guild.channels:
                        if channel.id in data[f'{reaction_guild.id}']['channel_ids']:
                            if channel.name == reaction_guild.get_member(payload.user_id).nick.lower():
                                if channel.topic == user_full_name:
                                    await channel.delete()
                                    with open('data/data.json', 'w') as f:
                                        data[f'{reaction_guild.id}']['channel_ids'].remove(
                                            channel.id)
                                        json.dump(data, f, indent=4)
                except KeyError as err:
                    print('Channel not found')


def setup(client):
    client.add_cog(Reaction(client))
