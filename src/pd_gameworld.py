from discord.ext import commands

bot = commands.Bot(command_prefix="!pd")


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(741965363549569034)
    await channel.send(f"""Welcome to the Server {member.mention} !""")
    role = member.guild.get_role(741836468674101270)
    member.add_roles(role)

bot.run("NzQyMDMyMDAzMTI1MzQ2MzQ0.XzANJw.M_1EwGyle3wi9d3yc4JzFqcENcY")


