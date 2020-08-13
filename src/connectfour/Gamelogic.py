import asyncio
import io

import numpy as np
from PIL import Image

from connectfour.Game import ConnectFourGame
from discord.ext import commands
import discord


class ConnectFourGameLogic(commands.Cog):
    def __init__(self, bot):
        self.channels_in_use = {
        }
        self.queue = []
        self.bot: commands.Bot = bot
        self.joinchannel = 743425069216170024

    async def add_to_queue(self, memberid):
        self.queue.append(memberid)
        await self.check_for_gamestart()

    #After a player join or a game finsihed do this function
    async def check_for_gamestart(self):
        while(len(self.queue) > 1):
            guild: discord.Guild = self.bot.get_guild(741823660188500008)
            channel: discord.TextChannel = await guild.create_text_channel(name="🔴🔵connectfour-"+ str(len(self.channels_in_use) + 1),category=self.bot.get_channel(742406887567392878))
            channelid = channel.id
            gameplayerids = [self.queue.pop(0), self.queue.pop(0)]
            gamefield = np.zeros((6, 7))
            embed = discord.Embed(title="Game is starting!", description="Playing in Channel: **" + self.bot.get_channel(channelid).name + "** !", color=0x2dff32)
            embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.set_author(name="ConnectFour",
                             icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.add_field(name="Players",
                            value=f"""{self.bot.get_user(gameplayerids[0]).display_name} vs. {self.bot.get_user(gameplayerids[1]).display_name}""",
                            inline=True)
            embed.set_footer(text="Thanks for Playing!")
            channel = self.bot.get_channel(self.joinchannel)
            await channel.send(embed=embed, delete_after=10)
            message = await self.bot.get_channel(channelid).send(file=await self.build_board(gamefield))
            gameobject = ConnectFourGame(gameplayerids, channelid, self.bot, gamefield, message)
            gameobject.is_in_action = True
            self.bot.add_cog(gameobject)
            self.channels_in_use[channelid] = gameobject
            await message.add_reaction("1️⃣")
            await message.add_reaction('2️⃣')
            await message.add_reaction('3️⃣')
            await message.add_reaction('4️⃣')
            await message.add_reaction('5️⃣')
            await message.add_reaction('6️⃣')
            await message.add_reaction("7️⃣")
            gameobject.is_in_action = False
            break

    async  def build_board(self, gamefield: np.matrix):
        field_img: Image.Image = Image.open("../resources/connectfour/field.png")
        o = Image.open("../resources/connectfour/o_universe.png")

        X = Image.open("../resources/connectfour/x_universe.png")

        fields = [[(34, 34),  (184, 34),   (334, 34),  (484, 34), (634, 34),  (784, 34),  (934, 34)],
                  [(34, 184), (184, 184), (334, 184), (484, 184), (634, 184), (784, 184), (934, 184)],
                  [(34, 334), (184, 334), (334, 334), (484, 334), (634, 334), (784, 334), (934, 334)],
                  [(34, 484), (184, 484), (334, 484), (484, 484), (634, 484), (784, 484), (934, 484)],
                  [(34, 634), (184, 634), (334, 634), (484, 634), (634, 634), (784, 634), (934, 634)],
                  [(34, 784), (184, 784), (334, 784), (484, 784), (634, 784), (784, 784), (934, 784)]]
        fields.reverse()

        for i in range(len(gamefield)):
            for x in range(len(gamefield[i])):
                if gamefield[i][x] == 1:
                    field_img.paste(X, fields[i][x], X)
                if gamefield[i][x] == 2:
                    field_img.paste(o, fields[i][x], o)

        arr = io.BytesIO()
        field_img.save(arr, format="png")
        basewidth = 250
        wpercent = (basewidth/float(field_img.size[0]))
        hsize = int((float(field_img.size[1])*float(wpercent)))
        field_img = field_img.resize((basewidth,hsize), Image.ANTIALIAS)
        arr = io.BytesIO()
        field_img.save(arr, format="png")
        arr.seek(0)
        file = discord.File(arr)
        file.filename = "field.png"
        return file

    @commands.command()
    async def connectfour(self, ctx: commands.Context, *, member: discord.Member = None):
        member = ctx.author or member
        await ctx.message.delete()
        commandchannel = ctx.channel
        if commandchannel.id == self.joinchannel:
            #if member.id in self.queue:
            #    self.queue.remove(member.id)
            #    embed = discord.Embed(title="See you soon!", description=f"""{member.display_name} left the Queue""",color=0x49ff35)
            #    embed.set_author(name="ConnectFour",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            #    embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            #    await ctx.channel.send(embed=embed, delete_after=10)
            #    return
            embed = discord.Embed(title="Nice!", description=f"""{member.display_name} Joined the Queue""", color=0x49ff35)
            embed.set_author(name="ConnectFour", icon_url = "https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.add_field(name="But:", value="It may take a moment for the game to start, so sit back and relax", inline=False)
            embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.set_footer(text="Thanks vor Playing!")
            await ctx.channel.send(embed=embed, delete_after=10)
            await self.add_to_queue(member.id)

    async def stop(self, channel_id):
        game = self.channels_in_use[channel_id]
        await game.bot.get_channel(game.channelid).delete()
        game.bot.remove_cog(game)
        self.channels_in_use.pop(channel_id)

    async def sendmessage(self, game):
        await game.gamefield_message.delete()
        game.gamefield_message = await self.bot.get_channel(game.channelid).send(file=await self.build_board(game.gamefield))
        await game.gamefield_message.add_reaction("1️⃣")
        await game.gamefield_message.add_reaction('2️⃣')
        await game.gamefield_message.add_reaction('3️⃣')
        await game.gamefield_message.add_reaction('4️⃣')
        await game.gamefield_message.add_reaction('5️⃣')
        await game.gamefield_message.add_reaction('6️⃣')
        await game.gamefield_message.add_reaction("7️⃣")

    @commands.Cog.listener()
    async def on_reaction_add(self, payload: discord.Reaction, user):
        if self.channels_in_use.__contains__(payload.message.channel.id):
            game: ConnectFourGame = self.channels_in_use.get(payload.message.channel.id)
            if payload.message.id == game.gamefield_message.id:
                if user.id in game.playerids:
                    if game.is_in_action == False:
                        game.is_in_action = True
                        await game.gamefield_message.remove_reaction(payload.emoji, game.bot.get_user(user.id))
                        if user.id == game.playerids[game.aktplayer]:
                            emojis = {
                                "1️⃣": 0,
                                '2️⃣': 1,
                                '3️⃣': 2,
                                '4️⃣': 3,
                                '5️⃣': 4,
                                '6️⃣': 5,
                                "7️⃣": 6
                            }

                            col = emojis[payload.emoji]
                            if col != None:
                                if await game.is_location_valid(col):
                                    row = await game.get_next_row(col)
                                    await game.insert_selected(row, col, game.aktplayer)
                                    await self.sendmessage(game)

                                    game.aktplayer += 1
                                    if game.aktplayer == 2:
                                        game.aktplayer = 0
                                if not await game.check_state(game.aktplayer):
                                    embed = discord.Embed(title=":tada: " + game.bot.get_user(game.playerids[game.aktplayer]).display_name + " won :tada:",colour=discord.Colour.green())
                                    await game.bot.get_channel(game.channelid).send(embed=embed, delete_after=10)
                                    await asyncio.sleep(5)
                                    await self.stop(game.channelid)

                        game.is_in_action = False
                    else:
                        try:
                            await payload.message.remove_reaction(payload.emoji, game.bot.get_user(user.id))
                        except:
                            return

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if self.channels_in_use.__contains__(message.channel.id):
            game: ConnectFourGame = self.channels_in_use.get(message.channel.id)
            if message.channel.id == game.channelid:
                if message.author != game.bot.user:
                    await message.delete()







