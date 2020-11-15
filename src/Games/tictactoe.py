import logging
logger = logging.getLogger("tictactoe")

from discord.ext import commands, tasks
import discord
from PIL import Image
import io

fields = {
            "A1": 0, "B1": 1, "C1": 2,
            "A2": 3, "B2": 4, "C2": 5,
            "A3": 6, "B3": 7, "C3": 8
        }
        
################# User Modules:
from Gadgets.user_extension import add_xp, add_to_stats, deposit_money

class Game(commands.Cog):
    def __del__(self):
        logger.info("Game has been destroyed.")
        
    def __init__(self, bot, channel, players):
        self.bot = bot
        self.gamechannel = channel
        self.players = players

        self.placedFields = {
            0: 0, 1: 0, 2: 0,
            3: 0, 4: 0, 5: 0,
            6: 0, 7: 0, 8: 0
        }
        self.currentPlayer = 0
        self.gamefield_message = None
        
        self.bot.add_cog(self)
        logger.info("Game has been started.")

        
    async def endgame( self ):
        logger.info("Endgame.")
        for player in self.players:
            add_to_stats(player, "TicTacToe", 0, 1, 0)
            add_xp(player, 5)
        self.bot.remove_cog(self)
        
        
    def is_undecided(self):
        if 0 in list(self.placedFields.values()):
            return False
        else:
            return True

    def compute_winner(self, playeri):
        won = playeri * 3
        # winning possibilities
        on_top = self.placedFields[0] + self.placedFields[1] + self.placedFields[2]
        below = self.placedFields[6] + self.placedFields[7] + self.placedFields[8]
        left = self.placedFields[0] + self.placedFields[3] + self.placedFields[6]
        right = self.placedFields[2] + self.placedFields[5] + self.placedFields[8]
        middle_top = self.placedFields[1] + self.placedFields[4] + self.placedFields[7]
        middle_left = self.placedFields[3] + self.placedFields[4] + self.placedFields[5]
        below = self.placedFields[6] + self.placedFields[7] + self.placedFields[8]
        diagonal_right = self.placedFields[6] + self.placedFields[4] + self.placedFields[2]
        diagonal_left = self.placedFields[8] + self.placedFields[4] + self.placedFields[0]
        # winner check
        if middle_top == won or middle_left == won or on_top == won or below == won or left == won or right == won or diagonal_right == won or diagonal_left == won:
            return True
        else:
            return False

        
    async def send_gamefield(self):
        if self.gamefield_message:
            await self.gamefield_message.delete()
        self.gamefield_message = await self.gamechannel.send(file=self.build_board(self.placedFields))
        

    def build_board(self, placedFields: dict):
        field_img: Image.Image = Image.open("../resources/tictactoe/gamefield_universe.png")
        o = Image.open("../resources/tictactoe/o_universe.png")
        X = Image.open("../resources/tictactoe/x_universe.png")
        fields = [(12, 12), (175, 12), (337, 12),
                  (12, 175), (175, 175), (337, 175),
                  (12, 337), (175, 337), (337, 337)]
        for x in list(placedFields.keys()):
            if placedFields[x] == -1:
                field_img.paste(X, fields[list(placedFields).index(x)],X)
            elif placedFields[x] == 1:
                field_img.paste(o, fields[list(placedFields).index(x)],o)
        arr = io.BytesIO()
        field_img.save(arr, format="png")
        arr.seek(0)
        file = discord.File(arr)
        file.filename = "field.png"
        return file

    
    @commands.command()
    async def leave(self, ctx: commands.Context, *args):
        logger.info("Leave called.")
        if ctx.channel.id != self.gamechannel.id:
            return # Die Nachricht war nicht aus unserem Channel
        if ctx.author.id == self.bot.user.id:
            return # Nachrichten vom BOT werden ignoriert
        await self.endgame()
        
            
    @tasks.loop(seconds=2.0)
    async def startgame( self ):
        logger.info(" Init Game")
        current_player = self.players[self.currentPlayer].display_name
        embed = MyEmbed( name="TicTacTow",
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
        await self.send_gamefield()

        
    @commands.Cog.listener()
    async def on_message(self, message ):
        if message.channel.id != self.gamechannel.id:
            return # Die Nachricht war nicht aus unserem Channel
        if message.author.id == self.bot.user.id:
            return # Nachrichten vom BOT werden ignoriert
        
        await message.delete()
        
        if message.author.id != self.players[self.currentPlayer].id:
            return # Falscher Spieler
        
        id = fields.get(message.content.upper())

        # checks if selected field exists
        if id is not None:
            field = self.placedFields.get(id)
            # checks if field is empty
            if field == 0:
                # set field placed
                playerindex = [-1, 1] # wird nur zum konvertieren benutzt
                self.placedFields[id] = playerindex[self.currentPlayer]
                await self.send_gamefield()
                if self.compute_winner(playerindex[self.currentPlayer]):
                    embed = discord.Embed(title=":tada: Player " + 
                                                self.players[self.currentPlayer].name +
                                                " hat gewonnen :tada:",
                                          colour=discord.Colour.green())
                    await self.gamechannel.send(embed=embed)
                    add_xp(self.players[self.currentPlayer], 20)
                    add_to_stats(self.players[self.currentPlayer], "TicTacToe", 1, 0, 0)
                    deposit_money(self.players[self.currentPlayer], 10)
                    await self.endgame()
                elif self.is_undecided():
                    embed = discord.Embed(title=":tada: Unentschieden :tada:",
                                          colour=discord.Colour.green())
                    await self.gamechannel.send(embed=embed)
                    for player in self.players:
                        add_to_stats(player, "TicTacToe", 0, 0, 1)
                    await self.endgame()
                else:
                    self.currentPlayer = (self.currentPlayer + 1) % 2
            else:
                embed = discord.Embed(title=":loudspeaker: Kein erlaubtes Feld :loudspeaker:",
                                      colour=discord.Colour.red())
                await self.gamechannel.send(embed=embed, delete_after=2)

                
                
##################################################################                
"""    async def gametask(self):

        #warten auf Spielzüge:
        while self.running:
            try:
                await asyncio.wait_for( self.turnevent.wait(), timeout=300)
            except asyncio.TimeoutError:
                embed = discord.Embed(title="Game Gestoppt:", description="(Timeout)", color=0x58ff46)
                embed.set_author(name="TicTacToe",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await self.gamechannel.send(embed=embed)
                break;
"""


