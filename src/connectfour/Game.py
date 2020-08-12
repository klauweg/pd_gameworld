import discord
import numpy as np
from discord.ext import commands


class ConnectFourGame(commands.Cog):

    def __init__(self, playerlistids, cid, botvar, message, gamefield):
        self.row_count = 6
        self.column_count = 7
        self.turn = 2
        self.playerids = playerlistids
        self.channelid = cid
        self.bot = botvar
        self.gamefield = gamefield
        self.aktplayer = 0
        self.gamefield_message: discord.Message = message

    async def insert_selected(self, row, col, playerindex):
        self.gamefield[row][col] = playerindex + 1

    async def is_location_valid(self, col):
        return self.gamefield[self.row_count - 1][col] == 0

    async def get_next_row(self,col):
        for r in range(self.row_count):
            if self.gamefield[r][col] == 0:
                return r

    async def print_gamefield(self):
        embed = discord.Embed(title="", description=str(np.flip(self.gamefield, 0)), color=discord.Color.green())
        embed.set_author(name="ConnectFour",
                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        await self.gamefield_message.edit(embed = embed)

    async def check_state(self, piece):
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
    async def on_reaction_add(self, payload: discord.Reaction, user):
        if payload.message.id == self.gamefield_message.id:
            if user.id == self.playerids[self.aktplayer]:

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
                if(col != None):
                    if await self.is_location_valid(col):
                        row = await self.get_next_row(col)
                        await self.insert_selected(row, col, self.aktplayer)
                        await self.print_gamefield()
                    if not await self.check_state(self.aktplayer):
                        # TODO: SEND MESSAGE TO PLAYERS THAT A PLAYER WON AND KICK THEM OUT OF THE GAME
                        # TODO: DELETE GAME MESSAGE TO PREVENT SO MANY MESSAGES
                        print(self.bot.get_user(self.playerids[self.aktplayer]).display_name + " won the Game!")
                        return

                await self.gamefield_message.remove_reaction(payload.emoji, self.bot.get_user(user.id))
                self.aktplayer += 1
                self.aktplayer % self.aktplayer / 2



