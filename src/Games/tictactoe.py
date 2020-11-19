# TODO: Member Objekte werden manchmal direkt verglichen, manchmal per ID. Was ist besser?

import logging
logger = logging.getLogger("tictactoe")

from discord.ext import commands
import discord
from PIL import Image
import io, random, asyncio

################# User Modules:
from Gadgets.user_extension import add_xp, add_to_stats, deposit_money
from myclient import client, MyEmbed

fieldmap={ "A1":0, "B1":1, "C1":2,
           "A2":3, "B2":4, "C2":5,
           "A3":6, "B3":7, "C3":8 }

# Spielklasse
# Parameter:
# <channel> Kanal in dem das Spiel stattfindet
# <players> Liste der Spieler, index 0 ist der Initiator des Spiels
class Game():
    def __del__(self): # for debug only
        logger.info("Game Object has been destroyed.")
        
    def __init__(self, channel, players):
        self.gamechannel = channel
        self.players = players
        self.playfield_message = None
        self.queue = asyncio.Queue()
        self.game_task = asyncio.create_task( self.game() )
        client.add_listener(self.on_message)
        logger.info("Game has been started.")

    # Beenden des Spiels:
    async def destroygame( self ):
        logger.info("Spiel wird beendet.")
        for player in self.players:
            add_to_stats(player, "TicTacToe", 0, 1, 0)
            add_xp(player, 5)
        client.remove_listener(self.on_message)
        logger.info("Before Task Cancel")
        self.game_task.cancel()
        logger.info("After Task Cancel")
        # Hier muss irgend ein await stehen, damit sich der Task
        # noch selbst canceln kann:
        await asyncio.sleep(1)
        logger.error("This shouldn't never ever happen!")
        
    # MSG handler:
    async def on_message(self, message):
        if message.channel.id != self.gamechannel.id:
            return # Die Nachricht war nicht aus unserem Channel
        if message.author.id == client.user.id:
            return # Nachrichten vom BOT werden ignoriert
        # Nachrichten in die Queue zum Game Task schreiben:
        await self.queue.put( message )
        
        
    # Eigentlicher Game Task:
    async def game( self ):
        # Genug Spieler?
        if len(self.players) < 2:
            await self.msg_tooFewPlayers()
            await self.destroygame()
        # Spieler auswählen:
        self.players = [ self.players[0], random.choice( self.players[1:] ) ]
        self.currentPlayer = random.choice( (0,1) )
        # Spielfeld vorbereiten:
        self.playfield = 9*[None]
        # Spieler begrüßen und Spielfeld erstmalig ausgeben:
        await self.msg_gameInstructions()
        await self.msg_playfield()
        
        # Start Game, Wait for Messages with Timeout:
        while True:
            try:
                message = await asyncio.wait_for(self.queue.get(), timeout=60*5)
            except asyncio.TimeoutError:
                logger.info("Timeout")
                await self.msg_timeout()
                await self.destroygame() #EXIT

            if message.content.lower() == "leave":
                if message.author.id in [ player.id for player in self.players]:
                    await message.delete()
                    await self.msg_leave( message.author.name )
                    self.players.remove( message.author )
                    await self.destroygame() #EXIT

            # Gültige Spielfeldpositionseingabe?
            id = fieldmap.get( message.content.upper() )
            if id != None:
                await message.delete()
                # Richtiger Spieler?
                if message.author.id != self.players[self.currentPlayer].id:
                    await self.msg_wrongPlayer()
                    continue
                # Ist das Feld noch frei?
                if self.playfield[ id ] != None:
                    await self.msg_occupied()
                    continue

                self.playfield[id] = self.currentPlayer # Markierung setzen
                await self.msg_playfield()

                result = self.compute_winner()
                
                if result == True: # Einer hat gewonnen
                    await self.msg_won( self.players[self.currentPlayer].name )
                    add_xp(self.players[self.currentPlayer], 20)
                    add_to_stats(self.players[self.currentPlayer], "TicTacToe", 1, 0, 0)
                    deposit_money(self.players[self.currentPlayer], 10)
                    await self.destroygame()
                elif result == "pat": # Unentschieden
                    await self.msg_pat()
                    for player in self.players:
                        add_to_stats(player, "TicTacToe", 0, 0, 1)
                    await self.destroygame()
                else: # Geht noch weiter, Spieler wechseln
                    self.currentPlayer = 0 if self.currentPlayer == 1 else 1


    # Durchsucht das Spielfeld nach drei gleichen Marken in einer Reihe
    def compute_winner(self):
        gf = self.playfield
        alle_gleich = lambda x,y,z: ( gf[x] == gf[y] ) and ( gf[y] == gf[z] ) and ( gf[x] != None )
        lines = ( (0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (6,4,2) )
        
        for line in lines: # Linien absuchen
            if alle_gleich( *line ): # einer hat gewonnen
                return True

        if not None in self.playfield: # Unentschieden
            return "pat"
        
########################################################################################
    # Zu sendende Nachrichten:
    async def msg_pat(self):
        embed = discord.Embed(
           title=":tada: Unentschieden :tada:",
           colour=discord.Colour.green())
        await self.gamechannel.send(embed=embed)
        
    async def msg_won(self, name):
        embed = discord.Embed(
           title=":tada: Player " + name + " hat gewonnen :tada:",
           colour=discord.Colour.green())
        await self.gamechannel.send(embed=embed)

    async def msg_wrongPlayer(self):
        embed = discord.Embed(
            title=":loudspeaker: Du bist nicht dran :loudspeaker:",
            colour=discord.Colour.red())
        await self.gamechannel.send(embed=embed, delete_after=2)
        
    async def msg_occupied(self):
        embed = discord.Embed(
            title=":loudspeaker: Kein erlaubtes Feld :loudspeaker:",
            colour=discord.Colour.red())
        await self.gamechannel.send(embed=embed, delete_after=2)
            
    async def msg_leave(self, name):
        embed = discord.Embed(
            title="Das Spiel wird beendet, weil " +
                    name + " keine Lust mehr hat.",
            colour=discord.Colour.green())
        await self.gamechannel.send(embed=embed)
        
    async def msg_timeout(self):
        embed = discord.Embed(title="Game Gestoppt:",
           description="(Timeout)", color=0x58ff46)
        embed.set_author(name="TicTacToe")
        await self.gamechannel.send(embed=embed, delete_after=7)

    async def msg_tooFewPlayers(self):
        embed = MyEmbed(name="TicTacToe Game",
           title="Fehler",
           description="Das Spiel braucht mindestens zwei Spieler "
             "oder mehr aus denen dann zufällig gewählt wird.",
           color=0xFF0000)
        await self.gamechannel.send(embed=embed, delete_after=10)            
    
    async def msg_gameInstructions(self):
        current_player = self.players[self.currentPlayer].display_name
        embed = MyEmbed( name="TicTacToe",
                         title="Also, "+current_player+" bitte beginne!",
                         description="", color=0x58ff46)
        embed.add_field(name="Wie wähle ich ein Feld aus?",
                        value="A1   B1   C1\n"
                             +"A2  B2  C2\n"
                             +"A3  B3  C3",
                        inline=True)
        embed.add_field(name="Und jetzt?",
                        value="Schreibe das gewählte Feld in den Channel!",
                        inline=True)
        await self.gamechannel.send(embed=embed, delete_after=30)

    async def msg_playfield(self):
        field_img = Image.open("../resources/tictactoe/gamefield_universe.png")
        marker_imgs = ( Image.open("../resources/tictactoe/o_universe.png"),
                        Image.open("../resources/tictactoe/x_universe.png") )
        coords = [(12, 12), (175, 12), (337, 12),
                  (12, 175), (175, 175), (337, 175),
                  (12, 337), (175, 337), (337, 337)]
        for fieldno in range(0,9):
            if self.playfield[fieldno] is not None: # Feld besetzt?
                symbol = marker_imgs[ self.playfield[ fieldno ] ]
                field_img.paste( symbol, coords[fieldno], symbol )
        arr = io.BytesIO()
        field_img.save(arr, format="png")
        arr.seek(0)
        file = discord.File(arr)
        file.filename = "field.png"
        if self.playfield_message:
            await self.playfield_message.delete()
        self.playfield_message = await self.gamechannel.send(file=file)
        
