from discord.ext import commands
from tictactoe import TicTacToeGame
from GameAPI.Queue import Queue
import discord
from discord.utils import get
from PIL import Image
import io


class TicTacToeGameLogic(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.queue: Queue = Queue()
        self.channels_in_use = {
            "0": 0
        }
        self.inviteChannel = 741835475085557860

    @commands.command()
    async def tictactoe(self, ctx: commands.Context):
        if ctx.channel.id is not self.inviteChannel and ctx.author.bot is True:
            return
        if self.queue.__contains__(ctx.author.id):
             self.queue.remove(ctx.author.id)
             embed = discord.Embed(title="See you soon!", description=f"""{ctx.author.display_name} left the Queue""",
                                   color=0x49ff35)
             embed.set_author(name="ConnectFour",
                              icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
             embed.set_thumbnail(
                 url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
             await ctx.channel.send(embed=embed)
             return
        guild: discord.Guild = ctx.guild

        if self.queue.__len__() >= 1:
            channel: discord.TextChannel = await guild.create_text_channel(name="📝tic-tac-toe-" +
                                                                                str(self.channels_in_use.__len__()),
                                                                           category=get(guild.categories,
                                                                                        name="⚔| TIC TAC TOE |⚔"))
            game = TicTacToeGame.TicTacToeGame([ctx.author.id, self.queue.get()])
            game.currentPlayer = game.players[0]
            game.currentPlayerID = 0
            self.channels_in_use[channel.id] = game
            embed = discord.Embed(title="A game was found", description="Your game takes place in channel " +
                                                                        channel.mention,
                                  color=0x44df30)
            embed.set_author(
                name="TicTacToe", icon_url="https://images-ext-1.discordapp.net/external"
                                           "/NoSlZoNmSKGQhi63nMjEiVtdTgv7WrPtBk4g9GEiRy8/%3Fsize%3D256/https/cdn"
                                           ".discordapp.com/app-icons/742032003125346344"
                                           "/e4f214ec6871417509f6dbdb1d8bee4a.png")
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png"
                    "?size=256")
            embed.add_field(name="Players", value=self.bot.get_user(game.players[0]).mention + " vs. " +
                                                  self.bot.get_user(game.players[1]).mention,
                            inline=True)
            await ctx.send(embed=embed)
            await channel.purge(limit=100)
            await channel.send(file=await self.build_board(placedFields=game.placedFields))
        else:
            self.queue.put(ctx.author.id)
            embed = discord.Embed(title="You joined the queue.",
                                  description="Please wait a moment until a channel becomes free or another player "
                                              "joins the queue", color=0x44df30)
            embed.set_author(name="TicTacToe", icon_url="https://images-ext-1.discordapp.net/external"
                                                        "/NoSlZoNmSKGQhi63nMjEiVtdTgv7WrPtBk4g9GEiRy8/%3Fsize%3D256"
                                                        "/https/cdn.discordapp.com/app-icons/742032003125346344"
                                                        "/e4f214ec6871417509f6dbdb1d8bee4a.png")

            embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344"
                                    "/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            await ctx.send(embed=embed)

    # Searches for free channels to play and returns its id.

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        channel: discord.TextChannel = message.channel
        # checks if channel is a tic tac toe channel and is actual in a game
        if message.author.bot is True:
            return
        if self.channels_in_use.keys().__contains__(channel.id) and not self.channels_in_use.get(
                channel.id).is_empty():
            game: TicTacToeGame.TicTacToeGame = self.channels_in_use.get(channel.id)
            # checks if player is player of this round
            if game.players.__contains__(message.author.id):
                # checks if its player turn
                if game.currentPlayer is message.author.id:
                    if game.is_working == False:
                        game.is_working = True
                        id = game.fields.get(message.content)
                        # checks if selected field exists
                        if id is not None:
                            isPlaced = game.placedFields.get(id) != 99
                            # checks if field is empty
                            if not isPlaced:
                                # set field placed
                                game.placedFields[id] = game.players.index(game.currentPlayer) + 1
                                await channel.purge()
                                await channel.send(file=await self.build_board(game.placedFields))
                                if game.compute_winner() == 1:
                                    embed = discord.Embed(title=":tada: Player " + self.bot.get_user(game.players[1]).name +
                                                                " won :tada:",
                                                          colour=discord.Colour.green())
                                    await channel.send(embed=embed)
                                    await self.stopGame(channel.id)
                                    game.is_working = False
                                    return
                                elif game.compute_winner() == 0:
                                    embed = discord.Embed(
                                        title=":tada: Player " + self.bot.get_user(game.players[0]).name + " won :tada:",
                                        colour=discord.Colour.green())
                                    await channel.send(embed=embed)
                                    await self.stopGame(channel.id)
                                    game.is_working = False
                                    return
                                elif game.compute_winner() == -2:
                                    embed = discord.Embed(title=":crossed_swords:Undecided:crossed_swords: ",
                                                          color=0xffe605)
                                    await channel.send(embed=embed)
                                    await self.stopGame(channel.id)
                                    game.is_working = False
                                    return
                                game.change_to_next_player()
                                self.channels_in_use[channel.id] = game
                            game.is_working = False
                        else:
                            embed = discord.Embed(title=":loudspeaker: The Field is not valid :loudspeaker:",
                                                  colour=discord.Colour.red())
                            await channel.send(embed=embed, delete_after=10)
                            await message.delete(delay=10)
                            game.is_working = False

                else:
                    embed = discord.Embed(title=":loudspeaker: It is not your turn :loudspeaker:",
                                          colour=discord.Colour.red())
                    await channel.send(embed=embed, delete_after=10)
                    await message.delete(delay=10)
            else:
                embed = discord.Embed(title=":loudspeaker: You aren't a player of this game. :loudspeaker:",
                                      colour=discord.Colour.red())
                await channel.send(embed=embed, delete_after=10)
                await message.delete(delay=10)

    async def stopGame(self, channel_id):
        self.channels_in_use.pop(channel_id)
        channel: discord.TextChannel = self.bot.get_channel(channel_id)
        await channel.delete()

    async def build_board(self, placedFields: dict):
        field_img: Image.Image = Image.open("../resources/tictactoe/gamefield_universe.png")
        o = Image.open("../resources/tictactoe/o_universe.png")

        X = Image.open("../resources/tictactoe/x_universe.png")
        fields = [(12, 12), (175, 12), (337, 12),
                  (12, 175), (175, 175), (337, 175),
                  (12, 337), (175, 337), (337, 337)]

        for x in list(placedFields.keys()):
            if placedFields[x] == 1:
                field_img.paste(X, fields[list(placedFields).index(x)],X)
            elif placedFields[x] == 2:
                field_img.paste(o, fields[list(placedFields).index(x)],o)

        arr = io.BytesIO()
        field_img.save(arr, format="png")
        arr.seek(0)
        file = discord.File(arr)
        file.filename = "field.png"
        return file
