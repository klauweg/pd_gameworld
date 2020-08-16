import discord
from discord.ext import commands

from GameAPI.PlayerAPI import FileManager
from GameAPI.PlayerAPI.Players import Player, PlayerStats
from bugreport.BugReport import BugReport
from tictactoe.GameLogic import TicTacToeGameLogic
from connectfour.Gamelogic import ConnectFourGameLogic
from hangman.GameLogic import HangManGameLogic
client = commands.Bot(command_prefix="!")


@client.event
async def on_member_join(member: discord.Member):
    channel = client.get_channel(741965363549569034)
    await channel.send(f"""Welcome to the Server {member.mention} !""")

client.add_cog(TicTacToeGameLogic(client))
client.add_cog(ConnectFourGameLogic(client))
client.add_cog(HangManGameLogic(client))
client.add_cog(BugReport(client))
token_file = open("../resources/privates.txt")
client.run(token_file.readline())
