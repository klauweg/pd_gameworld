import numpy as np
import discord
from discord.ext import commands

class Game(commands.Cog):

    def __init__(self, playerlist, cid, botvar):
        self.row_count = 6
        self.column_count = 7
        self.turn = 2
        self.players = playerlist
        self.channelid = cid
        self.bot = botvar
        self.gamefield = np.zeros((self.row_count, self.column_count))
        self.bot.get_channel(self.channelid).send(self.gamefield)
        self.print_gamefield()

    def insert_selected(self, row, col, playerindex):
        self.gamefield[row][col] = playerindex

    def is_location_valid(self, col):
        return self.gamefield[self.row_count - 1][col] == 0

    def get_next_row(self,col):
        for r in range(self.row_count):
            if (self.gamefield[r][col] == 0):
                return r

    def print_gamefield(self):
        message = self.bot.get_channel(self.channelid).send(self.gamefield)
        message.add_reaction('\u2776')
        message.add_reaction('\u2777')
        message.add_reaction('\u2778')
        message.add_reaction('\u2779')
        message.add_reaction('\u277A')
        message.add_reaction('\u277B')
        message.add_reaction('\u277C')

    def check_state(self,piece):
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
                        return False
                except:
                    pass
        return True

    # TODO: ADD REACT LISTENER AND GAMESTATES

