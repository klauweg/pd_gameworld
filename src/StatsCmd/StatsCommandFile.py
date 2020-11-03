import discord
from discord.ext import commands

from GameAPI.user_extension import *

class StatsCommand(commands.Cog):
    @commands.command()
    async def stats(self, ctx: commands.Context, *args):
        await ctx.message.delete()

        if ctx.channel.id == 741835965164814458:
            member = None
            if len(args) == 0:
                member = ctx.author
            else:
                member = ctx.guild.get_member_named(' '.join(args))
            if member is not None:
                statsdata = get_stats(member)
                xp = round(get_xp(member))
                level = get_level(member)
                pet_amount = get_pet_amount(member)
                money = get_money(member)
                backpack_level = get_backpack_level(member)
                pickaxe_level = get_pickaxe_level(member)
                player_rank = get_player_role(member)
                embed = discord.Embed(title="Statistiken von " + member.name + "!", description="Hier sind die Stats:",color=0x00FF00)
                embed.set_author(name="STATS",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.add_field(name="Xp:", value=str(xp), inline=False)
                embed.add_field(name="Level:", value=str(level), inline=False)
                embed.add_field(name="Money:", value=str(round(money, 2)), inline=False)
                embed.add_field(name="Rang:", value=player_rank, inline=False)
                embed.add_field(name="Pets:", value=str(pet_amount), inline=False)
                embed.add_field(name="MoneyMiner:", value="Rucksack Lvl: " + str(backpack_level) + "\nSpitzhacken Lvl: " + str(pickaxe_level), inline=False)
                for game in statsdata:
                    embed.add_field(name=game, value="Played:" + str(statsdata[game][1]) + ", Wins:" + str(statsdata[game][0]), inline=False)
                await ctx.channel.send(embed=embed, delete_after=20)
                return