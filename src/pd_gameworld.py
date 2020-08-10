from discord.ext import commands
from tictactoe.GameLogic import GameLogic
import discord
bot = commands.Bot(command_prefix="!pd")


@bot.event
async def on_member_join(member: discord.Member):
    channel = bot.get_channel(741965363549569034)
    role = member.guild.get_role(741836468674101270)
    await member.add_roles(role)
    await channel.send(f"""Welcome to the Server {member.mention} !""")

bot.add_cog(GameLogic(bot))
bot.run("NzQyMDMyMDAzMTI1MzQ2MzQ0.XzANJw.M_1EwGyle3wi9d3yc4JzFqcENcY")
