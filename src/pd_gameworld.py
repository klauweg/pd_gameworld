import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound, MissingRequiredArgument

from parse import parse
from ClearCmd.ClearCommand import ClearCommand
from GameAPI.Queue import Queue
from StatsCmd.StatsCommandFile import StatsCommand
from bugreport.BugReport import BugReport

#from tictactoe.GameLogic import TicTacToeGameLogic
from connectfour.Gamelogic import GameControl as connectfour_GameControl
#from hangman.GameLogic import HangManGameLogic

client = commands.Bot(command_prefix="!")

# join-channelid -> Spieleklasse
games = {
#    743463967996903496: [HangManGameLogic],
#    741835475085557860: [TicTacToeGameLogic],
    743425069216170024: [connectfour_GameControl]
}


# Erzeugen der GameQueues und Spielekontrollobjekt koppeln:
for channelid in games:
    gamequeue = Queue()  # Queue erzeugen
    games[channelid].append(gamequeue) # Die Queue dem Join Channel zuordnen
    games[channelid][0](gamequeue) # Spiel mit Kopplung an die Queue erzeugen
    
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

@client.event
async def on_ready():
    # Alte Gamechannels löschen:
    for channel in client.get_all_channels():
        if parse("{}-{:d}", channel.name):
            await channel.delete()
    for channelid in games:
        await client.get_channel(channelid).purge()

client.add_cog(ClearCommand())

token_file = open("../resources/privates.txt")
client.run(token_file.readline())



