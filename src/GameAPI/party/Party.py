import asyncio
from initalizing import client

class Party():

    __partys = []

    def __init__(self, owner, channelid):
        self.owner = owner
        self.members = []
        self.playing = False
        __partys.append(self)
        self.partychannel = await self.guild.create_text_channel(
            name=self.owner.name + "'s Party",
            category=self.bot.get_channel(773935446732308502))

    @client.command()
    async def invite(self, ctx: commands.Context, *args):
        if ctx.author == self.owner and len(args) == 1:
            


    # Jemand will eine Queue verlassen:
    @client.command()
    async def leave(self, ctx: commands.Context):
        if ctx.channel == self.partychannel:
            if self.owner == ctx.author:
                embed = discord.Embed(title=ctx.author.name,
                                      description=ctx.author.name + ", der Owner hat die Party verlassen. Deswegen wird die Party aufgelößt.",
                                      color=0xFF0000)
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.set_author(name="Party",
                                 icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await self.partychannel.send(embed=embed, delete_after=7)
                await asyncio.sleep(5)
                __partys.remove(self)
            else:
                self.members.remove(ctx.author)
                embed = discord.Embed(title=member.name,
                                      description="Hat die Party verlassen",
                                      color=0xFF0000)
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.set_author(name="Party",
                                 icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await self.partychannel.send(embed=embed, delete_after=7)
