import discord
from discord.ext import commands


class BugReport(commands.Cog):
    def __init__(self, bot):
        self.bugreportschannelid = 743797646883553370
        self.modreportschannelid = 743798512663265290
        self.devreportschannelid = 743805821418209321
        self.bot: commands.Bot = bot


    @commands.command()
    async def bug(self, ctx: commands.Context, arg):
        message: discord.Message = ctx.message
        await message.delete()
        if not message.channel.id == self.bugreportschannelid:
            return
        embed = discord.Embed(title="You reported a Bug", description=arg, color=0x49ff35)
        embed.set_author(name="Bug:" + arg,
                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_footer(text="Thanks for your Report!")
        await self.bot.get_channel(self.bugreportschannelid).send(embed=embed, delete_after=10)
        embed = discord.Embed(title=message.author.display_name + " reported a Bug:", description=arg, color=0x49ff35)
        embed.add_field(name="**Member-Info**", value="at report Time", inline=True)
        embed.add_field(name="Display-Name:", value=message.author.display_name, inline=True)
        embed.add_field(name="User-Id:", value=str(message.author.id), inline=True)
        embed.add_field(name="User-Status:", value=str(message.author.status), inline=True)
        embed.add_field(name="On-Mobile:", value=str(message.author.is_on_mobile()), inline=True)
        embed.set_author(name="BugReport",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        message: discord.Message = await self.bot.get_channel(self.modreportschannelid).send(embed=embed)
        await message.add_reaction("✔️")
        await message.add_reaction("❌")
        await message.add_reaction("🅱️")
        await message.add_reaction("🟨")

    @commands.Cog.listener()
    async def on_reaction_add(self, payload: discord.Reaction, user):
        if user != self.bot.user:
            if payload.message.channel.id == self.modreportschannelid:
                message: discord.Message = payload.message
                if payload.emoji == "✔️":
                    embed: discord.Embed = message.embeds[0]
                    devmessage = await self.bot.get_channel(self.devreportschannelid).send(embed=embed)
                    await devmessage.add_reaction("✔️")
                    embed = discord.Embed(title="Done!", description="You accepted the bug!",color=0x49ff35)
                    embed.set_author(name="BugReport",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    await self.bot.get_channel(self.modreportschannelid).send(embed=embed, delete_after=10)
                    await message.delete()
                if payload.emoji == "❌":
                    await message.delete()
                    embed = discord.Embed(title="Done!", description="You denied the bug!", color=0x49ff35)
                    embed.set_author(name="BugReport",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    await self.bot.get_channel(self.modreportschannelid).send(embed=embed, delete_after=10)
                if payload.emoji == "🅱️":
                    embed: discord.Embed = message.embeds[0]
                    embed.add_field(name="Are you sure?", value="Do you really want to ban him for ever?")
                    confirm_message = await message.channel.send(embed=embed)
                    await confirm_message.add_reaction("✅")
                    await message.delete()
                if payload.emoji == "✅":
                    embed: discord.Embed = message.embeds[0]
                    await self.bot.get_user(embed.fields[2].name).ban()
                    await message.delete()
                    embed = discord.Embed(title="Done!", description="You banned him!", color=0x49ff35)
                    embed.add_field(name="Player-ID:", value=str(embed.fields[2].name))
                    embed.set_author(name="BugReport",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    banmessage: discord.Message = await self.bot.get_channel(self.modreportschannelid).send(embed=embed, delete_after=500)
                    await banmessage.add_reaction("🆘")
                if payload.emoji == "🟨":
                    embed: discord.Embed = message.embeds[0]
                    guild: discord.Guild = self.bot.get_guild(741823660188500008)
                    user_to_kick = guild.get_member(int(embed.fields[2].value))
                    try:
                        await user_to_kick.kick(reason="You were kicked off the server for an inappropriate report! You can join again at any time. If this is not correct, we are sorry.")
                    except:
                        embed = discord.Embed(title="Error!", description="there was an error and therefore the player was not kicked off the server (Maybe you tried to kick an Admin/Owner?)!", color=0x49ff35)
                        embed.set_author(name="BugReport",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        await self.bot.get_channel(self.modreportschannelid).send(embed=embed, delete_after=20)
                    await message.delete()
                if payload.emoji == "🆘":
                    embed: discord.Embed = message.embeds[0]
                    await self.bot.get_user(embed.fields[0].name).unban()
                    await message.delete()
                    embed = discord.Embed(title="Done!", description="You unbanned him!", color=0x49ff35)
                    embed.set_author(name="BugReport",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    await self.bot.get_channel(self.modreportschannelid).send(embed=embed,delete_after=10)
            if payload.message.channel.id == self.devreportschannelid:
                message: discord.Message = payload.message
                if payload.emoji == "✔️":
                    await message.delete()
                    embed = discord.Embed(title="Done!", description="You completed the bug!", color=0x49ff35)
                    embed.set_author(name="BugReport", icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    await self.bot.get_channel(self.devreportschannelid).send(embed=embed, delete_after=10)