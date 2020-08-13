import math
import asyncio
import discord
from discord.ext import commands


class Player:
    def __init__(self, user_id, xp, player_stats):
        self.user_id = user_id
        self.xp = xp
        self.player_stats = player_stats

    def compute_level(self):
        level = math.sqrt(self.xp / 10)
        return level

    def to_json(self):
        return {self.user_id: {"xp": self.xp, "TicTacToe": self.player_stats.tictactoe,
                               "Connect4": self.player_stats.connect4, "Hangman": self.player_stats.hangman}}


class PlayerStats:
    def __init__(self):
        self.total_wins = 0
        # Stats of all games formatted as (wins, loses, played, win chance)
        self.tictactoe = (0, 0, 0, 0)
        self.connect4 = (0, 0, 0, 0)
        self.hangman = (0, 0, 0, 0)
