import discord
from discord.ext import commands

from GameAPI.utils import FileManager
from GameAPI.utils.Players import Player, PlayerStats
from tictactoe.GameLogic import TicTacToeGameLogic
client = commands.Bot(command_prefix="!")


@client.event
async def on_member_join(member: discord.Member):
    channel = client.get_channel(741965363549569034)
    await channel.send(f"""Welcome to the Server {member.mention} !""")
    player: Player = Player(member.id, 0, PlayerStats())
    FileManager.add_player_data(player)

client.add_cog(TicTacToeGameLogic(client))
token_file = open("../resources/privates.txt")
client.run(token_file.readline())
