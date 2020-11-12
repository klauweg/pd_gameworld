import asyncio
from threading import Timer

import discord
from discord.ext import commands


class Book(commands.Cog):
    def __init__(self, title, pages, bot, channelid):
        self.title = title
        self.page_content = pages
        self.akt_page = 0
        self.book_message: discord.Message = None
        self.bot: commands.Bot = bot
        self.channelid = channelid
        self.bot.add_cog(self)
        self.task: asyncio.Task = asyncio.create_task(
            self.delete_book(120))

    async def delete_book(self, sleeptime):
        await asyncio.sleep(sleeptime)
        await self.book_message.delete()
        self.bot.remove_cog(self)

    async def send_message(self):
        if self.book_message is not None:
            embed = discord.Embed(title="Beschreibung:", description=self.page_content[self.akt_page],
                                  color=0x49ff35)
            embed.set_author(name=self.title,
                             icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.add_field(name="--------",
                            value="[" + str(self.akt_page + 1) + "/" + str(len(self.page_content)) + "]",
                            inline=True)
            try:
                await self.book_message.edit(embed=embed)
            except:
                pass
        else:
            embed = discord.Embed(title="Beschreibung:", description=self.page_content[self.akt_page], color=0x49ff35)
            embed.set_author(name=self.title,icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.add_field(name="--------",
                            value="[" + str(self.akt_page + 1) +"/" + str(len(self.page_content)) +"]",
                            inline=True)
            message: discord.Message = await self.bot.get_channel(self.channelid).send(embed=embed)
            await message.add_reaction("◀️")
            await message.add_reaction("▶️")
            self.book_message = message


    @commands.Cog.listener()
    async def on_reaction_add(self, payload: discord.Reaction, user):
        if self.book_message is None:
            return
        if user == self.bot.user:
            return
        if payload.message.id == self.book_message.id:
            await payload.message.remove_reaction(payload.emoji, user)
            self.task.cancel()
            self.task: asyncio.Task = asyncio.create_task(
                self.delete_book(120))
            if payload.emoji == "◀️":
                self.akt_page -= 1
                if self.akt_page == -1:
                    self.akt_page = len(self.page_content)-1
                await self.send_message()
            elif payload.emoji == "▶️":
                self.akt_page += 1
                if self.akt_page == len(self.page_content):
                    self.akt_page = 0
                await self.send_message()