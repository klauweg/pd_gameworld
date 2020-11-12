

################ TODO

import asyncio

import random

import discord

from discord.ext import commands

from parse import parse

from GameAPI.user_extension import add_to_stats, add_xp, deposit_money

channel_prefix = "💬onewordchallange-"


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
                self.task = asyncio.create_task(self.timer(30))
            if self.queue.len() == 8:
                if self.task:
                    self.task.cancel()
                self.task = asyncio.create_task(self.timer(0))
            if self.queue.len() < 2:
                if self.task:
                    self.task.cancel()

class Game(commands.Cog):
    def __init__(self, contexts, queue):
        self.sentence = ""
        self.queue = queue
        self.players = [ctx.author for ctx in contexts]
        random.shuffle(self.players)
        self.nextplayer = 0
        self.joinchannel = contexts[0].channel
        self.gamechannel = None
        self.guessed_letters = []
        self.bot: commands.Bot = contexts[0].bot
        self.guild = contexts[0].guild
        self.message: discord.Message = None
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
        self.gamechannel = await self.guild.create_text_channel(name=channel_prefix + str(next_channel),category=self.bot.get_channel(771386811154300958))

        role = self.guild.get_role(741823660188500008)
        await self.gamechannel.set_permissions(role, read_messages=False)
        for player in self.players:
            await self.gamechannel.set_permissions(player, read_messages=True)

        # Nachricht im Joinchannel:
        embed = discord.Embed(title="Spiel startet!",description="Es wird gespielt in: **" + self.gamechannel.name + "** !",color=0x2dff32)
        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_author(name="OneWordChallange",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_footer(text="Viel Spas!")
        await self.joinchannel.send(embed=embed, delete_after=10)

        embed = discord.Embed(title="Also, " + self.players[self.nextplayer].name + ", bitte beginne und schreibe den Satzanfang",description="",color=0x58ff46)
        embed.set_author(name="OneWordChallange",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        await self.gamechannel.send(embed=embed, delete_after=60)

        self.bot.add_cog(self)

        while self.running:
            try:
                await asyncio.wait_for( self.turnevent.wait(), timeout=300 )
            except asyncio.TimeoutError:
                embed = discord.Embed(title="Spiel Gestoppt:", description="(Timeout)", color=0x58ff46)
                embed.set_author(name="OneWordChallange",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await self.gamechannel.send(embed=embed)
                break;

        for player in self.players:
            add_to_stats(player, "OneWordChallange", 0, 1, 0)
            add_xp(player, 10)
            deposit_money(player, 5)
            self.queue.release_player(player.id)
        self.bot.remove_cog(self)
        await asyncio.sleep(25)
        await self.gamechannel.delete()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id == self.gamechannel.id and message.author.id is not self.bot.user.id:
            try:
                await message.delete()
            except:
                pass

            undoplayer = self.nextplayer - 1
            if undoplayer < 0:
                undoplayer = len(self.players) - 1
            if message.author.id == self.players[undoplayer].id:
                if (message.content.upper() == "!UNDO"):
                    self.sentence = self.sentence.rsplit(' ', 1)[0]

                    embed = discord.Embed(title="Undo!", description="Du hast das letzte Word gelöscht!", color=0x58ff46)
                    embed.set_author(name="OneWordChallange",
                                     icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    embed.set_thumbnail(
                        url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    await self.gamechannel.send(embed=embed, delete_after=6)

                    self.nextplayer = undoplayer

                    await self.send_gamefield()
                    return
            elif message.author in self.players and message.author.id == self.players[self.nextplayer].id:
                if(message.content.upper() == "!KOMMA"):
                    self.sentence = self.sentence + ", "

                    embed = discord.Embed(title="Komma!",description="Du hast ein Komma eingefügt!", color=0x58ff46)
                    embed.set_author(name="OneWordChallange",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    await self.gamechannel.send(embed=embed, delete_after=6)

                    await self.send_gamefield()
                else:
                    if message.content.upper() == ".":
                        embed = discord.Embed(title=":tada: " + message.author.name + " Hat den Punkt gesetzt! :tada:",description="("+ self.sentence +" )", color=0x58ff46)
                        embed.set_author(name="OneWordChallange",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        await self.gamechannel.send(embed=embed)
                        self.running = False
                    elif(message.content.isalpha()):
                        self.sentence = self.sentence + " " + message.content
                        self.nextplayer = self.nextplayer + 1
                        if(self.nextplayer >= len(self.players)):
                            self.nextplayer = 0
                        await self.send_gamefield()
                    else:
                        embed = discord.Embed(title=message.author.name + ": Falsche Eingabe",description="Bitte benutze nur Buchstaben, einen Punkt oder !undo bzw. !komma !", color=0x58ff46)
                        embed.set_author(name="OneWordChallange",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        await self.gamechannel.send(embed=embed, delete_after=6)

                self.turnevent.set()
                return

    async def send_gamefield(self):
        # ggf. altes Spielfeld löschen:
        if self.message:
            embed = discord.Embed(title="Euer Satz:", description=self.sentence + ".", color=0x58ff46)
            embed.set_author(name="OneWordChallange",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.add_field(name="Nächster Spieler:",
                        value=self.players[self.nextplayer].name,
                        inline=True)
            await self.message.edit(embed=embed)
            return
        embed = discord.Embed(title="Euer Satz:", description=self.sentence + ".", color=0x58ff46)
        embed.set_author(name="OneWordChallange",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.add_field(name="Nächster Spieler:",
                        value=self.players[self.nextplayer].name,
                        inline=True)
        self.message = await self.gamechannel.send(embed=embed)