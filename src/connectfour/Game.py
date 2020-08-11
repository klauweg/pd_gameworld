import numpy as np
from discord.ext import commands

class Game(commands.Cog):

    def __init__(self, playerlist, cid, botvar):
        self.row_count = 6
        self.column_count = 7
        self.turn = 2
        self.players = playerlist
        self.channelid = cid
        self.bot = botvar
        self.gamefield = np.zeros((self.row_count, self.column_count))
        self.print_gamefield()
        self.gamefield_message = None
        self.aktplayer = 0

    async def insert_selected(self, row, col, playerindex):
        self.gamefield[row][col] = playerindex + 1

    async def is_location_valid(self, col):
        return self.gamefield[self.row_count - 1][col] == 0

    async def get_next_row(self,col):
        for r in range(self.row_count):
            if (self.gamefield[r][col] == 0):
                return r

    async def print_gamefield(self):
        if(self.gamefield_message == None):
            message = self.bot.get_channel(self.channelid).send(str(self.gamefield))
            await message.add_reaction('\u2776')
            await message.add_reaction('\u2777')
            await message.add_reaction('\u2778')
            await message.add_reaction('\u2779')
            await message.add_reaction('\u277A')
            await message.add_reaction('\u277B')
            await message.add_reaction('\u277C')
            self.gamefield_message = message
        else:
            self.gamefield_message.edit(content=str(self.gamefield))


    async def check_state(self,piece):
        piece += 1
        for c in range(self.column_count):
            for r in range(self.row_count):
                try:
                    if ((self.gamefield[r][c] == piece and self.gamefield[r][c + 1] == piece and self.gamefield[r][c + 2] == piece and
                         self.gamefield[r][c + 3] == piece) or
                            (self.gamefield[r][c] == piece and self.gamefield[r + 1][c] == piece and self.gamefield[r + 2][c] == piece and
                             self.gamefield[r + 3][c] == piece) or
                            (self.gamefield[r][c] == piece and self.gamefield[r + 1][c + 1] == piece and self.gamefield[r + 2][
                                c + 2] == piece and self.gamefield[r + 3][c + 3] == piece) or
                            (self.gamefield[r][c] == piece and self.gamefield[r - 1][c + 1] == piece and self.gamefield[r - 2][
                                c + 2] == piece and self.gamefield[r - 3][c + 3] == piece)):
                        return False
                except:
                    pass
        return True

    @commands.Cog.listener()
    async def on_reaction_add(self, payload):
        if payload.channel_id == self.channelid:
            if payload.user_id == self.players[self.aktplayer].id:

                emojis = {
                    "68546f5fc3b2166f42cf90b7e23c5ae9" : 0,
                    "eb29ce5fcf54bc3b23ff77039a4ecf3c" : 1,
                    "67f896405747f26f63f09e0cb048d358" : 2,
                    "09fe8a2882cac4cdb4712ab9622d3fe1" : 3,
                    "5575865e2cb3d50ea051b09d7e1d2550" : 4,
                    "f8b3e0e54d99d2b2962a2e474b2110e4" : 5,
                    "c5ef2ff553f9cecd81add57e79aaf81d" : 6
                }

                col = emojis[payload.emoji.id]
                if(col != None):
                    if (self.is_location_valid(self.gamefield, col)):
                        row = self.get_next_row(self.gamefield, col)
                        self.insert_selected(self.gamefield, row, col, self.aktplayer)
                    if self.check_state(self.gamefield, self.aktplayer) == False:
                        # TODO: SEND MESSAGE TO PLAYERS THAT A PLAYER WON AND KICK THEM OUT OF THE GAME
                        print(self.players[self.aktplayer].display_name + " won the Game!")
                        return

                await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id).remove_reaction(payload.emoji, self.bot.get_user(payload.user_id))
                self.aktplayer += 1
                self.aktplayer % self.aktplayer / 2



