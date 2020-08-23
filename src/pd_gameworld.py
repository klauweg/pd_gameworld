import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound, MissingRequiredArgument

from parse import parse
import logging

from GameAPI.PlayerDataApi import Utils
from GameAPI.Queue import Queue
from StatsCmd.StatsCommandFile import StatsCommand
from bugreport.BugReport import BugReport

import tictactoe.GameLogic
import connectfour.Gamelogic
import hangman.GameLogic

logging.basicConfig(level=logging.INFO)

client = commands.Bot(command_prefix="!")

client.add_cog(StatsCommand())

# join-channelid -> Spieleklasse, Queuename, (Queue)
games = {
    743463967996903496: [hangman.GameLogic.GameControl, "HangMan" ],
    741835475085557860: [tictactoe.GameLogic.GameControl, "TicTacToe" ],
    743425069216170024: [connectfour.Gamelogic.GameControl, "ConnectFour" ]
}


# Erzeugen der GameQueues und Spielekontrollobjekt koppeln:
for channelid in games:
    gamequeue = Queue( games[channelid][1] )  # Queue erzeugen und Namen zuweisen
    games[channelid].append(gamequeue) # Die Queue dem Join Channel zuordnen
    games[channelid][0]( gamequeue ) # Gamecontroller des Spiels erzeugen, queue übergeben

    
# Jemand will einem Spiel joinen und landet in der Queue:
@client.command()
async def join(ctx: commands.Context):
    await ctx.message.delete()
    if ctx.channel.id in games:
        queue = games[ctx.channel.id][2]
        await queue.append(ctx)

        
# Jemand will eine Queue verlassen:
@client.command()
async def leave(ctx: commands.Context):
    await ctx.message.delete()
    if ctx.channel.id in games:
        queue = games[ctx.channel.id][2]
        await queue.remove(ctx)


# Der Chef darf Channels purgen:
@client.command()
async def purge(ctx: commands.Context, *, member: discord.Member = None):
    role = discord.utils.get(ctx.guild.roles, id=744630374855868456)
    if role in ctx.author.roles:
        await ctx.channel.purge()


# Neue User im Welcome Channel begrüßen:
@client.event
async def on_member_join(member: discord.Member):
    channel = client.get_channel(741965363549569034)
    await channel.send(f"""Welcome to the Server {member.mention} !""")

    
# Nicht existierende oder fehlerhafte Commands werden aus dem Channel gelöscht:
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.message.delete()
        return
    if isinstance(error, MissingRequiredArgument):
        await ctx.message.delete()
        return
    raise error


# Aufräumen beim Start:
@client.event
async def on_ready():
    # Alte Gamechannels löschen:
    for channel in client.get_all_channels():
        if parse("{}-{:d}", channel.name):
            logging.info( "delete "+channel.name )
            await channel.delete()
    # Inhalt der Join Channels löschen:
    for channelid in games:
        channel = client.get_channel(channelid)
        logging.info( "cleanup "+channel.name )
        await channel.purge()

        
with open("../resources/privates.txt") as token_file:
    token = token_file.readline()
client.run(token)

