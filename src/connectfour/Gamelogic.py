import numpy as np

from connectfour.Game import ConnectFourGame
from discord.ext import commands
import discord


class ConnectFourGameLogic(commands.Cog):
    def __init__(self, bot):
        self.games = []
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
            channel: discord.TextChannel = await guild.create_text_channel(name="🔴🔵connectfour-"+ str(len(self.games) + 1),category=self.bot.get_channel(742406887567392878))
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
            embed = discord.Embed(title="",description=str(np.flip(gamefield)),color=discord.Color.green())
            embed.set_author(name="ConnectFour",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            message = await self.bot.get_channel(channelid).send(embed=embed)
            gameobject = ConnectFourGame(gameplayerids, channelid, self.bot, message, gamefield)
            self.bot.add_cog(gameobject)
            self.games.append(gameobject)
            await message.add_reaction("1️⃣")
            await message.add_reaction('2️⃣')
            await message.add_reaction('3️⃣')
            await message.add_reaction('4️⃣')
            await message.add_reaction('5️⃣')
            await message.add_reaction('6️⃣')
            await message.add_reaction("7️⃣")
            break

    @commands.command()
    async def connectfour(self, ctx: commands.Context, *, member: discord.Member = None):
        member = ctx.author or member
        await ctx.message.delete()
        commandchannel = ctx.channel
        if commandchannel.id == self.joinchannel:
            #if member.id in self.queue:
             #   self.queue.remove(member.id)
              #  embed = discord.Embed(title="See you soon!", description=f"""{member.display_name} left the Queue""",color=0x49ff35)
             #   embed.set_author(name="ConnectFour",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
             #   embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
              #  await ctx.channel.send(embed=embed)
              #  return
            embed = discord.Embed(title="Nice!", description=f"""{member.display_name} Joined the Queue""", color=0x49ff35)
            embed.set_author(name="ConnectFour", icon_url = "https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.add_field(name="But:", value="It may take a moment for the game to start, so sit back and relax", inline=False)
            embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.set_footer(text="Thanks vor Playing!")
            await ctx.channel.send(embed=embed, delete_after=10)
            await self.add_to_queue(member.id)







