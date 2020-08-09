from discord.ext import commands
from discord.utils import get

bot = commands.Bot(command_prefix='!pd')


channel = bot.get_channel(741965363549569034)


@bot.event
async def on_member_join(member):
    await channel.send(f"""Welcome to the Server {member.mention} !""")
    role = get(member.server.roles, id="741836468674101270")
    await bot.add_roles(member, role)




bot.run("NzQyMDMyMDAzMTI1MzQ2MzQ0.XzANJw.M_1EwGyle3wi9d3yc4JzFqcENcY")


