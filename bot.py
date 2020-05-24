import discord
import os
from discord.ext import commands
from discord.errors import LoginFailure
from database.mongo import Mongo, SriftGuild
from utils.config import SriftConfig

token = SriftConfig().getParsedConfig().get('discord', 'token')
client = commands.Bot(command_prefix='>')
Mongo(
    SriftConfig().getParsedConfig().get('mongoengine', 'db'),
    SriftConfig().getParsedConfig().get('mongoengine', 'host'),
    SriftConfig().getParsedConfig().get('mongoengine', 'port')
).connect()


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
async def on_guild_join(guild):
    SriftGuild(
        guild_id=guild.id,
        initialized=False
    ).save()


@client.event
async def on_guild_remove(guild):
    SriftGuild.objects(guild_id=guild.id).delete()


@client.event
async def on_ready():
    print('Bot ist ready!')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

try:
    client.run(token)
except LoginFailure as loginerr:
    print(str(loginerr) + ' Please edit the config.ini file.')
