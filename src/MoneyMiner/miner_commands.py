import discord
import asyncio
from discord.ext import commands

from GameAPI.PlayerDataApi import Utils

from GameAPI.user_extension import *

from myclient import client


class MineCommands(commands.Cog):

    def __init__(self):
        self.gamechannels = [772515089181310977, 772543056640868404, 772543093714714666, 773486403073736735, 773486430047305728]
        self.gamemessages = {}
        asyncio.create_task(self.timer())

    @commands.command(aliases=['bp','rucksack'])
    async def backpack(self, ctx: commands.Context, *args):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        if not ctx.channel.id in self.gamechannels:
            return
        backpack_fill = get_backpack_money(ctx.author)
        max_backpack_fill = get_max_backpack(ctx.author)
        backpack_level = get_backpack_level(ctx.author)

        next_level_cost = 5 * (backpack_level+1) ** 2 + 15 * (backpack_level+1)

        embed = discord.Embed(title="Rucksack ( " + ctx.author.name +" )",description="[ " + str(backpack_fill) + " / " + str(max_backpack_fill) + " ] ",color=0x00FF00)
        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_author(name="MoneyMiner",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.add_field(name="RuckSack Level:", value=str(backpack_level), inline=False)
        embed.add_field(name="Upgrade kostet:", value=str(next_level_cost), inline=False)
        if ctx.author in self.gamemessages:
            try:
                await self.gamemessages[ctx.author].delete()
            except:
                pass
            self.gamemessages[ctx.author] = await ctx.channel.send(embed=embed,delete_after=120)
        else:
            self.gamemessages[ctx.author] = await ctx.channel.send(embed=embed,delete_after=120)
        return

    @commands.command(aliases=['pa','spitzhacke'])
    async def pickaxe(self, ctx: commands.Context, *args):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        if not ctx.channel.id in self.gamechannels:
            return
        pickaxe_level = get_pickaxe_level(ctx.author)

        next_level_cost = 5 * (pickaxe_level+1) ** 2 + 15 * (pickaxe_level+1)

        embed = discord.Embed(title="Spitzhacke ( " + ctx.author.name +" )",description="Spitzhackeninformationen",color=0x00FF00)
        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_author(name="MoneyMiner",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.add_field(name="Spitzhacken Level:", value=str(pickaxe_level), inline=False)
        embed.add_field(name="Money pro Minute:", value=str(1 * (pickaxe_level/4)), inline=False)
        embed.add_field(name="Upgrade kostet:", value=str(next_level_cost), inline=False)
        if ctx.author in self.gamemessages:
            try:
                await self.gamemessages[ctx.author].delete()
            except:
                pass
            self.gamemessages[ctx.author] = await ctx.channel.send(embed=embed,delete_after=120)
        else:
            self.gamemessages[ctx.author] = await ctx.channel.send(embed=embed,delete_after=120)
        return

    @commands.command()
    async def upgrade(self, ctx: commands.Context, *args):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        if not len(args) == 1:
            return
        if not ctx.channel.id in self.gamechannels:
            return
        pickaxe_aliases = ["pickaxe", "pa", "spitzhacke"]
        backpack_aliases = ["backpack", "bp", "rucksack"]

        if args[0] in pickaxe_aliases:
            pickaxe_level = get_pickaxe_level(ctx.author)
            needed_money = 5*pickaxe_level**2 + 15*pickaxe_level
            player_balance = get_money(ctx.author)
            if has_money(ctx.author, needed_money):
                withdraw_money(ctx.author, needed_money)
                newlevel = levelup_pickaxe(ctx.author, 1)
                embed = discord.Embed(title="Upgegradet", description="Spitzhacke für "+ str(needed_money) +" auf Level " + str(newlevel) + " geupgradet!", color=0x00FF00)
                embed.set_author(name="MoneyMiner",
                                 icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await ctx.channel.send(embed=embed, delete_after=6)
            else:
                embed = discord.Embed(title="Achtung", description="Du brauchst min. " + str(needed_money) + " zum Upgraden, hast aber nur "+str(round(player_balance,2))+"!", color=0xFF0000)
                embed.set_author(name="MoneyMiner",
                                 icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await ctx.channel.send(embed=embed, delete_after=6)


        elif args[0] in backpack_aliases:
            backpack_level = get_backpack_level(ctx.author)
            needed_money = 5*backpack_level**2 + 15*backpack_level
            player_balance = get_money(ctx.author)
            if has_money(ctx.author, needed_money):
                withdraw_money(ctx.author, needed_money)
                newlevel = levelup_backpack(ctx.author, 1)
                embed = discord.Embed(title="Upgegradet", description="Rucksack für "+ str(needed_money) +" auf Level " + str(newlevel) + " geupgradet!", color=0x00FF00)
                embed.set_author(name="MoneyMiner",
                                 icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await ctx.channel.send(embed=embed, delete_after=6)
            else:
                embed = discord.Embed(title="Achtung", description="Du brauchst min. " + str(needed_money) + " zum Upgraden, hast aber nur "+str(round(player_balance,2))+"!", color=0xFF0000)
                embed.set_author(name="MoneyMiner",
                                 icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await ctx.channel.send(embed=embed, delete_after=6)

        else:
            return

    @commands.command()
    async def claim(self, ctx: commands.Context, *args):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        if not ctx.channel.id in self.gamechannels:
            print("fals channel")
            return
        backpack_money = get_backpack_money(ctx.author)
        deposit_money(ctx.author, backpack_money)
        backpack_set_money(ctx.author, 0)
        embed = discord.Embed(title="Claimed!", description=ctx.author.name + " hat " + str(backpack_money) + " aus seinem Rucksack geholt!", color=0x58ff46)
        embed.set_author(name="MoneyMiner",
                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        await ctx.channel.send(embed=embed, delete_after=6)

    async def timer(self):
        while True:
            members = client.guilds[0].members
            for member in members:
                if member.status == discord.Status.online:
                    pickaxe_level = get_pickaxe_level(member)
                    money_to_earn = 1 * (pickaxe_level/4)
                    backpack_fill = get_backpack_money(member)
                    max_backpack_fill = get_max_backpack(member)
                    if (backpack_fill + money_to_earn) > max_backpack_fill:
                        backpack_set_money(member, max_backpack_fill)
                    else:
                        backpack_set_money(member, backpack_fill + money_to_earn)
            await asyncio.sleep(60)

# Aufräumen beim Start:
@client.listen()
async def on_ready():
    client.add_cog(MineCommands())






