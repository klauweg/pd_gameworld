from discord.ext import commands
from connectfour.Gamelogic import ConnectFourGameLogic
from tictactoe.GameLogic import TicTacToeGameLogic
from discord.ext.commands import CommandNotFound
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
token_file = open("../resources/privates.txt")
client.run(token_file.readline())
