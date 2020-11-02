import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound, MissingRequiredArgument

from parse import parse
import logging

from GameAPI import user_commands
from src.bugreport import BugReport
from GameAPI.Book import Book

from GameAPI.Queue import Queue
from StatsCmd.StatsCommandFile import StatsCommand

import tictactoe.GameLogic
import connectfour.Gamelogic
import hangman.GameLogic
import onewordchallange.GameLogic
from src.MoneyMiner import miner_commands

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)

client.add_cog(BugReport.BugReport(client))
client.add_cog(StatsCommand())
client.add_cog(user_commands.Commands(client))

# join-channelid -> Spieleklasse, Queuename, (Queue)
games = {
    743463967996903496: [hangman.GameLogic.GameControl, "Galgenmännchen"],
    741835475085557860: [tictactoe.GameLogic.GameControl, "TicTacToe"],
    743425069216170024: [connectfour.Gamelogic.GameControl, "VierGewinnt"],
    771386889927262248: [onewordchallange.GameLogic.GameControl, "OneWordChallange"]
}


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


client.remove_command("help")


@client.command()
async def help(ctx: commands.Context):
    await ctx.message.delete()
    if ctx.channel.id == 771745879723606107:
        page1 = "Hey! Schön das du auf diesen Server gefunden hast!!\nKleiner Tipp schalte diesen Server bis auf Erwähnungen stumm, damit du nicht mit Nachrichten vollgespamt wirst :-)"
        page2 = "Wenn du spielen willst gehe zu dem jeweiligen Channel und schreibe !join um mitzuspielen"
        page3 = "Um Statistiken von dir bzw. von anderen zu sehen gehe in den Stats channel und schreibe !stats [Spielername]"
        page4 = 'Willst du Haustiere gewinnen um tolle Xp-Multiplikatoren oder Money-Multiplikatoren zu bekommen? Gehe in den Haustier Channel und schreibe !pet (kostet anfangs 200 Money). Deine Haustiere kannst du sehen indem du im Haustier Channel !pets schreibst!'
        page5 = 'Wenn du einen Bug gefunden hast schreibe bitte folgendes in den Bug-Report Channel: !bug "your message"! Thanks for helping :-) !'
        page6 = 'Auf den nächsten Seiten wird erklärt wie die jeweiligen Spiele funktionieren! ->'
        page7 = 'TicTacToe:\nWie man ein Feld anklickt wird im Spiel erklährt!\nWas ist TicTacToe?:\nEin 3x3 Spielfeld auf dem du versuchen musst 3 Felder in einer Reihe mit deiner Spielfigur zu markieren!'
        page8 = 'Vier Gewinnt:\nEin Großes Spielfeld, in dem du versuchen musst 4 Spielsteine deiner Farbe in einer Reihe zu haben!'
        page9 = 'Hangman:\nEin zufällig ausgewählter Spieler sucht sich ein Wort aus, welches die anderen Erraten müssen! Wenn die Spieler zu oft einen falschen Buchstaben ausprobiert haben ist das Spiel vorbei!'
        page9 = 'MoneyMiner:\nBekomme Geld über deine Spitzhacke und erweitere deinen Rucksack um mehr speichern zu können! Mache !upgrade pickaxe/pa/spitzhacke/rucksack/backpack/bp um upgraden zu können! Benutze !bp/backpack/rucksack um dir Informationen über den Rucksack' \
                ' anzeigen zu lassen! Schreibe !pa/pickaxe/spitzhacke um dir Informationen über die Spitzhacke anzeigen zu lassen!'
        page10 = 'OneWordChallange:\nDer Reihe nach müssen die Spieler wörter aussuchen und daraus einen Satz bilden!'
        book = Book("Help", [page1, page2, page3, page4, page5, page6, page7, page8, page9, page10], client, 771745879723606107)
        await book.send_message()

# Der Chef darf Channels purgen:
@client.command()
async def purge(ctx: commands.Context, *, member: discord.Member = None):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        return
    await ctx.message.delete()
    role = discord.utils.get(ctx.guild.roles, id=744630374855868456)
    if role in ctx.author.roles:
        if isinstance(ctx.channel, discord.channel.TextChannel):
            await ctx.channel.purge()




# Neue User im Welcome Channel begrüßen:
@client.event
async def on_member_join(member: discord.Member):
    channel = client.get_channel(741965363549569034)
    await channel.send(f"""Wilkommen auf **PD-GAMEWORLD** {member.mention} !""")


# Nicht existierende oder fehlerhafte Commands werden aus dem Channel gelöscht:
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        try:
            await ctx.message.delete()
        except:
            pass
        return
    elif isinstance(error, MissingRequiredArgument):
        try:
            await ctx.message.delete()
        except:
            pass
        return
    else:
        raise error


# Aufräumen beim Start:
@client.event
async def on_ready():
    # Alte Gamechannels löschen:
    for channel in client.get_all_channels():
        if parse("{}-{:d}", channel.name):
            logging.info("delete " + channel.name)
            await channel.delete()
    # Inhalt der Join Channels löschen:
    for channelid in games:
        channel = client.get_channel(channelid)
        logging.info("cleanup " + channel.name)
        await channel.purge()

    deletechannels = [771745879723606107, 741835965164814458, 772214299997110292, 743797646883553370, 772515089181310977, 772543056640868404, 772543093714714666]
    for channelid in deletechannels:
        channel = client.get_channel(channelid)
        logging.info("cleanup " + channel.name)
        await channel.purge()

    # Erzeugen der GameQueues und Spielekontrollobjekt koppeln:
    for channelid in games:
        gamequeue = Queue(games[channelid][1], client.get_channel(channelid))  # Queue erzeugen und Namen zuweisen
        games[channelid].append(gamequeue)  # Die Queue dem Join Channel zuordnen
        games[channelid][0](gamequeue)  # Gamecontroller des Spiels erzeugen, queue übergeben

    client.add_cog(miner_commands.MineCommands(client))


with open("../resources/privates.txt") as token_file:
    token = token_file.readline()

client.run(token)
