import discord
import os
from discord.ext import commands


def read_token():
    with open('data/token.txt', 'r') as f:
        lines = f.readlines()
    return lines[0].strip()


token = read_token()

client = commands.Bot(command_prefix='>')


@client.command(hidden=True)
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'Extension {extension} loaded.')


@client.command(hidden=True)
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send(f'Extension {extension} unloaded')


@client.command(hidden=True)
async def reload(ctx, extension=None):
    if extension is None:
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                client.reload_extension(f'cogs.{filename[:-3]}')
                await ctx.send(f'All Extensions reloaded.')
    else:
        client.reload_extension(f'cogs.{extension}')
        await ctx.send(f'Extension {extension} reloaded.')


@client.command(hidden=True)
async def quit(ctx):
    await ctx.send(f'Stopping Srift Bot.')
    await client.close()


@client.event
async def on_connect():
    print('Srift Bot is connected to Discord')


@client.event
async def on_ready():
    print('Bot ist ready!')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


client.run(token)
