from discord.ext import commands
from tictactoe import Game
import queue
import discord


class TicTacToeGameLogic(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.queue = queue.Queue()
        self.channels_in_use = {
            741830852689920050: Game.get_empty_game(),
            741831083108204604: Game.get_empty_game(),
            741831127723147355: Game.get_empty_game()
        }
        self.inviteChannel = 741835475085557860
        self.get_free_channel()

    @commands.command()
    async def tictactoe(self, ctx: commands.Context):
        if ctx.channel.id is not self.inviteChannel and ctx.author.bot is True:
            return
        # if ctx.author.id in self.queue:
        #     return
        channel: discord.TextChannel = self.bot.get_channel(self.get_free_channel())
        if channel is not None:
            if self.queue.qsize() >= 1:
                game = Game.Game([ctx.author.id, self.queue.get_nowait()])
                game.currentPlayer = game.players[0]
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
                await channel.send(await self.build_board(game.placedFields))
            else:
                self.queue.put_nowait(ctx.author.id)
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
        else:
            self.queue.put_nowait(ctx.author.id)
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
    def get_free_channel(self):
        free_channels: list = []
        for x in self.channels_in_use:
            if self.channels_in_use[x] is Game.get_empty_game():
                free_channels.append(x)
        if free_channels.__len__() == 0:
            return None
        else:
            return free_channels[0]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        channel: discord.TextChannel = message.channel
        # checks if channel is a tic tac toe channel and is actual in a game
        if message.author.bot is True:
            return
        if self.channels_in_use.keys().__contains__(channel.id) and not self.channels_in_use.get(
                channel.id).is_empty():
            game = self.channels_in_use.get(channel.id)
            # checks if player is player of this round
            if game.players.__contains__(message.author.id):
                # checks if its player turn
                if game.currentPlayer is message.author.id:
                    id = game.fields.get(message.content)
                    # checks if selected field exists
                    if id is not None:
                        isPlaced = game.placedFields.get(id) != 99
                        # checks if field is empty
                        if not isPlaced:
                            # set field placed
                            game.placedFields[id] = game.players.index(game.currentPlayer) + 1
                            await channel.purge()
                            await channel.send(await self.build_board(game.placedFields))
                            if game.compute_winner() == 1:
                                embed = discord.Embed(title=":tada: Player " + self.bot.get_user(game.players[1]).name +
                                                            " won :tada:",
                                                      colour=discord.Colour.green())
                                await channel.send(embed=embed)
                                await self.stopGame(channel.id)
                                return
                            elif game.compute_winner() == 0:
                                embed = discord.Embed(
                                    title=":tada: Player " + self.bot.get_user(game.players[0]).name + " won :tada:",
                                    colour=discord.Colour.green())
                                await channel.send(embed=embed)
                                await self.stopGame(channel.id)
                                return
                            if game.players.index(game.currentPlayer) == 1:
                                game.currentPlayer = game.players[0]
                            elif game.players.index(game.currentPlayer) == 0:
                                game.currentPlayer = game.players[1]
                            self.channels_in_use[channel.id] = game
                    else:
                        embed = discord.Embed(title=":loudspeaker: The Field is not valid :loudspeaker:",
                                              colour=discord.Colour.red())
                        await channel.send(embed=embed, delete_after=10)
                        await message.delete(delay=10)

                else:
                    embed = discord.Embed(title=":loudspeaker: It is not your turn :loudspeaker:",
                                          colour=discord.Colour.red())
                    await channel.send(embed=embed)
            else:
                embed = discord.Embed(title=":loudspeaker: You aren't a player of this game. :loudspeaker:",
                                      colour=discord.Colour.red())
                await channel.send(embed=embed)

    async def stopGame(self, channel_id):
        self.channels_in_use[channel_id] = Game.get_empty_game()
        channel: discord.TextChannel = self.bot.get_channel(channel_id)
        await channel.purge()
        embed = discord.Embed(title="No game running",
                              description="This channel is free at the moment. Use !tictactoe in #📫-tic-tac-toe-invites to join the queue.",
                              color=0x3dff6a)
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        await channel.send(embed=embed)

    async def build_board(self, placedFields: dict):
        fields = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                  ":white_large_square:", ":white_large_square:", ":white_large_square:",
                  ":white_large_square:", ":white_large_square:", ":white_large_square:"]
        for x in range(0, placedFields.__len__()):
            if placedFields[x] == 2:
                fields[x] = ":regional_indicator_x:"
            elif placedFields[x] == 1:
                fields[x] = ":regional_indicator_o:"
        message = "      :orange_square: ˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍ:orange_square:\n\
     |                                       |\n\
     |     " + fields[0] + "      " + fields[1] + "      " + fields[2] + "    |\n\
     |                                       |\n\
     |     " + fields[3] + "      " + fields[4] + "      " + fields[5] + "    |\n\
     |                                       |\n\
     |     " + fields[6] + "      " + fields[7] + "      " + fields[8] + "    |\n\
     |                                       |\n\
   :orange_square: ˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍ:orange_square:"
        return message
