import discord
import json
from discord.ext import commands
from database.mongo import SriftGuild, Mongo


class Srift(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['Srift', 'sr', 's'])
    @commands.has_guild_permissions(administrator=True)
    async def srift(self, ctx, subcommand=None):
        guild = ctx.message.guild
        if subcommand == 'init':
            if SriftGuild.objects.get(guild_id=guild.id).initialized:
                already_message = await ctx.send('Bot already initialized')
                await already_message.add_reaction('\U00002714')
                return

            srift_category = await guild.create_category_channel('SRIFT-BOT')
            srift_text = await guild.create_text_channel(name='srift-bot', category=srift_category)
            await srift_text.set_permissions(guild.default_role, add_reactions=False, send_messages=False)

            embed = discord.Embed(
                title='Create your channel', color=0x0cc2b7)
            embed.add_field(name='Create your channel',
                            value=f'React with  \U0001F7E2', inline=True)
            embed.add_field(name='Delete your channel',
                            value=f'React with  \U0001F534', inline=True)

            msg = await srift_text.send(embed=embed)
            created_message = await ctx.send(f'Srift channels created!')
            await created_message.add_reaction('\U00002714')
            await msg.add_reaction('\U0001F7E2')
            await msg.add_reaction('\U0001F534')

            SriftGuild.objects(guild_id=guild.id).get().update(
                srift_ids={'category_channel': srift_category.id,
                           'srift_channel': srift_text.id,
                           'srift_message': msg.id},
                initialized=True
            )

        elif subcommand == 'term':
            try:
                guild_mongo = SriftGuild.objects(guild_id=guild.id).get()
            except Exception as e:
                print(e)
            if guild_mongo.initialized:
                term_message = await ctx.send(f'Terminating Srift Channels...')
                await term_message.add_reaction('\U00002714')
                for channel in list(reversed(guild.channels)):
                    if channel.id in guild_mongo.srift_ids.values():
                        await channel.delete()
            else:
                no_message = await ctx.send(f'No Srift Channels have been initialized yet.')
                await no_message.add_reaction('\U00002714')

            SriftGuild.objects(guild_id=guild.id).get().update(
                srift_ids={},
                initialized=False
            )

    @srift.error
    async def srift_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.message.add_reaction('\U000026D4')


def setup(client):
    client.add_cog(Srift(client))
