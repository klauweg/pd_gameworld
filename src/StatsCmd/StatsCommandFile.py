import discord
from discord.ext import commands

from GameAPI.PlayerDataApi import Utils


class StatsCommand(commands.Cog):
    @commands.command()
    async def stats(self, ctx: commands.Context,*, arg):
        await ctx.message.delete()
        if ctx.channel.id == 741835965164814458:
            member = ctx.guild.get_member_named(arg)
            if member is not None:
                userdata = await Utils.get_player_data(member)

                embed = discord.Embed(title="Stats of " + member.name + "!", description="Here are the Stats:",color=0x49ff35)
                embed.set_author(name="STATS",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.add_field(name="Xp: " + str(userdata["xp"]) + ", Level: " + str(await Utils.get_level(member.id)), value="---------------------", inline=False)
                for game in userdata["stats"]:
                    embed.add_field(name=game, value="Played:" + str(userdata["stats"][game][0]) + ", Wins:" + str(userdata["stats"][game][1]), inline=False)
                await ctx.channel.send(embed=embed, delete_after=20)
                return