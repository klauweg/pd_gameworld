import discord
from discord.ext import commands

from GameAPI.user_extension import add_xp, get_xp, get_level, get_money
from GameAPI.PlayerDataApi import Utils


class StatsCommand(commands.Cog):
    @commands.command()
    async def stats(self, ctx: commands.Context, *args):
        await ctx.message.delete()

        if ctx.channel.id == 741835965164814458:
            member = None
            if len(args) == 0:
                member = ctx.author
            else:
                member = ctx.guild.get_member_named(args[0])
            if member is not None:
                statsdata = Utils.get_stats(member)
                xp = round(get_xp(member))
                level = get_level(member)
                money = round(get_money(member))
                embed = discord.Embed(title="Statistiken von " + member.name + "!", description="Hier sind die Stats:",color=0x49ff35)
                embed.set_author(name="STATS",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.add_field(name="Xp: " + str(xp) + ", Level: " + str(level) + ", Money: " + str(money), value="---------------------", inline=False)
                for game in statsdata:
                    embed.add_field(name=game, value="Played:" + str(statsdata[game][1]) + ", Wins:" + str(statsdata[game][0]), inline=False)
                await ctx.channel.send(embed=embed, delete_after=20)
                return