import discord
import os
from discord.ext import commands


def read_token():
    if os.path.isfile('data/token.txt'):
        with open('data/token.txt', 'r+') as f:
            if os.path.getsize('data/token.txt') == 0:
                f.write("- Change this line to your discord bot token -")
    else:
        with open('data/token.txt', 'w') as f:
            f.write("- Change this line to your discord bot token -")

    with open('data/token.txt', 'r') as f:
        lines = f.readlines()

    if lines[0] == "- Change this line to your discord bot token -":
        print('Edit data/token.txt file and restart the bot!')
        return None
    else:
        return lines[0].strip()


token = read_token()

client = commands.Bot(command_prefix='>')


@client.command(hidden=True)
@commands.has_guild_permissions(administrator=True)
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    print(f'Extension {extension} loaded by {ctx.author}')
    await ctx.send(f'Extension {extension} loaded.')


@client.command(hidden=True)
@commands.has_guild_permissions(administrator=True)
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    print(f'Extension {extension} unloaded by {ctx.author}')
    await ctx.send(f'Extension {extension} unloaded')


@client.command(hidden=True)
@commands.has_guild_permissions(administrator=True)
async def reload(ctx, extension=None):
    if extension is None:
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                client.reload_extension(f'cogs.{filename[:-3]}')
        print(f'All Extensions reloaded by {ctx.author}')
        await ctx.send(f'All Extensions reloaded.')
    else:
        client.reload_extension(f'cogs.{extension}')
        print(f'Extension {extension} reloaded by {ctx.author}')
        await ctx.send(f'Extension {extension} reloaded.')


@client.command(hidden=True)
@commands.has_guild_permissions(administrator=True)
async def quit(ctx):
    print(f'Bot stopped by {ctx.author}')
    await ctx.send(f'Stopping Srift Bot.')
    await client.close()


@load.error
async def load_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.message.add_reaction('\U000026D4')


@unload.error
async def unload_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.message.add_reaction('\U000026D4')


@reload.error
async def reload_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.message.add_reaction('\U000026D4')


@quit.error
async def quit_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.message.add_reaction('\U000026D4')


@client.event
async def on_connect():
    print('Srift Bot is connected to Discord')


@client.event
async def on_ready():
    print('Bot ist ready!')
    if os.path.isfile('data/data.json'):
        with open('data/data.json', 'r+') as f:
            if os.path.getsize('data/data.json') == 0:
                f.write("{}")
    else:
        with open('data/data.json', 'w') as f:
            f.write("{}")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

if token is not None:
    client.run(token)
