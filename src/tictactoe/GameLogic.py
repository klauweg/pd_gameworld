import asyncio

from discord.ext import commands
from parse import parse

from GameAPI.PlayerDataApi import Utils
import discord
from PIL import Image
import io

channel_prefix = "🔴🔵tictactoe-"

class GameControl():
    def __init__(self, queue):
        self.queue = queue
        self.queue.on_queue_change = self.check_for_gamestart

    def check_for_gamestart(self):
        if self.queue.len() >= 2:
            player_contexts = [self.queue.pop(), self.queue.pop()]
            Game(player_contexts, self.queue)

class Game(commands.Cog):
    def __init__(self, contexts, queue):
        self.players = [ctx.author for ctx in contexts]  # Extract Players
        self.playerindex = [-1, 1]
        self.bot = contexts[0].bot
        self.guild = contexts[0].guild
        self.joinchannel = contexts[0].channel
        self.queue = queue
        self.fields = {
            "A1": 0, "B1": 1, "C1": 2,
            "A2": 3, "B2": 4, "C2": 5,
            "A3": 6, "B3": 7, "C3": 8
        }
        self.placedFields = {
            0: 0, 1: 0, 2: 0,
            3: 0, 4: 0, 5: 0,
            6: 0, 7: 0, 8: 0
        }
        self.currentPlayer = 0
        self.gamechannel = None
        self.gamefield_message = None
        self.turn_lock = asyncio.Lock()

        self.running = True
        self.turnevent = asyncio.Event()
        self.bot.loop.create_task(self.gametask())


    async def gametask(self):
        # Suche ersten freien Channelslot
        cparse = lambda channel: parse( channel_prefix+"{:d}", channel.name ) # Parsefunktion für die Channelnames
        snums = sorted( [ cparse(c)[0] for c in self.bot.get_all_channels() if cparse(c) ] ) # extract
        next_channel = next( (x[0] for x in enumerate(snums) if x[0]+1 != x[1]), len(snums) ) + 1 #search gap
        # Spielchannel erzeugen:
        self.gamechannel = await self.guild.create_text_channel(
            name=channel_prefix + str(next_channel),
            category=self.bot.get_channel(741830130011209779))

        # Nachricht im Joinchannel:
        embed = discord.Embed(title="Game is starting!",description="Playing in Channel: **" + self.gamechannel.name + "** !",color=0x2dff32)
        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_author(name="TicTacToe",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.add_field(name="Players",value=f"""{self.players[0].name} vs. {self.players[1].name}""",inline=True)
        embed.set_footer(text="Have fun!")
        await self.joinchannel.send(embed=embed, delete_after=10)

        async with self.turn_lock:
            await self.send_gamefield()

        self.bot.add_cog(self)

        #warten auf Spielzüge:
        while self.running:
            try:
                await asyncio.wait_for( self.turnevent.wait(), timeout=60)
            except asyncio.TimeoutError:
                break;

        # Spiel beenden:
        await asyncio.sleep(5)
        for player in self.players:
            await Utils.add_to_stats(player, "TicTacToe", 0, 1)
        self.queue.release_player(self.players[0].id)
        self.queue.release_player(self.players[1].id)
        await self.gamechannel.delete()
        self.bot.remove_cog(self)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id == self.gamechannel.id and message.author.id is not self.bot.user.id:
            await message.delete()
            if message.author.id == self.players[self.currentPlayer].id:
                async with self.turn_lock:
                    id = self.fields.get(message.content)
                    # checks if selected field exists
                    if id is not None:
                        field = self.placedFields.get(id)
                        # checks if field is empty
                        if field == 0:
                            # set field placed
                            self.placedFields[id] = self.playerindex[self.currentPlayer]
                            await self.send_gamefield()
                            if self.compute_winner(self.playerindex[self.currentPlayer]):
                                embed = discord.Embed(title=":tada: Player " + self.players[self.currentPlayer].name +" won :tada:",colour=discord.Colour.green())
                                await self.gamechannel.send(embed=embed)
                                Utils.add_xp(self.players[self.currentPlayer], 20)
                                await Utils.add_to_stats(self.players[self.currentPlayer], "TicTacToe", 1, 0)
                                self.running = False
                            elif self.is_undecided():
                                embed = discord.Embed(title="Undecided",colour=discord.Colour.green())
                                await self.gamechannel.send(embed=embed)
                                self.running = False
                            else:
                                self.currentPlayer = (self.currentPlayer + 1) % 2
                    else:
                        embed = discord.Embed(title=":loudspeaker: The Field is not valid :loudspeaker:",colour=discord.Colour.red())
                        await self.gamechannel.send(embed=embed, delete_after=2)

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
        diagonal_right = self.placedFields[6] + self.placedFields[4] + self.placedFields[2]
        diagonal_left = self.placedFields[8] + self.placedFields[4] + self.placedFields[0]
        # winner check
        if on_top == won or below == won or left == won or right == won or diagonal_right == won or diagonal_left == won:
            return True
        #elif not list(self.placedFields.values()).__contains__(0):
        #    return -2
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
