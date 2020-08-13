import discord
from discord.ext import commands


class Game(commands.Cog):
    def __init__(self, playerids, channelid,  bot, notguessingplayerid):
        self.correct_word = None
        self.playerids = playerids
        self.not_guessing_player_id = notguessingplayerid
        self.channelid = channelid
        self.guessed_letters = []
        self.gamestate = 0
        self.bot: commands.Bot = bot
        self.message: discord.Message = None
        self.loose_level = 0

    async def guess(self, letter):
        self.guessed_letters.append(letter)

        if letter not in self.correct_word:
            self.loose_level += 1

        embed = discord.Embed(title="You have to guess:", description=self.get_print_string(), color=0x58ff46)
        embed.set_author(name="Hangman", icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.add_field(name="HangMan-Hung:", value=str(self.loose_level*10) + "**/100 %**", inline=False)

        await self.message.edit(embed=embed)

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

    def check_finsihed(self):
        for char in self.correct_word:
            if self.has_already_guessed(char) == False:
                return False
        return True

    def get_print_string(self):
        print_string = ""
        for char in self.correct_word:
            if self.has_already_guessed(char.upper()):
                print_string += "[ "+char+" ]"
            else:
                print_string += "[ ? ]"
        return print_string



