import discord
import json
from discord.ext import commands


class Srift(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['srift', 'sr', 's'])
    async def Srift(self, ctx, subcommand=None):
        guild = ctx.message.guild
        with open('data/servers.json', 'r') as f:
            servers = json.load(f)
        if subcommand == 'init':
            await ctx.send(f'Initializing Srift channels...')
            channels = []
            for ch in guild.categories:
                channels.append(str(ch).upper())
            if 'SRIFT-BOT' not in channels:
                srift_category = await guild.create_category_channel('SRIFT-BOT')
                srift_text = await guild.create_text_channel(name='srift-bot', category=srift_category)
                servers.update(
                    {guild.id: [srift_category.id, srift_text.id]})
                await ctx.send(f'Srift channels created!')
            else:
                await ctx.send(f'Bot is already initialized!\nTry to terminate the existing channels.')
                return
        elif subcommand == 'term':
            await ctx.send(f'Terminating Srift Channels...')
            if bool(servers):
                for channel in guild.channels:
                    if channel.id in servers[f'{guild.id}']:
                        await channel.delete()
                servers.clear()
            else:
                await ctx.send(f'No Srift channels have been initialized yet.')

        with open('data/servers.json', 'w') as f:
            json.dump(servers, f, indent=4)


def setup(client):
    client.add_cog(Srift(client))
