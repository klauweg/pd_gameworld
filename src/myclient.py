import logging
logger = logging.getLogger("myclient")

import discord
from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument, CommandNotFound
import sys
import traceback

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
        logger.warn('Ignoring exception in command "{}":'.format(ctx.command))
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


class MyEmbed( discord.Embed ):
    def __init__( self, *args, name="", **kwargs ):
        super().__init__( *args, **kwargs )
        self.set_thumbnail(url="https://cdn.discordapp.com/app-icons/"
                "742032003125346344/"
                "e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        self.set_author(name=name, icon_url="https://cdn.discordapp.com/"
               "app-icons/742032003125346344/"
               "e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
