import discord
from discord.ext import commands


class Game(commands.Cog):
    def __init__(self, players, channelid,  bot, notguessingplayer):
        self.correct_word = None
        self.players = players
        self.not_guessing_player = notguessingplayer
        self.channelid = channelid
        self.guessed_letters = []
        self.gamestate = 0
        self.bot: commands.Bot = bot
        self.message: discord.Message = None
        self.loose_level = 0
        self.is_in_action = False

    async def guess(self, letter):
        self.guessed_letters.append(letter)

        if letter not in self.correct_word:
            self.loose_level += 1

    def is_valid_guess(self, string):
        valid_guesses = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "Ö", "Ü", "Ä"]
        if string in valid_guesses:
            return True
        else:
            return False

    def has_already_guessed(self, letter):
        if letter in self.guessed_letters:
            return True
        else:
            return False

    def check_finsihed(self):
        for char in self.correct_word:
            if self.has_already_guessed(char) == False:
                return False
        return True

    def get_print_string(self):
        print_string = ""
        for char in self.correct_word:
            if self.has_already_guessed(char.upper()):
                print_string += "["+char+"]"
            else:
                print_string += "[?]"
        return print_string



