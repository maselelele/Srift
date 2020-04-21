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
        with open('data/messages.json', 'r') as f:
            messages = json.load(f)
        if payload.message_id == messages[f'{payload.guild_id}']:
            reaction_guild = self.client.get_guild(payload.guild_id)
            reaction_channel = self.client.get_channel(payload.channel_id)
            reaction_message = await reaction_channel.fetch_message(payload.message_id)
            await reaction_message.remove_reaction(payload.emoji, payload.member)

            if payload.emoji.name == '\U0001F7E2':
                print('Create Channel...')
                # Channel creation here
            elif payload.emoji.name == '\U0001F534':
                print('Delete Channel...')
                # Channel deletion here


def setup(client):
    client.add_cog(Reaction(client))
