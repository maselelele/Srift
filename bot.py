import discord
import os
from discord.ext import commands


def read_token():
    with open('token.txt', 'r') as f:
        lines = f.readlines()
    return lines[0].strip()


token = read_token()

client = commands.Bot(command_prefix='>')


@client.command(hidden=True)
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    ctx.send(f'Extension {extension} loaded.')


@client.command(hidden=True)
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    ctx.send(f'Extension {extension} unloaded')


@client.command(hidden=True)
async def reload(ctx, extension):
    client.reload_extension(f'cogs.{extension}')
    ctx.send(f'Extension {extension} reloaded.')


for filename in os.listdir('./cogs'):
    if filename.endwith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


client.run(token)
