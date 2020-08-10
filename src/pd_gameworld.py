import discord

client = discord.Client()

@client.event
async def on_member_join(member):
    channel = client.get_channel(741965363549569034)
    await channel.send(f"""Welcome to the Server {member.mention} !""")

client.run("NzQyMDMyMDAzMTI1MzQ2MzQ0.XzANJw.M_1EwGyle3wi9d3yc4JzFqcENcY")


