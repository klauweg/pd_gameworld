import discord
from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument, CommandNotFound

import logging


loggger = logging.getLogger("myclient")

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)

# Nicht existierende oder fehlerhafte Commands werden aus dem Channel gelöscht:
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        try:
            await ctx.message.delete()
        except:
            pass
        return
    elif isinstance(error, MissingRequiredArgument):
        try:
            await ctx.message.delete()
        except:
            pass
        return
    else:
        raise error

