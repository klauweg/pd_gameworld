# TODO: Member Objekte werden manchmal direkt verglichen, manchmal per ID. Was ist besser?

import logging
logger = logging.getLogger("tictactoe")

from discord.ext import commands
import discord
from PIL import Image
import io, random, asyncio

################# User Modules:
from Gadgets.user_extension import add_xp, add_to_stats, deposit_money
from myclient import MyEmbed

fieldmap={ "A1":0, "B1":1, "C1":2,
           "A2":3, "B2":4, "C2":5,
           "A3":6, "B3":7, "C3":8 }

class Game():
    def __del__(self): # for debug only
        logger.info("Game Object has been destroyed.")
        
    def __init__(self, bot, channel, players):
        self.bot = bot
        self.gamechannel = channel
        # 1. und zufälligen weiteren Player auswählen:
        self.players = players[0], random.choice( players[1:] )
        # Wer fängt an?
        self.currentPlayer = random.choice( (0,1) )
        # Das eigentliche Spielfeld:
        self.playfield = 9*[None]
        self.playfield_message = None
        
        self.bot.add_listener(self.on_message)
        self.trigger = asyncio.Event()
        self.lock = asyncio.Lock()
        self.game_task = asyncio.create_task( self.game() )
        logger.info("Game has been started.")

    # Beenden des Spiels, Aufräumen kann auch von Extern für Abbruch aufgerufen werden:
    def endgame( self ):
        logger.info("Spiel wird beendet.")
        for player in self.players:
            add_to_stats(player, "TicTacToe", 0, 1, 0)
            add_xp(player, 5)
        self.game_task.cancel()
        self.bot.remove_listener(self.on_message)
        
        
    # MSG dispatcher (hier ist auch die eigentliche Spiellogik)
    async def on_message(self, message):
        if message.channel.id != self.gamechannel.id:
            return # Die Nachricht war nicht aus unserem Channel
        if message.author.id == self.bot.user.id:
            return # Nachrichten vom BOT werden ignoriert

        await message.delete() # Nachricht im discord Channel löschen

        async with self.lock: # Immer nur eine Msg gleichzeitig
            self.trigger.set() # prevent timeout
            # Leave Befehl:
            if message.content.lower() == "leave" and message.author in self.players:
                embed = discord.Embed(title="Das Spiel wird beendet, weil " +
                         message.author.name + " keine Lust mehr hat.",
                         colour=discord.Colour.green())
                await self.gamechannel.send(embed=embed)
                self.endgame()
                return # Ein spieler hat das Spiel verlassen

            # richtiger Spieler?
            if message.author.id != self.players[self.currentPlayer].id:
                return # Falscher Spieler

            # Ist die Eingabe eine Spielfeldkoordinate?
            id = fieldmap.get( message.content.upper() )
            if id == None: # Obacht: "0" ist auch "False"
                return # Der String ist keine Spielfeldkoordinate

            if self.playfield[ id ] != None: # Das Feld ist schon benutzt
                embed = discord.Embed(title=":loudspeaker: Kein erlaubtes Feld :loudspeaker:",
                                      colour=discord.Colour.red())
                await self.gamechannel.send(embed=embed, delete_after=2)
                return # Das Feld war schon besetzt

            self.playfield[id] = self.currentPlayer # Markierung setzen
            await self.send_playfield()

            result = self.compute_winner()
            if result == True: # Einer hat gewonnen
                embed = discord.Embed(title=":tada: Player " + 
                                self.players[self.currentPlayer].name +
                                " hat gewonnen :tada:",
                                colour=discord.Colour.green())
                await self.gamechannel.send(embed=embed)
                add_xp(self.players[self.currentPlayer], 20)
                add_to_stats(self.players[self.currentPlayer], "TicTacToe", 1, 0, 0)
                deposit_money(self.players[self.currentPlayer], 10)
                self.endgame()
            elif result == "pat": # Unentschieden
                embed = discord.Embed(title=":tada: Unentschieden :tada:",
                        colour=discord.Colour.green())
                await self.gamechannel.send(embed=embed)
                for player in self.players:
                    add_to_stats(player, "TicTacToe", 0, 0, 1)
                self.endgame()
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


    # Spielfeld neu erzeugen:
    async def send_playfield(self):
        if self.playfield_message:
            await self.playfield_message.delete()
        self.playfield_message = await self.gamechannel.send(file=self.build_board())
        
    def build_board(self):
        field_img: Image.Image = Image.open("../resources/tictactoe/gamefield_universe.png")
        o = Image.open("../resources/tictactoe/o_universe.png")
        X = Image.open("../resources/tictactoe/x_universe.png")
        fields = [(12, 12), (175, 12), (337, 12),
                  (12, 175), (175, 175), (337, 175),
                  (12, 337), (175, 337), (337, 337)]
        for fieldno in range(0,9):
            if self.playfield[fieldno] != None:
                symbol = X if self.playfield[fieldno]==0 else o
                field_img.paste( symbol, fields[fieldno], symbol )
        arr = io.BytesIO()
        field_img.save(arr, format="png")
        arr.seek(0)
        file = discord.File(arr)
        file.filename = "field.png"
        return file

    
    # Async Game Task, für Zeitsteuerung u.ä.:
    async def game( self ):
        logger.info("Timer started")
        # spiel initialisieren:
        async with self.lock:
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
            await self.send_playfield()
        # Wait for Timeout:
        while True:
            try:
                await asyncio.wait_for(self.trigger.wait(), timeout=60*5)
            except asyncio.TimeoutError:
                logger.info("Timeout")
                embed = discord.Embed(title="Game Gestoppt:", description="(Timeout)", color=0x58ff46)
                embed.set_author(name="TicTacToe")
                await self.gamechannel.send(embed=embed)
                self.endgame()

