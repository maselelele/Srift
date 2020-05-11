import discord
import json
from discord.ext import commands


class Srift(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['Srift', 'sr', 's'])
    @commands.has_guild_permissions(administrator=True)
    async def srift(self, ctx, subcommand=None):
        guild = ctx.message.guild
        if subcommand == 'init':
            await ctx.send(f'Initializing Srift channels...')
            channels = []
            for ch in guild.categories:
                channels.append(str(ch).upper())
            if 'SRIFT-BOT' not in channels:
                srift_category = await guild.create_category_channel('SRIFT-BOT')
                srift_text = await guild.create_text_channel(name='srift-bot', category=srift_category)
                with open('data/data.json', 'r') as f:
                    data = json.load(f)
                with open('data/data.json', 'w') as f:
                    data.update(
                        {guild.id: {'channel_ids': [srift_category.id, srift_text.id]}})
                    json.dump(data, f, indent=4)
                embed = discord.Embed(
                    title='Create your channel', color=0x0cc2b7)
                embed.add_field(name='Create your channel',
                                value=f'React with  \U0001F7E2', inline=True)
                embed.add_field(name='Delete your channel',
                                value=f'React with  \U0001F534', inline=True)

                msg = await srift_text.send(embed=embed)
                await ctx.send(f'Srift channels created!')
                await msg.add_reaction('\U0001F7E2')
                await msg.add_reaction('\U0001F534')
                # TODO: Merge read and write modes
                with open('data/data.json', 'r') as f:
                    data = json.load(f)
                with open('data/data.json', 'w') as f:
                    data[f'{guild.id}'].update({'message_id': msg.id})
                    json.dump(data, f, indent=4)
            else:
                await ctx.send(f'Bot is already initialized!\nTry to terminate the existing channels.')
                return
        elif subcommand == 'term':
            with open('data/data.json', 'r') as f:
                data = json.load(f)
            await ctx.send(f'Terminating Srift Channels...')
            try:
                for channel in guild.channels:
                    if channel.id in data[f'{guild.id}']['channel_ids']:
                        await channel.delete()
                with open('data/data.json', 'w') as f:
                    del data[f'{guild.id}']
                    json.dump(data, f, indent=4)
            except KeyError as err:
                await ctx.send(f'No Srift channels have been initialized yet.')

    @srift.error
    async def srift_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.message.add_reaction('\U000026D4')


def setup(client):
    client.add_cog(Srift(client))
