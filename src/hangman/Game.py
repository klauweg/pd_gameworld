import random

import discord
from discord.ext import commands


class Game(commands.Cog):
    def __init__(self, channelid, playerids, bot):
        self.correct_word = None
        self.playerids = playerids
        self.not_guessing_player_id = random.choice(self.playerids)
        self.channelid = channelid
        self.guessed_letters = []
        self.game_state = 0


    def guess(self, letter):
        self.guessed_letters.append(letter)

    def is_valid_guess(self, string):
        valid_guesses = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        if string in valid_guesses:
            return True
        else:
            return False

    def has_already_guessed(self, letter):
        if letter in self.guessed_letters:
            return True
        else:
            return False

    def check_win(self):
        for char in self.correct_word:
            if self.has_already_guessed(char) == False:
                return False
        return True

    def get_print_string(self):
        print_string = ""
        for char in self.correct_word:
            if self.has_already_guessed(char.upper()):
                print_string += char
            else:
                print_string += "_"
        return print_string

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id == self.channelid:
            if self.game_state == 0 and message.author.id == self.not_guessing_player_id and message.content.isalpha():
                self.correct_word = message.content
                # TODO: SEND MESSAGE TO PLAYERS THAT THE WORD HAS BEEN SET
