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
                with open('data/servers.json', 'w') as f:
                    servers.update(
                        {guild.id: [srift_category.id, srift_text.id]})
                    json.dump(servers, f, indent=4)
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
                with open('data/messages.json', 'w') as f:
                    json.dump({guild.id: msg.id}, f, indent=4)
            else:
                await ctx.send(f'Bot is already initialized!\nTry to terminate the existing channels.')
                return
        elif subcommand == 'term':
            await ctx.send(f'Terminating Srift Channels...')
            if bool(servers):
                for channel in guild.channels:
                    if channel.id in servers[f'{guild.id}']:
                        await channel.delete()
                with open('data/servers.json', 'w') as f:
                    servers.clear()
                    json.dump(servers, f, indent=4)
            else:
                await ctx.send(f'No Srift channels have been initialized yet.')


def setup(client):
    client.add_cog(Srift(client))
