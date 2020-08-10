import numpy as np
from discord.ext import commands

class Game(commands.Cog):

    def __init__(self, playerlist, cid):
        self.row_count = 6
        self.column_count = 7
        self.turn = 2
        self.players = playerlist
        self.channelid = cid

        self.gamefield = np.zeros((self.row_count, self.column_count))

    def insert_selected(gamefield, row, col, playerindex):
        gamefield[row][col] = playerindex

    def is_location_valid(self,gamefield, col):
        return gamefield[self.row_count - 1][col] == 0

    def get_next_row(self,gamefield, col):
        for r in range(self.row_count):
            if (gamefield[r][col] == 0):
                return r

    def print_gamefield(gamefield):
        print(np.flip(gamefield, 0))

    def check_state(self,gamefield, piece):
        for c in range(self.column_count):
            for r in range(self.row_count):
                try:
                    if ((gamefield[r][c] == piece and gamefield[r][c + 1] == piece and gamefield[r][c + 2] == piece and
                         gamefield[r][c + 3] == piece) or
                            (gamefield[r][c] == piece and gamefield[r + 1][c] == piece and gamefield[r + 2][c] == piece and
                             gamefield[r + 3][c] == piece) or
                            (gamefield[r][c] == piece and gamefield[r + 1][c + 1] == piece and gamefield[r + 2][
                                c + 2] == piece and gamefield[r + 3][c + 3] == piece) or
                            (gamefield[r][c] == piece and gamefield[r - 1][c + 1] == piece and gamefield[r - 2][
                                c + 2] == piece and gamefield[r - 3][c + 3] == piece)):
                        return False
                except:
                    pass
        return True