from discord.ext import commands
from tictactoe import Game
import queue
import discord


class TicTacToeGameLogic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = queue.Queue()
        self.channels_in_use = {
            741830852689920050: Game.empty_game,
            741831083108204604: Game.empty_game,
            741831127723147355: Game.empty_game
        }

    @commands.command()
    async def tictactoe(self, ctx: commands.Context):
        # checks if channel is not a tic tac toe channel and game is running then error Message and return
        if not self.channels_in_use.keys().__contains__(ctx.channel.id) or not self.channels_in_use.get(
                ctx.channel.id).is_empty():
            embed = discord.Embed(title=":loudspeaker:  You cant play here :loudspeaker:", colour=discord.Colour.red())
            await ctx.author.send(embed=embed)
            return

        # checks if queue is not empty then get a player from the queue and start a match else add player queue
        if self.queue.qsize() > 0:
            players = [self.queue.get_nowait(), ctx.author]
            game = Game.Game(players)
            game.currentPlayer = players[0]
            self.channels_in_use[ctx.channel.id] = game
            embed = discord.Embed(title=":loudspeaker: The game starts now. :loudspeaker:",
                                  colour=discord.Colour.green())
            await ctx.author.send(embed=embed)
        else:
            embed = discord.Embed(title=":loudspeaker: No player found, please wait a moment. :loudspeaker:",
                                  colour=discord.Colour.red())
            await ctx.author.send(embed=embed)
            self.queue.put_nowait(ctx.author)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        channel: discord.TextChannel = message.channel
        # checks if channel is a tic tac toe channel and is actual in a game
        if self.channels_in_use.keys().__contains__(channel.id) and not self.channels_in_use.get(
                channel.id).is_empty():
            game = self.channels_in_use.get(channel.id)
            # checks if player is player of this round
            if game.players.__contains__(message.author):
                # checks if player is on train
                if game.currentPlayer is message.author:
                    id = game.fields.get(message.content)
                    # checks if selected field exists
                    if id is not None:
                        isPlaced = game.placedFields.get(id) is not -1
                        # checks if field is empty
                        if not isPlaced:
                            # set field placed
                            game.placedFields[id] = game.players.index(game.currentPlayer)
                            await channel.purge()
                            await channel.send(await self.build_board(game.placedFields))
                            if game.compute_winner() is 3:
                                embed = discord.Embed(title=":tada: Player " + game.players[1] + " won :tada:",
                                                      colour=discord.Colour.green())
                                await channel.send(embed=embed)
                                await self.stopGame(channel.id)
                                return
                            elif game.compute_winner() is 0:
                                embed = discord.Embed(title=":tada: Player " + game.players[0] + " won :tada:",
                                                      colour=discord.Colour.green())
                                await channel.send(embed=embed)
                                await self.stopGame(channel.id)
                                return
                            if game.players.index(game.currentPlayer) is 1:
                                game.currentPlayer = game.players[0]
                            else:
                                game.currentPlayer = game.players[1]
                            self.channels_in_use[channel.id] = game
                    else:
                        embed = discord.Embed(title=":loudspeaker: The Field is not valid :loudspeaker:",
                                              colour=discord.Colour.red())
                        await channel.send(embed=embed)
                else:
                    embed = discord.Embed(title=":loudspeaker: It is not your turn :loudspeaker:",
                                          colour=discord.Colour.red())
                    await channel.send(embed=embed)
            else:
                embed = discord.Embed(title=":loudspeaker: You aren't a player of this game. :loudspeaker:",
                                      colour=discord.Colour.red())
                await channel.send(embed=embed)

    async def stopGame(self, channel_id):
        self.channels_in_use[channel_id] = Game.empty_game

    async def build_board(self, placedFields: dict):
        fields = [":white_large_square:", ":white_large_square:", ":white_large_square:"
                                                                  ":white_large_square:", ":white_large_square:",
                  ":white_large_square:",
                  ":white_large_square:", ":white_large_square:", ":white_large_square:"]
        for x in range(0, placedFields.__len__()):
            if placedFields[x] is 1:
                fields[x] = ":regional_indicator_x:"
            else:
                fields[x] = ":regional_indicator_o:"

        message = ":orange_square: ˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍ:orange_square: \
                    |                                         |\
                    |     " + fields[0] + "      " + fields[1] + "      " + fields[2] + "|\
                    |                                         |\
                    |     " + fields[3] + "      " + fields[4] + "      " + fields[5] + "|\
                    |                                         |\
                    |     " + fields[6] + "      " + fields[7] + "      " + fields[8] + "|\
                    :orange_square: ˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍ_ˍˍ:orange_square:"
        return message
