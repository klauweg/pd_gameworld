import asyncio
import io
import time

import numpy as np
from parse import parse
from PIL import Image

from GameAPI.Book import Book
from GameAPI.PlayerDataApi import Utils
from discord.ext import commands
import discord

channel_prefix = "🔴🔵connectfour-"


class GameControl():
    def __init__(self, queue):
        self.queue = queue
        # check_for_gamestart action in der queue registrieren:
        self.queue.on_queue_change = self.check_for_gamestart

    # Spiel erzeugen wenn genug Spieler in der Queue:
    def check_for_gamestart(self):
        if self.queue.len() >= 2:
            # ctx objekte aus der queue holen:
            player_contexts = [self.queue.pop(), self.queue.pop()]
            # Das eigentliche Spiel mit zwei Spielern starten und registrieren:
            Game(player_contexts, self.queue)


#######################################################################################################

class Game(commands.Cog):
    def __init__(self, contexts, queue):
        self.players = [ctx.author for ctx in contexts]  # Extract Players
        self.bot = contexts[0].bot
        self.guild = contexts[0].guild
        self.joinchannel = contexts[0].channel
        
        self.queue = queue # queue wird gebraucht um Spieler nach Ende zu "releasen"

        self.gamechannel = None  # Wird erst in prepare_game() erzeugt!
        self.gamefield = None
        self.gamefield_message = None

        self.row_count = 6
        self.column_count = 7
        self.nextplayer = 1
        self.emojis = {"1️⃣": 0, '2️⃣': 1, '3️⃣': 2, '4️⃣': 3, '5️⃣': 4, '6️⃣': 5, "7️⃣": 6}
        self.turn_lock = asyncio.Lock() # Mutex für mehrfach ausgeführte reaction adds

        self.bot.add_cog(self)
        self.bot.loop.create_task(self.prepare_game())  # __init__ kann nicht async sein!

    async def prepare_game(self):
        # Suche ersten freien Channelslot
        cparse = lambda channel: parse( channel_prefix+"{:d}", channel.name ) # Parsefunktion für die Channelnames
        snums = sorted( [ cparse(c)[0] for c in self.bot.get_all_channels() if cparse(c) ] ) # extract
        next_channel = next( (x[0] for x in enumerate(snums) if x[0]+1 != x[1]), len(snums) ) + 1 #search gap
        # Spielchannel erzeugen:
        self.gamechannel = await self.guild.create_text_channel(
            name=channel_prefix + str(next_channel),
            category=self.bot.get_channel(742406887567392878))

        # Nachricht im Joinchannel:
        embed = discord.Embed(title="Game is starting!",
                              description="Playing in Channel: **" + self.gamechannel.name + "** !",
                              color=0x2dff32)
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_author(name="ConnectFour",
                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.add_field(name="Players",
                        value=f"""{self.players[0].display_name} vs. {self.players[1].display_name}""",
                        inline=True)
        embed.set_footer(text="Have fun!")
        await self.joinchannel.send(embed=embed, delete_after=10)

        # Spielfeld erzeugen:
        self.gamefield = np.zeros((6, 7))

        # Spielfeld initial einmal ausgeben:
        async with self.turn_lock:
            await self.send_gamefield()

    # Nachrichten im Spielchannel werden gleich wieder gelöscht:
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (self.gamechannel == message.channel  # Unser Channel?
                and self.bot.user != message.author):  # Nachricht nicht vom Bot?
            await message.delete()  # Dann löschen wir die Nachricht

    # Action bei drücken eines Reaction-Buttons: (Spielzug)
    @commands.Cog.listener()
    async def on_reaction_add(self, payload: discord.Reaction, member):
        if payload.message.id == self.gamefield_message.id and member.id is not self.bot.user.id:
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
                            title=":tada: " + self.players[self.nextplayer].name + " won :tada:",
                            colour=discord.Colour.green())
                        await self.gamechannel.send(embed=embed, delete_after=10)
                        # Statistik#
                        await Utils.add_xp(self.players[self.nextplayer], 20)
                        await Utils.add_to_stats(self.players[self.nextplayer], "ConnectFour", 1, 0)
                        for player in self.players:
                            await Utils.add_to_stats(player, "ConnectFour", 0, 1)
                        await asyncio.sleep(5)
                        # Selbstzerstörung:
                        self.queue.release_player( self.players[0].id )
                        self.queue.release_player( self.players[1].id )
                        await self.gamechannel.delete()
                        self.bot.remove_cog(self)
                        return
                    else:  # Das Spiel geht noch weiter:
                        self.nextplayer = (self.nextplayer + 1) % 2

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
