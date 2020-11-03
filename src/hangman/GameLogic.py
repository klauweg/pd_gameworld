import asyncio
import io
import random

import discord
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands

from parse import parse

from GameAPI.user_extension import add_to_stats, add_xp, deposit_money

channel_prefix = "🪓galgenmännchen-"


class GameControl():
    def __init__(self, queue):
        self.queue = queue
        self.queue.on_queue_change = self.check_for_game_start
        self.task: asyncio.Task = None

    async def timer(self, time):
        await asyncio.sleep(time)
        elements = []
        for i in range(self.queue.len()):
            elements.append(self.queue.pop())
        Game(elements, self.queue)

    def check_for_game_start(self):
            if self.queue.len() == 2:
                if self.task:
                    self.task.cancel()
                self.task = asyncio.create_task(self.timer(5))
            if self.queue.len() == 8:
                if self.task:
                    self.task.cancel()
                self.task = asyncio.create_task(self.timer(0))
            if self.queue.len() < 2:
                if self.task:
                    self.task.cancel()

class Game(commands.Cog):
    def __init__(self, contexts, queue):
        self.correct_word = None
        self.queue = queue
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
        self.turn_lock = asyncio.Lock()
        self.running = True
        self.turnevent = asyncio.Event()
        self.bot.loop.create_task(self.gametask())

    async def gametask(self):
        # Suche ersten freien Channelslot
        cparse = lambda channel: parse( channel_prefix+"{:d}", channel.name ) # Parsefunktion für die Channelnames
        snums = sorted( [ cparse(c)[0] for c in self.bot.get_all_channels() if cparse(c) ] ) # extract
        next_channel = next( (x[0] for x in enumerate(snums) if x[0]+1 != x[1]), len(snums) ) + 1 #search gap
        # Spielchannel erzeugen:
        self.gamechannel = await self.guild.create_text_channel(name=channel_prefix + str(next_channel),category=self.bot.get_channel(743386428624601200))

        # Nachricht im Joinchannel:
        embed = discord.Embed(title="Game startet!",description="Es wird gespielt in: **" + self.gamechannel.name + "** !",color=0x2dff32)
        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_author(name="Galgenmännchen",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_footer(text="Viel Spaß!")
        await self.joinchannel.send(embed=embed, delete_after=10)

        self.not_guessing_player = random.choice(self.players)
        self.players.remove(self.not_guessing_player)

        embed = discord.Embed(title="Warum sehe ich nichts?",description=self.not_guessing_player.display_name + " hat eine Private nachricht bekommen. Dort muss er das Wort eingeben welches die anderen erraten müssen",color=0x58ff46)
        embed.set_author(name="Galgenmännchen",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        await self.gamechannel.send(embed=embed, delete_after=60)

        embed = discord.Embed(title="Jetzt,", description="musst du das Wort zurückschreiben welches die anderen in " + self.gamechannel.name + " erraten sollen!",color=0x58ff46)
        embed.set_author(name="Galgenmännchen",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        await self.not_guessing_player.send(embed=embed, delete_after=60)

        self.bot.add_cog(self)

        while self.running:
            try:
                await asyncio.wait_for( self.turnevent.wait(), timeout=300 )
            except asyncio.TimeoutError:
                embed = discord.Embed(title="Game gestoppt:", description="(Timeout)", color=0x58ff46)
                embed.set_author(name="Galgenmännchen",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await self.gamechannel.send(embed=embed)
                break;

        for player in self.players:
            add_to_stats(player, "HangMan", 0, 1, 0)
            add_xp(player, 5)
            self.queue.release_player(player.id)
        add_xp(self.not_guessing_player, 5)
        add_to_stats(self.not_guessing_player,"HangMan", 0,1)
        self.queue.release_player(self.not_guessing_player.id)
        self.bot.remove_cog(self)
        await asyncio.sleep(10)
        await self.gamechannel.delete()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id == self.gamechannel.id and message.author.id is not self.bot.user.id:
            await message.delete()

        if self.gamestate == 0:
            if message.channel.type == discord.ChannelType.private and message.author.id == self.not_guessing_player.id:
                if message.content.isalpha():
                    if len(message.content) <= 15:
                        self.correct_word = message.content.upper()
                        self.gamestate = 1
                        await self.gamechannel.purge()
                        embed = discord.Embed(title="Done!", description="Du kannst nun zu " + self.gamechannel.name + " zurückkehren!",color=0x58ff46)
                        embed.set_author(name="Galgenmännchen",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        await self.not_guessing_player.send(embed=embed, delete_after=10)
                        await self.send_gamefield()
                        self.gamestate = 1
                    else:
                        embed = discord.Embed(title="Achtung", description=" Weniger als 15 Buchstaben!", color=0xff4646)
                        embed.set_author(name="Galgenmännchen",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        await self.not_guessing_player.send(embed=embed, delete_after=10)
                else:
                    embed = discord.Embed(title="Achtung", description="Dein Word darf nur Buchstaben enthalten!",color=0xff4646)
                    embed.set_author(name="Galgenmännchen",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    await self.not_guessing_player.send(embed=embed, delete_after=10)
                self.turnevent.set()
                return
        elif self.gamestate == 1:
            if message.channel.id == self.gamechannel.id and message.author.id is not self.not_guessing_player.id and message.author in self.players:
                if message.content.upper() == self.correct_word:
                    embed = discord.Embed(title=":tada: " + message.author.display_name + " hat das Wort erraten! :tada:",description="Danke fürs Spielen!", color=0x58ff46)
                    embed.set_author(name="Galgenmännchen",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    embed.add_field(name="Das Wort war:", value=self.correct_word, inline=False)
                    await self.gamechannel.send(embed=embed)
                    add_xp(message.author, 30)
                    add_to_stats(message.author, "HangMan", 1, 0, 0)
                    deposit_money(message.author, 20)
                    self.running = False
                elif self.is_valid_guess(message.content.upper()):
                    self.guess(message.content.upper())
                    await self.send_gamefield()
                    if self.loose_level == 10:
                        embed = discord.Embed(title="Du hast verloren:", description="Hangman wurde erhängt!", color=0x58ff46)
                        embed.set_author(name="Galgenmännchen",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        embed.add_field(name="Das Wort war:", value=self.correct_word, inline=False)
                        await self.gamechannel.send(embed=embed)
                        add_xp(self.not_guessing_player, 30)
                        add_to_stats(self.not_guessing_player, "HangMan", 1, 0, 0)
                        deposit_money(self.not_guessing_player, 20)
                        self.running = False
                self.turnevent.set()
                return

    def guess(self, letter):
        self.guessed_letters.append(letter)
        if letter not in self.correct_word:
            self.loose_level += 1

    def is_valid_guess(self, string):
        if not self.has_already_guessed(string):
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

    async def send_gamefield(self):
        # ggf. altes Spielfeld löschen:
        if self.message:
            await self.message.delete()
        self.message = await self.gamechannel.send(file=await self.build_board())


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