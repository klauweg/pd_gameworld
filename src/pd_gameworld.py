import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound, MissingRequiredArgument

from ClearCmd.ClearCommand import ClearCommand
from GameAPI.Queue import Queue
from StatsCmd.StatsCommandFile import StatsCommand
from bugreport.BugReport import BugReport


#from tictactoe.GameLogic import TicTacToeGameLogic
import connectfour
#from hangman.GameLogic import HangManGameLogic

client = commands.Bot(command_prefix="!")

# join-channelid -> Spieleklasse
games = {
#    743463967996903496: [HangManGameLogic],
#    741835475085557860: [TicTacToeGameLogic],
    743425069216170024: [connectfour]
}

# Erzeugen der SpieleKontrollObjekte:
for channelid in games:
    gamequeue = Queue()  # Queue erzeugen
    games[channelid].append(gamequeue) # Die Queue dem Join Channel zuordnen
    games[channelid][0].GameControl(gamequeue) # Spiel mit Kopplung an die Queue erzeugen
    
# Jemand will einem Spiel joinen und landet in der Queue:
@client.command()
async def join(ctx: commands.Context):
    await ctx.message.delete()
    if ctx.channel.id in games:
        # ctx object in der queue speichern:
        queue = games[ctx.channel.id][1] #zugehörige queue zum Channel ermitteln
        await queue.append(ctx)


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

token_file = open("../resources/privates.txt")
client.run(token_file.readline())

