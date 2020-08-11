from discord.ext import commands
from discord.ext.commands import CommandNotFound

from src.connectfour.Gamelogic import Gamelogic

bot = commands.Bot(command_prefix="!")

connectfour = Gamelogic(bot)
bot.add_cog(connectfour)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

bot.run("NzQyMDMyMDAzMTI1MzQ2MzQ0.XzANJw.M_1EwGyle3wi9d3yc4JzFqcENcY")


