from discord.ext import commands

from src.connectfour.Gamelogic import Gamelogic

bot = commands.Bot(command_prefix="!")

connectfour = Gamelogic(bot)
bot.add_cog(connectfour)

bot.run("NzQyMDMyMDAzMTI1MzQ2MzQ0.XzANJw.M_1EwGyle3wi9d3yc4JzFqcENcY")


