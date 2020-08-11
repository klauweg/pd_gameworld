from src.connectfour import Game
from discord.ext import commands
import discord


class ConnectFourGameLogic(commands.Cog):
    def __init__(self, botvar):
        self.games = []
        self.channelids = [
            742406934317236346,
            742407045944442991,
            742407072125157377
        ]
        self.queue = []
        self.bot = botvar
        self.joinchannel = 742407492520378418

    #Is a Channel id availible to play?
    def get_availible_channel_id(self):
        freechannels = self.channelids
        for gameobject in self.games:
            freechannels.remove(gameobject.channelid)
        if len(freechannels) > 0:
            return freechannels[0]
        else:
            return False

    def add_to_queue(self, member):
        self.queue.append(member)
        self.check_for_gamestart()

    #After a player join or a game finsihed do this function
    def check_for_gamestart(self):
        while(len(self.queue) > 1):
            channelid = self.get_availible_channel_id()
            if not channelid == False:
                gameplayers = [self.queue.pop(0), self.queue.pop(1)]
                gameobject = Game(gameplayers, channelid, self.bot)
                self.bot.add_cog(gameobject)
                self.games.append(gameobject)
                # TODO: Send Message to the 2 players in wich channel they play (get channel name by channel id)
                break
            else:
                # TODO: Send Message in chat that at the moment there is no free channel to play
                return
        # TODO: Send Message to all left player in queue that they have to wait...

    @commands.command()
    async def connectfour(self, ctx: discord.ext.commands.Context, *, member: discord.Member = None):
        member = member or ctx.author
        commandchannel = ctx.channel
        if(commandchannel.id == self.joinchannel):
            self.add_to_queue(member)
            embed = discord.Embed(title="Nice!", description=f"""{member.display_name} Joined the Queue""", color=0x49ff35)
            embed.set_author(name="ConnectFour")
            embed.add_field(name="But:", value="It may take a moment for the game to start, so sit back and relax", inline=False)
            queueplayernames = ""
            for member in self.queue:
                queueplayernames = queueplayernames + (member.display_name + " ")
            embed.add_field(name="Queue:", value=queueplayernames, inline=False)
            embed.set_footer(text="Thanks vor Playing!")
            message = await ctx.channel.send(embed=embed)
            emoji = '\N{THUMBS UP SIGN}'
            await message.add_reaction(emoji)






