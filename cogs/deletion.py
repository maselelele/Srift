import discord
from discord.ext import commands
from database.mongo import SriftGuild


class Deletion(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        # Get the user from audit log
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
            user = entry.user

        # Return if bot deletes the channel
        if user.id == self.client.user.id:
            return

        # Get channel ids from database
        srift_ids = list(SriftGuild.objects.get(
            guild_id=channel.guild.id).srift_ids.values())
        userchannel_ids = list(SriftGuild.objects.get(
            guild_id=channel.guild.id).user_channels.values())

        # Check if deleted channel was part of Srift Channels
        if channel.id in srift_ids:
            srift_channels_dict = dict(SriftGuild.objects(
                guild_id=channel.guild.id).get().to_mongo()['srift_ids'])
            dictKey = list(srift_channels_dict.keys())[list(
                srift_channels_dict.values()).index(channel.id)]
            srift_channels_dict.pop(dictKey)
            for key, value in srift_channels_dict.items():
                if key == 'srift_channel':
                    channel = self.client.get_channel(value)
                    await channel.delete()
                elif key == 'category_channel':
                    channel = self.client.get_channel(value)
                    await channel.delete()

            SriftGuild.objects(guild_id=channel.guild.id).get().update(
                srift_ids={})
            SriftGuild.objects(guild_id=channel.guild.id).get().update(
                initialized=False)
        elif channel.id in userchannel_ids:
            pass


def setup(client):
    client.add_cog(Deletion(client))
