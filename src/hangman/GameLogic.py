import random

import discord
from discord.ext import commands

from GameAPI.Queue import Queue

from threading import Timer

from hangman.Game import Game


class HangManGameLogic(commands.Cog):
    def __init__(self, bot):
        self.games = []
        self.channelids = [743386550225600573, 743386626587361393, 743386652462022717]
        self.bot: commands.Bot = bot
        self.queue: Queue = Queue()
        self.joinchannel = 743386731453087756
        self.timer: Timer = None


    #Is a Channel id availible to play?
    async def get_availible_channel_id(self):
        freechannels = self.channelids
        for gameobject in self.games:
            freechannels.remove(gameobject.channelid)
        if len(freechannels) > 0:
            return freechannels[0]
        else:
            return False

    async def add_to_queue(self, memberid):
        self.queue.put(memberid)
        await self.check_for_gamestart()

    #After a player join or a game finsihed do this function
    async def check_for_gamestart(self):
        if self.queue.__len__() > 1:
            channelid = await self.get_availible_channel_id()
            if not channelid == False:
                if self.queue.__len__() == 2:
                    self.timer = Timer(60, await self.start_game(self.queue.queue, channelid))
                    self.timer.start()
                    embed = discord.Embed(title="Game is starting...", description="Startet Timer (30 seconds) to allow other players to join in", color=0x58ff46)
                    embed.set_author(name="Hangman", icon_url = "https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    await self.bot.get_channel(self.joinchannel).send(embed=embed, delete_after=10)
                    return
                if self.queue.__len__() == 8:
                    await self.start_game(self.queue.queue, channelid)
                    self.queue.queue.clear()
                    self.timer.cancel()
                    return
        else:
            if self.timer is not None:
                self.timer.cancel()


    async def start_game(self, playerids, channelid):
        embed = discord.Embed(title="Enter correctword", description="You have to write the word here which the others have to guess")
        embed.set_author(name="Hangman", icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        notguessingplayerid = random.choice(playerids)
        playerids.remove(notguessingplayerid)
        await self.bot.get_user(notguessingplayerid).send(embed=embed, delete_after=10)
        hangmangame = Game(playerids, channelid, self.bot, notguessingplayerid)
        self.bot.add_cog(hangmangame)
        self.games.append(hangmangame)
        embed = discord.Embed(title="Game is starting!", description="Game takes place in " + self.bot.get_channel(channelid).name, color=0x58ff46)
        embed.set_author(name="Hangman", icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        playernames = ""
        for id in playerids:
            playernames += (self.bot.get_user(id).display_name + " ")
        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.add_field(name="Players",value=playernames, inline=True)
        await self.bot.get_channel(self.joinchannel).send(embed=embed, delete_after=10)
        return

    @commands.command()
    async def hangman(self, ctx: commands.Context, *, member: discord.Member = None):
        member = ctx.author or member

        commandchannel = ctx.channel
        if commandchannel.id == self.joinchannel:

            #if member.id in self.queue:
             #   self.queue.remove(member.id)
             #   embed = discord.Embed(title="See you soon!", description=f"""{member.display_name} left the Queue""",color=0x49ff35)
             #   embed.set_author(name="Hangman",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
             #   embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
             #   await ctx.channel.send(embed=embed)
             #   return

            embed = discord.Embed(title="Nice!", description=f"""{member.display_name} Joined the Queue""", color=0x49ff35)
            embed.set_author(name="Hangman", icon_url = "https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.add_field(name="But:", value="It may take a moment for the game to start, so sit back and relax", inline=False)
            embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.set_footer(text="Thanks vor Playing!")
            await ctx.channel.send(embed=embed, delete_after=10)
            await self.add_to_queue(member.id)