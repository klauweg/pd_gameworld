import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound, MissingRequiredArgument

from ClearCmd.ClearCommand import ClearCommand
from StatsCmd.StatsCommandFile import StatsCommand
from bugreport.BugReport import BugReport
from tictactoe.GameLogic import TicTacToeGameLogic
from connectfour.Gamelogic import ConnectFourGameLogic
from hangman.GameLogic import HangManGameLogic
client = commands.Bot(command_prefix="!")
current_playing_players = []


@client.event
async def on_member_join(member: discord.Member):
    channel = client.get_channel(741965363549569034)
    await channel.send(f"""Welcome to the Server {member.mention} !""")

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.message.delete()
        return
    if isinstance(error, MissingRequiredArgument):
        await ctx.message.delete()
        return
    raise error

client.add_cog(TicTacToeGameLogic(client, current_playing_players))
client.add_cog(ConnectFourGameLogic(client, current_playing_players))
client.add_cog(HangManGameLogic(client, current_playing_players))
client.add_cog(BugReport(client))
client.add_cog(StatsCommand(client))
client.add_cog(ClearCommand(client))
token_file = open("../resources/privates.txt")
client.run(token_file.readline())
