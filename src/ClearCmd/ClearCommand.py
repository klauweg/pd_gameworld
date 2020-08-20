import discord
from discord.ext import commands


class ClearCommand(commands.Cog):

    @commands.command()
    async def purge(self, ctx: commands.Context, *, member: discord.Member = None):
        role = discord.utils.get(ctx.guild.roles, id=744630374855868456)
        if role in ctx.author.roles:
            await ctx.channel.purge()