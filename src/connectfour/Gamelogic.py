from src.connectfour.Game import Game
from discord.ext import commands
import discord


class ConnectFourGameLogic(commands.Cog):
    def __init__(self, bot):
        self.games = []
        self.channel_ids = [
            742406934317236346,
            742407045944442991,
            742407072125157377
        ]
        self.queue = []
        self.bot = bot
        self.join_channel = 742407492520378418

    def get_available_channel_id(self):
        free_channels = self.channel_ids
        for game_object in self.games:
            free_channels.remove(game_object.channelid)
        if len(free_channels) > 0:
            return free_channels[0]
        else:
            return False

    def add_to_queue(self, member):
        self.queue.append(member)
        self.check_for_gamestart()

    # After a player join or a game finished do this function
    def check_for_gamestart(self):
        while len(self.queue) > 1:
            channel_id = self.get_available_channel_id()
            if channel_id is not False:
                game_players = [self.queue.pop(0), self.queue.pop(1)]
                game_object = Game(game_players, channel_id)
                self.games.append(game_object)
                # TODO: Send Message to the 2 players in wich channel they play (get channel name by channel id)
                break
            else:
                # TODO: Send Message in chat that at the moment there is no free channel to play
                return
        # TODO: Send Message to all left player in queue that they have to wait...

    @commands.command()
    async def connect_four(self, ctx: discord.ext.commands.Context, *, member: discord.Member = None):
        member = member or ctx.author
        command_channel = ctx.channel
        if command_channel.id == self.join_channel:
            embed = discord.Embed(title="Nice!", description="You Joined the Queue", color=0x49ff35)
            embed.set_author(name="ConnectFour")
            embed.add_field(name="But:", value="It may take a moment for the game to start, so sit back and relax",
                            inline=False)
            embed.set_footer(text="Thanks vor Playing!")
            await ctx.channel.send(embed=embed)
            self.add_to_queue(member)
