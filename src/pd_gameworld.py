from discord.ext import commands
from tictactoe.GameLogic import TicTacToeGameLogic
client = commands.Bot(command_prefix="!")


@client.event
async def on_member_join(member):
    channel = client.get_channel(741965363549569034)
    await channel.send(f"""Welcome to the Server {member.mention} !""")

client.add_cog(TicTacToeGameLogic(client))
token_file = open("../resources/privates.txt")
client.run(token_file.readline())
