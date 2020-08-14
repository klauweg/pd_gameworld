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
    player: Player = Player(member.id, 0, PlayerStats())
    FileManager.add_player_data(player)
    await member.edit(nick=member.display_name + " [Lvl: " + str(
        FileManager.get_player_data(member.id).compute_level()) + "]")

client.add_cog(TicTacToeGameLogic(client))
client.add_cog(ConnectFourGameLogic(client))
client.add_cog(HangManGameLogic(client))
client.add_cog(BugReport(client))
token_file = open("../resources/privates.txt")
client.run(token_file.readline())
