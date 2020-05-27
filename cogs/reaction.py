import discord
import json
from discord.ext import commands
from discord import abc
from database.mongo import SriftGuild
from cogs.userchannel import UserChannel


class Reaction(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.client.user.id:
            return
        if not SriftGuild.objects.get(guild_id=payload.guild_id).initialized:
            return
        if payload.message_id == SriftGuild.objects.get(guild_id=payload.guild_id).srift_ids['srift_message']:
            reaction_guild = self.client.get_guild(payload.guild_id)
            reaction_channel = self.client.get_channel(payload.channel_id)
            reaction_message = await reaction_channel.fetch_message(payload.message_id)
            reaction_category = self.client.get_channel(
                SriftGuild.objects.get(guild_id=payload.guild_id).srift_ids['category_channel'])
            user_full_name = f'{self.client.get_user(payload.user_id).name}#{self.client.get_user(payload.user_id).discriminator}'
            await reaction_message.remove_reaction(payload.emoji, payload.member)

            # Create user channel
            if payload.emoji.name == '\U0001F7E2':
                for channel in reaction_guild.channels:
                    if type(channel) == discord.channel.TextChannel:
                        if channel.topic == user_full_name:
                            return
                user_channel = await reaction_guild.create_text_channel(name=f'{reaction_guild.get_member(payload.user_id).display_name}', category=reaction_category)
                await user_channel.edit(topic=user_full_name)

                user_channels_dict = dict(SriftGuild.objects(
                    guild_id=payload.guild_id).get().to_mongo()['user_channels'])
                user_channels_dict.update({
                    str(payload.user_id): {
                        "username": user_full_name,
                        "channel_id": user_channel.id
                    }
                })

                SriftGuild.objects(guild_id=payload.guild_id).get().update(
                    user_channels=user_channels_dict
                )
                await UserChannel(self.client).sendMessageOnCreation(payload, user_channel)

            # Delete user channel
            elif payload.emoji.name == '\U0001F534':
                user_channels_dict = dict(SriftGuild.objects(
                    guild_id=payload.guild_id).get().to_mongo()['user_channels'])
                if str(payload.user_id) not in list(user_channels_dict.keys()):
                    return
                for mongo_user_id in list(user_channels_dict.keys()):
                    if mongo_user_id == str(payload.user_id):
                        user_channel = user_channels_dict[mongo_user_id]
                        user_channel_id = user_channel['channel_id']
                        for guild_channel in reaction_guild.channels:
                            if user_channel_id == guild_channel.id:
                                await guild_channel.delete()
                                user_channels_dict.pop(str(payload.user_id))

                SriftGuild.objects(guild_id=payload.guild_id).get().update(
                    user_channels=user_channels_dict
                )


def setup(client):
    client.add_cog(Reaction(client))
