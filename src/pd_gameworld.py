import logging
logging.basicConfig( level=logging.INFO )
logger = logging.getLogger("main")

import discord
from discord.ext import commands
import sys
logger.info( "Module search path: " + str(sys.path) )

# ############### User Modules:
from myclient import client
import Gadgets.user_commands
from Gadgets.Book import Book

client.remove_command("help")
@client.command()
async def help(ctx: commands.Context):
    await ctx.message.delete()
    if ctx.channel.id == 771745879723606107:
        page1 = "Hey! Schön das du auf diesen Server gefunden hast!!\nKleiner Tipp schalte diesen Server bis auf Erwähnungen stumm, damit du nicht mit Nachrichten vollgespamt wirst :-)"
        page2 = "Wenn du spielen willst gehe zu dem jeweiligen Channel und schreibe !join um mitzuspielen"
        page3 = "Kein Bock mehr auf ein Spiel, aber du bist schon in der Queue? Einfach !leave um die Queue zu verlassen!"
        page4 = "Um Statistiken von dir bzw. von anderen zu sehen gehe in den Stats-Channel und schreibe !stats [Spielername]"
        page5 = 'Du willst den Server boosten? gehe in den booster channel und schreibe !booster [xp/money] um xp bzw. money für 2h 1.25x zu boosten (kostet anfangs 100)'
        page6 = 'Willst du Haustiere gewinnen um tolle Xp-Multiplikatoren oder Money-Multiplikatoren zu bekommen? Gehe in den Haustier Channel und schreibe !pet (kostet anfangs 300 Money). Deine Haustiere kannst du sehen indem du im Haustier Channel !pets schreibst!'
        page7 = 'Wenn du einen Bug gefunden hast schreibe bitte folgendes in den Bug-Report Channel: !bug "dein bug"! Danke für deine Hilfe:-) !'
        page8 = 'Auf den nächsten Seiten wird erklärt wie die jeweiligen Spiele funktionieren! ->'
        page9 = 'TicTacToe:\nWie man ein Feld anklickt wird im Spiel erklährt!\nWas ist TicTacToe?:\nEin 3x3 Spielfeld auf dem du versuchen musst 3 Felder in einer Reihe mit deiner Spielfigur zu markieren!'
        page10 = 'Vier Gewinnt:\nEin Großes Spielfeld, in dem du versuchen musst 4 Spielsteine deiner Farbe in einer Reihe zu haben!'
        page11 = 'Hangman:\nEin zufällig ausgewählter Spieler sucht sich ein Wort aus, welches die anderen Erraten müssen! Wenn die Spieler zu oft einen falschen Buchstaben ausprobiert haben ist das Spiel vorbei!'
        page12 = 'MoneyMiner:\nBekomme Geld über deine Spitzhacke und erweitere deinen Rucksack um mehr speichern zu können! Mache !upgrade pickaxe/pa/spitzhacke/rucksack/backpack/bp um upgraden zu können! Benutze !bp/backpack/rucksack um dir Informationen über den Rucksack' \
                ' anzeigen zu lassen! Schreibe !pa/pickaxe/spitzhacke um dir Informationen über die Spitzhacke anzeigen zu lassen!  Zum schluss noch !claim um dein Geld vom Rucksack auf dein Konto zu übertragen!'
        page13 = 'OneWordChallange:\nDer Reihe nach müssen die Spieler wörter aussuchen und daraus einen Satz bilden!'
        book = Book("Help", [page1, page2, page3, page4, page5, page6, page7, page8, page9, page10, page11, page12, page13], client, 771745879723606107)
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

# Aufräumen beim Start:
@client.event
async def on_ready():
    deletechannels = [771745879723606107, 741835965164814458, 772214299997110292, 743797646883553370, 772515089181310977, 772543056640868404, 772543093714714666, 773486403073736735, 773486430047305728]
    for channelid in deletechannels:
        channel = client.get_channel(channelid)
        logger.info("cleanup " + channel.name)
        await channel.purge()

    helpchannel = client.get_channel(771745879723606107)
    embed = discord.Embed(title="Hilfe gefällig?",
                          description="!help für die detaillierte Hilfe von diesem Server!",
                          color=0x00FF00)
    embed.set_author(name="Help",
                     icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
    await helpchannel.send(embed=embed)

# Start Client:
with open("../resources/privates.txt") as token_file:
    token = token_file.readline()
client.run(token)