import logging
logger = logging.getLogger("connectfour")

import asyncio
import io
import logging
from itertools import chain
from discord.ext import commands
import discord
import numpy as np
from parse import parse
from PIL import Image

# User Modules:
from myclient import client
from Gadgets.user_extension import add_xp, add_to_stats, deposit_money

class Game(commands.Cog):
    def __init__(self, channel, player1, player2):
        self.gamechannel = channel
        self.players = [ player1, player2 ]

        self.gamefield = None
        self.gamefield_message = None

        self.row_count = 6
        self.column_count = 7
        self.nextplayer = 1
        self.emojis = {"1️⃣": 0, '2️⃣': 1, '3️⃣': 2, '4️⃣': 3, '5️⃣': 4, '6️⃣': 5, "7️⃣": 6}
        self.turn_lock = asyncio.Lock() # Mutex für mehrfach ausgeführte reaction adds

        self.running = True
        self.turnevent = asyncio.Event()
        client.loop.create_task(self.gametask())

    async def gametask(self):
        embed = discord.Embed(title="Also, " + self.players[self.nextplayer].display_name + " bitte beginne!",description="",color=0x58ff46)
        embed.set_author(name="VierGewinnt",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        await self.gamechannel.send(embed=embed, delete_after=30)

        # Spielfeld erzeugen:
        self.gamefield = np.zeros((6, 7))

        # Spielfeld initial einmal ausgeben:
        async with self.turn_lock:
            await self.send_gamefield()

        # COG aktivieren:
        client.add_cog(self)

        # Wir warten auf Spielzüge:
        while self.running:
            try:
                await asyncio.wait_for( self.turnevent.wait(), timeout=300 )
            except asyncio.TimeoutError:
                logging.info( "Timeout: Keine Spielzüge mehr, Spiel wird beendet" )
                embed = discord.Embed(title="Game gestoppt:", description="(Timeout)", color=0x58ff46)
                embed.set_author(name="Galgenmännchen",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await self.gamechannel.send(embed=embed)
                break;

        # Spiel beenden:
        for player in self.players:
            add_to_stats(player, "VierGewinnt", 0, 1, 0)
            add_xp(player, 5)
        await asyncio.sleep(5)
        client.remove_cog(self)


    # Nachrichten im Spielchannel werden gleich wieder gelöscht:
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (self.gamechannel == message.channel  # Unser Channel?
                and client.user != message.author):  # Nachricht nicht vom Bot?
            try:
                await message.delete()  # Dann löschen wir die Nachricht
            except:
                pass

    # Action bei drücken eines Reaction-Buttons: (Spielzug)
    @commands.Cog.listener()
    async def on_reaction_add(self, payload: discord.Reaction, member):
        if payload.message.id == self.gamefield_message.id and member.id is not client.user.id:
            try: # Die Nachricht könnte zwischenzeitlich gelöscht worden sein
                await payload.message.remove_reaction(payload.emoji, member)  # remove add
            except:
                pass
        if (payload.message.id == self.gamefield_message.id  # Ist das add-event für uns?
                and member.id == self.players[self.nextplayer].id  # Der richtige Spieler am Zug?
                and payload.emoji in self.emojis):
            async with self.turn_lock:
                col = self.emojis[payload.emoji]
                # Ist der Zug möglich?
                if self.is_location_valid(col):
                    row = self.get_next_row(col)
                    self.insert_selected(row, col, self.nextplayer)
                    # Neues spielfeld ausgeben:
                    await self.send_gamefield()
                    # Hat jemand gewonnen?
                    if self.check_state(self.nextplayer):
                        embed = discord.Embed(
                            title=":tada: " + self.players[self.nextplayer].name + " hat gewonnen :tada:",
                            colour=discord.Colour.green())
                        await self.gamechannel.send(embed=embed, delete_after=10)
                        # Statistik#
                        add_xp(self.players[self.nextplayer], 25)
                        add_to_stats(self.players[self.nextplayer], "VierGewinnt", 1, 0, 0)
                        deposit_money(self.players[self.nextplayer], 20)
                        # Selbstzerstörung:
                        self.running = False
                    elif not 0 in chain(*self.gamefield):
                        embed = discord.Embed(
                            title=":tada: Unentschieden :tada:",
                            colour=discord.Colour.green())
                        for player in self.players:
                            add_to_stats(player, "TicTacToe", 0, 0, 1)
                        await self.gamechannel.send(embed=embed, delete_after=10)
                        # Selbstzerstörung:
                        self.running = False
                    else:
                        self.nextplayer = (self.nextplayer + 1) % 2
            self.turnevent.set() # Watchdog trigger

    def insert_selected(self, row, col, playerindex):
        self.gamefield[row][col] = playerindex + 1

    def is_location_valid(self, col):
        return self.gamefield[self.row_count - 1][col] == 0

    def get_next_row(self, col):
        for r in range(self.row_count):
            if self.gamefield[r][col] == 0:
                return r

    def check_state(self, piece):
        piece += 1
        for c in range(self.column_count):
            for r in range(self.row_count):
                try:
                    if ((self.gamefield[r][c] == piece and self.gamefield[r][c + 1] == piece and self.gamefield[r][
                        c + 2] == piece and
                        self.gamefield[r][c + 3] == piece) or
                        (self.gamefield[r][c] == piece and self.gamefield[r + 1][c] == piece and
                         self.gamefield[r + 2][c] == piece and
                         self.gamefield[r + 3][c] == piece) or
                        (self.gamefield[r][c] == piece and self.gamefield[r + 1][c + 1] == piece and
                         self.gamefield[r + 2][
                             c + 2] == piece and self.gamefield[r + 3][c + 3] == piece) or
                        (self.gamefield[r][c] == piece and self.gamefield[r - 1][c + 1] == piece and
                         self.gamefield[r - 2][
                             c + 2] == piece and self.gamefield[r - 3][c + 3] == piece)):
                        return True
                except:
                    pass
        return False

    async def send_gamefield(self):
        # ggf. altes Spielfeld löschen:
        if self.gamefield_message:
            await self.gamefield_message.delete()
        # Neue Message erzeugen:
        self.gamefield_message = await self.gamechannel.send(file=self.build_board(self.gamefield))
        # Reaction Buttons hinzufügen:
        for tag in self.emojis.keys():
            await self.gamefield_message.add_reaction(tag)

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
