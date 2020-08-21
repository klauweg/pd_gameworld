import asyncio
import io
import random

import discord
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands

from GameAPI.PlayerDataApi import Utils
from GameAPI.Queue import Queue

from threading import Timer
from hangman.Game import Game
from parse import parse

channel_prefix = "🪓hangman-"


class HangManGameLogic(commands.Cog):
    def __init__(self, queue):
        self.queue = queue
        self.timer: Timer = None
        self.queue.add_action = self.check_for_gamestart

    #After a player join or a game finsihed do this function
    async def check_for_gamestart(self):
        if self.queue.len() >= 2:
            if self.queue.len() == 2:
                await asyncio.sleep(5) #TODO: NOCH IN 30 SEKUNDEN UMWANDELN
                Game(self.queue.queue)
                return
            if self.queue.len() == 8:
                Game(self.queue.queue)
                self.queue.queue.clear()
                self.timer.cancel()
                return
        else:
            if self.timer is not None:
                self.timer.cancel()


class Game(commands.Cog):
    def __init__(self, contexts):
        self.correct_word = None
        self.players = [ctx.author for ctx in contexts]
        self.not_guessing_player = None
        self.joinchannel = contexts[0].channel
        self.gamechannel = None
        self.guessed_letters = []
        self.gamestate = 0
        self.bot: commands.Bot = contexts[0].bot
        self.guild = contexts[0].guild
        self.message: discord.Message = None
        self.loose_level = 0
        self.is_in_action = False
        self.bot.add_cog(self)

        self.bot.loop.create_task(self.prepare_game())  # __init__ darf nicht async sein!

    async def prepare_game(self):
        # Suche ersten freien Channelslot
        cparse = lambda channel: parse( channel_prefix+"{:d}", channel.name ) # Parsefunktion für die Channelnames
        snums = sorted( [ cparse(c)[0] for c in self.bot.get_all_channels() if cparse(c) ] ) # extract
        next_channel = next( (x[0] for x in enumerate(snums) if x[0]+1 != x[1]), len(snums) ) + 1 #search gap
        # Spielchannel erzeugen:
        self.gamechannel = await self.guild.create_text_channel(
            name=channel_prefix + str(next_channel),
            category=self.bot.get_channel(743386428624601200))
        # Nachricht im Joinchannel:
        embed = discord.Embed(title="Game is starting!",description="Playing in Channel: **" + self.gamechannel.name + "** !",color=0x2dff32)
        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_author(name="ConnectFour",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.add_field(name="Players", value=f"""{self.players[0].display_name} vs. {self.players[1].display_name}""",inline=True)
        embed.set_footer(text="Have fun!")
        await self.joinchannel.send(embed=embed, delete_after=10)

        self.not_guessing_player = random.choice(self.players)
        self.players.remove(self.not_guessing_player)

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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (not self.is_in_action) and (message.author.id is not self.bot.user.id):
            print("message alone  author")
            self.is_in_action = True
            if self.gamestate == 0:
                if message.channel.type == discord.ChannelType.private and message.author.id == self.not_guessing_player.id:
                    if message.content.isalpha():
                        if len(message.content) <= 15:
                            self.correct_word = message.content.upper()
                            self.gamestate = 1
                            await self.gamechannel.purge()
                            embed = discord.Embed(title="Done!", description="Your can now return to "+self.gamechannel.name+"!",color=0x58ff46)
                            embed.set_author(name="Hangman",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                            embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                            await self.not_guessing_player.send(embed=embed, delete_after=10)

                            await self.send_gamefield()
                        else:
                            embed = discord.Embed(title="Attention", description="Less than 15 characters!",color=0xff4646)
                            embed.set_author(name="Hangman",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                            embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                            await self.not_guessing_player.send(embed=embed, delete_after=10)
                    else:
                        embed = discord.Embed(title="Attention", description="Your word can only contains letters!", color=0xff4646)
                        embed.set_author(name="Hangman", icon_url = "https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        await self.not_guessing_player.send(embed=embed, delete_after=10)
                else:
                    await message.delete()
                self.is_in_action = False
                return
            if message.channel.id == self.channelid and message.author.id is not self.not_guessing_player.id and message.author in self.players:
                await message.delete()
                if message.content.upper() == self.correct_word:
                    embed = discord.Embed(title=":tada: " + message.author.display_name + " has guessed the Word! :tada:", description="Thanks for playing!", color=0x58ff46)
                    embed.set_author(name="Hangman",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    await self.gamechannel.send(embed=embed)
                    await Utils.add_xp(message.author, 30)
                    await Utils.add_to_stats(message.author, "HangMan", 1, 0)
                    for player in self.players:
                        await Utils.add_to_stats(player, "HangMan", 0, 1)
                    await asyncio.sleep(10)
                    await self.gamechannel.delete()
                    self.bot.remove_cog(self)
                    return
                elif self.is_valid_guess(message.content.upper()):
                    if not self.has_already_guessed(message.content.upper()):
                        await self.guess(message.content.upper())
                        await self.send_gamefield()
                        if self.loose_level == 10:
                            embed = discord.Embed(title="You loose:", description="Hangman was hanged!", color=0x58ff46)
                            embed.set_author(name="Hangman", icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                            embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                            await self.gamechannel.send(embed=embed)
                            for player in self.players:
                                await Utils.add_to_stats(player, "HangMan", 0, 1)
                            await asyncio.sleep(10)
                            await self.gamechannel.delete
                            self.bot.remove_cog(self)
                self.is_in_action = False
                return
            else:
                self.is_in_action = False
                try:
                    await message.delete()
                except:
                    return
        else:
            try:
                await message.delete()
            except:
                return

    async def send_gamefield(self):
        # ggf. altes Spielfeld löschen:
        if self.message:
            await self.message.delete()
        self.gamefield_message = await self.gamechannel.send(file=await self.build_board())


    async def build_board(self):
        field_img: Image.Image = Image.open("../resources/hangman/message.png")
        draw = ImageDraw.Draw(field_img)
        lfont = ImageFont.truetype('../resurces/hangman/arial.ttf', 30)
        arr = io.BytesIO()
        draw.text((9, 51), self.get_print_string(), (0, 0, 0), font=lfont)
        draw.text((9, 170), str(self.loose_level * 10) + "/100%", (0, 0, 0), font=lfont)
        field_img.save(arr, format="png")
        arr.seek(0)
        file = discord.File(arr)
        file.filename = "field.png"
        return file

    def get_print_string(self):
        print_string = ""
        for char in self.correct_word:
            if self.has_already_guessed(char.upper()):
                print_string += "["+char+"]"
            else:
                print_string += "[?]"
        return print_string