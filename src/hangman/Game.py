import random

import discord
from discord.ext import commands


class Game(commands.Cog):
    def __init__(self, channelid, playerids, bot, notguessingplayerid):
        self.correct_word = None
        self.playerids = playerids
        self.not_guessing_player_id = notguessingplayerid
        self.channelid = channelid
        self.guessed_letters = []
        self.gamestate = 0
        self.bot: commands.Bot = bot
        self.message: discord.Message = None
        self.loose_level = 0

    def guess(self, letter):
        self.guessed_letters.append(letter)

        if letter not in self.correct_word:
            self.loose_level += 1
            print(self.loose_level)

        embed = discord.Embed(title="Word", description="The Word is " + self.get_print_string(), color=0x58ff46)
        embed.set_author(name="Hangman", icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        self.message.edit(embed=embed)

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
                print_string += char
            else:
                print_string += "_"
        return print_string

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if self.gamestate == 0:
            if message.author.id == self.not_guessing_player_id and message.channel.type == discord.ChannelType.private:
                if message.content.isalpha():
                    self.correct_word = message.content.upper()
                    self.gamestate = 1
                    embed = discord.Embed(title="Done!", description="Your can now return to "+self.bot.get_channel(self.channelid).name+"!",color=0x58ff46)
                    embed.set_author(name="Hangman",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    await self.bot.get_user(self.not_guessing_player_id).send(embed=embed, delete_after=10)

                    embed = discord.Embed(title="Word", description="The Word is " + self.get_print_string(), color=0x58ff46)
                    embed.set_author(name="Hangman",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    self.message = await self.bot.get_channel(self.channelid).send(embed=embed, delete_after=10)
                else:
                    embed = discord.Embed(title="Attention", description="Your word can only contains letters!", color=0xff4646)
                    embed.set_author(name="Hangman", icon_url = "https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    await self.bot.get_user(self.not_guessing_player_id).send(embed=embed, delete_after=10)
            return
        if message.channel.id == self.channelid and message.author.id != self.not_guessing_player_id and message.author.id in self.playerids:
            if message.author.id is not self.not_guessing_player_id:
                if message.content.upper() == self.correct_word:
                    print("won")
                    # TODO: PRINT WON MESSAGE ETC.
                elif self.is_valid_guess(message.content.upper) and not self.has_already_guessed(message.content.upper()):
                    self.guess(message.content)

            return
