import asyncio
import io
import time

import numpy as np
from PIL import Image

from GameAPI.Book import Book
from GameAPI.PlayerDataApi import Utils
from discord.ext import commands
import discord


class ConnectFourGameLogic(commands.Cog):
    def __init__(self, queue ):
        self.queue = queue
        # check_for_gamestart action in der queue registrieren:
        self.queue.add_action = self.check_for_gamestart

    # Spiel erzeugen wenn genug Spieler in der Queue:
    async def check_for_gamestart(self):
        while (self.queue.len() >= 2):
            # ctx objekte aus der queue holen:
            player_contexts = [self.queue.pop(), self.queue.pop()]
            # Das eigentliche Spiel mit zwei Spielern starten:
            ConnectFourGame( player_contexts )
            break

        
######################################################################################################



    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if ConnectFourGameLogic.channels_in_use.__contains__(message.channel.id):
            game: ConnectFourGame = ConnectFourGameLogic.channels_in_use.get(message.channel.id)
            if message.channel.id == game.channelid:
                if message.author != self.bot.user:
                    await message.delete()

#######################################################################################################
                    
class ConnectFourGame(commands.Cog):

    def __init__(self, contexts ):
        self.players = [ ctx.author for ctx in contexts ] # Extract Players
        self.bot = contexts[0].bot
        self.guild = contexts[0].guild
        self.joinchannel = contexts[0].channel

        self.gamechannel = None # Wird erst im Constructor erzeugt
        self.gamefield = None
        self.gamefield_message = None

        self.row_count = 6
        self.column_count = 7
        self.nextplayer = 1
        self.is_in_action = False
        self.emojis = { "1️⃣": 0, '2️⃣': 1, '3️⃣': 2, '4️⃣': 3, '5️⃣': 4, '6️⃣': 5, "7️⃣": 6 }
        
        self.bot.loop.create_task( self.prepare_game() )
        
    async def prepare_game( self ):
        # Spielchannel erzeugen:
        self.gamechannel = await guild.create_text_channel(
                          name="🔴🔵connectfour-" + str(len(ConnectFourGameLogic.channels_in_use) + 1),
                          category=bot.get_channel(742406887567392878))

        # Nachricht im Joinchannel:
        embed = discord.Embed(title="Game is starting!",
                            description="Playing in Channel: **" + gamechannel.name + "** !",
                            color=0x2dff32)
        embed.set_thumbnail(
                url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_author(name="ConnectFour",
                             icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.add_field(name="Players",
                             value=f"""{gameplayers[0].display_name} vs. {gameplayers[1].display_name}""",
                             inline=True)
        embed.set_footer(text="Thanks for Playing!")
        await self.joinchannel.send(embed=embed, delete_after=10)
           
        # Spielfeld erzeugen:
        self.gamefield = np.zeros((6, 7))

        # Spielfeld initial einmal ausgeben:
        self.send_gamefield()


    async def destroy_game( self ):
        await self.bot.get_channel(game.channelid).delete()
        self.bot.remove_cog(game)
        ConnectFourGameLogic.channels_in_use.pop(channel_id)
        for player in game.players:
            self.playing_players.remove(player.id)


                                game.aktplayer += 1
                                if game.aktplayer == 2:
                                    game.aktplayer = 0
                                game.last_actions.clear()
                                game.last_actions[game.players[game.aktplayer]] = time.time()

                        game.is_in_action = False
                    else:
                        try:
                            await payload.message.remove_reaction(payload.emoji, self.bot.get_user(member.id))
                        except:
                            return
                        
                        
@commands.Cog.listener() # Action bei drücken eines Reaction-Buttons:
    async def on_reaction_add(self, payload: discord.Reaction, member):
        if payload.message == self.gamefield_message: # Ist das add-event für uns?
            if member == self.players[ self.nextplayer ]: # Der richtige Spieler am Zug?
                if self.is_in_action == True: # Locking wegen async event
                    return
                self.is_in_action = True
                if not payload.emoji in self.emojis: # Valid emoji?
                    return
                await payload.message.remove_reaction(payload.emoji, member) # remove add
                col = self.emojis.get[ payload.emoji ]
                # Hier beginnt der eigentliche Spielzug:
                if self.is_location_valid(col):
                row = game.get_next_row(col)
                game.insert_selected(row, col, self.nextplayer)
                # Neues spielfeld ausgeben:
                self.send_gamefield()
                # Hat jemand gewonnen?
                if self.check_state(self.nextplayer):
                    embed = discord.Embed(
                             title=":tada: " + self.players[game.nextplayer].name + " won :tada:",
                                        colour=discord.Colour.green())
                    await self.bot.get_channel(game.channelid).send(embed=embed, delete_after=10)
                    # Statistik
                    await Utils.add_xp(game.players[game.aktplayer], 20)
                    await Utils.add_to_stats(game.players[game.aktplayer], "ConnectFour", 1, 0)
                    for player in game.players:
                        await Utils.add_to_stats(player, "ConnectFour", 0, 1)
                    await asyncio.sleep(5)
                    # Selbstzerstörung:
                    await self.destroy_game()


    def insert_selected(self, row, col, playerindex):
        self.gamefield[row][col] = playerindex + 1

    def is_location_valid(self, col):
        return self.gamefield[self.row_count - 1][col] == 0

    def get_next_row(self,col):
        for r in range(self.row_count):
            if self.gamefield[r][col] == 0:
                return r

    def check_state(self, piece):
        piece += 1
        for c in range(self.column_count):
            for r in range(self.row_count):
                try:
                    if ((self.gamefield[r][c] == piece and self.gamefield[r][c + 1] == piece and self.gamefield[r][c + 2] == piece and
                         self.gamefield[r][c + 3] == piece) or
                            (self.gamefield[r][c] == piece and self.gamefield[r + 1][c] == piece and self.gamefield[r + 2][c] == piece and
                             self.gamefield[r + 3][c] == piece) or
                            (self.gamefield[r][c] == piece and self.gamefield[r + 1][c + 1] == piece and self.gamefield[r + 2][
                                c + 2] == piece and self.gamefield[r + 3][c + 3] == piece) or
                            (self.gamefield[r][c] == piece and self.gamefield[r - 1][c + 1] == piece and self.gamefield[r - 2][
                                c + 2] == piece and self.gamefield[r - 3][c + 3] == piece)):
                        return True
                except:
                    pass
        return False

    async def send_gamefield( self ):
        # ggf. altes Spielfeld löschen:
        if self.gamefield_message:
            await game.gamefield_message.delete()
        # Neue Message erzeugen:
        self.gamefield_message = await self.gamechannel.send(file=self.build_board(self.gamefield))
        # Reaction Buttons hinzufügen:
        for tag in self.emojis.keys():
            await self.gamefield_message.add_reaction( tag )

    def build_board(self, gamefield: np.matrix):
        field_img: Image.Image = Image.open("../resources/connectfour/field.png")
        o = Image.open("../resources/connectfour/o_universe.png")
        X = Image.open("../resources/connectfour/x_universe.png")
        fields = [[(34, 34), (184, 34), (334, 34), (484, 34), (634, 34), (784, 34), (934, 34)],
                  [(34, 184), (184, 184), (334, 184), (484, 184), (634, 184), (784, 184), (934, 184)],
                  [(34, 334), (184, 334), (334, 334), (484, 334), (634, 334), (784, 334), (934, 334)],
                  [(34, 484), (184, 484), (334, 484), (484, 484), (634, 484), (784, 484), (934, 484)],
                  [(34, 634), (184, 634), (334, 634), (484, 634), (634, 634), (784, 634), (934, 634)],
                  [(34, 784), (184, 784), (334, 784), (484, 784), (634, 784), (784, 784), (934, 784)]]
        fields.reverse()
        for i in range(len(gamefield)):
            for x in range(len(gamefield[i])):
                if gamefield[i][x] == 1:
                    field_img.paste(X, fields[i][x], X)
                if gamefield[i][x] == 2:
                    field_img.paste(o, fields[i][x], o)
        arr = io.BytesIO()
        field_img.save(arr, format="png")
        basewidth = 250
        wpercent = (basewidth / float(field_img.size[0]))
        hsize = int((float(field_img.size[1]) * float(wpercent)))
        field_img = field_img.resize((basewidth, hsize), Image.ANTIALIAS)
        arr = io.BytesIO()
        field_img.save(arr, format="png")
        arr.seek(0)
        file = discord.File(arr)
        file.filename = "field.png"
        return file




