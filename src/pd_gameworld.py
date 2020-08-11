from discord.ext import commands
from discord.ext.commands import CommandNotFound
from src.connectfour.Gamelogic import ConnectFourGameLogic
from src.tictactoe.GameLogic import TicTacToeGameLogic
client = commands.Bot(command_prefix="!")


@client.event
async def on_member_join(member):
    channel = client.get_channel(741965363549569034)
    await channel.send(f"""Welcome to the Server {member.mention} !""")

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

client.add_cog(ConnectFourGameLogic(client))
client.add_cog(TicTacToeGameLogic(client))
token_file = open("resurces/privates.txt")
client.run(token_file.readline())





