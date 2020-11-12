import logging

from party import Party

logger = logging.getLogger("user_cmd")

import random

from discord.ext import commands
from myclient import client

from Gadgets.user_extension import *

@client.command()
async def pets(ctx: commands.Context, *args):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass

    if ctx.channel.id == 772214299997110292:
        if len(args) == 0:
            member = ctx.author
        else:
            member = ctx.guild.get_member_named(args[0])

        if not member == None:

            pets = get_pets(member)

            if (len(pets) == 0):
                embed = discord.Embed(title="Hinweis!",
                                      description="Der Spieler " + member.name +"  hat noch keine Pets",
                                      color=0x999999)
                embed.set_author(name="Haustiere",
                                 icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await ctx.author.send(embed=embed, delete_after=60)

                return

            embed = discord.Embed(title=member.name + "'s Haustiere",
                                  description="Hier sind alle Haustiere von " + member.name,
                                  color=0x999999)
            embed.set_author(name="Haustiere",
                             icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            await ctx.author.send(embed=embed, delete_after=60)

            rarity_color = {"Gewöhnlich": 0x999999, "Selten": 0x00FF00, "Episch": 0x8800FF, "Legendär": 0xE2B007}

            for pet in pets:
                isequipped = "✅" if pet.equipped else "❌"
                embed = discord.Embed(title="Haustier: " + pet.display_name + " :",
                                      description="Daten:",
                                      color=rarity_color.get(pet.rarity, 0x999999))
                embed.set_author(name="Haustier",
                                 icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.add_field(name="Rarität",
                                value=pet.rarity,
                                inline=False)
                embed.add_field(name="Xp Multiplikator:",
                                value=str(pet.xp_multiply),
                                inline=True)
                embed.add_field(name="Money Multiplikator:",
                                value=str(pet.money_multiply),
                                inline=True)
                embed.add_field(name="Equipped",
                                value=isequipped,
                                inline=False)

                await ctx.author.send(embed=embed, delete_after=60)
                await asyncio.sleep(0.21)

@client.command()
async def lock(ctx: commands.Context, *args):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass
    role = discord.utils.get(ctx.guild.roles, id=741837884583313440)
    if role in ctx.author.roles:
        embed = discord.Embed(title="Achtung!",
                              description="Bis der Bot wieder gestartet ist, könnt ihr nur in manchen Channels schreiben!",
                              color=0x00FF00)
        embed.set_author(name="Help",
                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        await client.get_channel(741835032020385802).send(embed=embed)
        non_block_channels = [742069974889267281, 743798512663265290, 743805821418209321, 746680429045874810, 741836337006772306, 741963559705247846, 741965363549569034]
        for channel in ctx.guild.text_channels:
            if not channel.id in non_block_channels:
                role = ctx.guild.get_role(741823660188500008)
                await channel.set_permissions(role, send_messages=False)
                await asyncio.sleep(0.21)
        await client.get_channel(741835032020385802).set_permissions(role, send_messages=True)


@client.command()
async def unlock(ctx: commands.Context, *args):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass
    role = discord.utils.get(ctx.guild.roles, id=741837884583313440)
    if role in ctx.author.roles:
        non_block_channels = [742069974889267281, 743798512663265290, 743805821418209321, 746680429045874810, 741836337006772306, 741963559705247846, 741965363549569034]
        for channel in ctx.guild.text_channels:
            if not channel.id in non_block_channels:
                role = ctx.guild.get_role(741823660188500008)
                await channel.set_permissions(role, send_messages=True)
                await asyncio.sleep(0.21)
        embed = discord.Embed(title="Achtung!",
                              description="Der Bot ist wieder an, ihr könnt wieder schreiben!",
                              color=0x00FF00)
        embed.set_author(name="Help",
                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        await client.get_channel(741835032020385802).send(embed=embed)

@client.command()
async def give_pet(ctx: commands.Context, *args):
    arguments = list(args)
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass
    role = discord.utils.get(ctx.guild.roles, id=741838175919538176)
    if role in ctx.author.roles:
        if len(arguments) >= 5:
            rarity = arguments.pop(-1)
            money_m = arguments.pop(-1)
            xp_m = arguments.pop(-1)
            name = arguments.pop(-1)
            member = ctx.guild.get_member_named(' '.join(arguments))
            if member:
                try:
                    add_pet(member, name, float(xp_m), float(money_m), rarity)
                except ValueError:
                    embed = discord.Embed(title="Du musst eine Zahl angeben!",
                                          description="!give_pet [spieler] [petname] [xp_multiply] [money_multiply] [rarity]",
                                          color=0xFF0000)
                    embed.set_author(name="Money",
                                     icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    await ctx.channel.send(embed=embed, delete_after=7)
                    return
            else:
                    embed = discord.Embed(title="Spieler " + ' '.join(arguments) + "nicht gefunden",
                                          description="Bitte versuche es erneut!",
                                          color=0xFF0000)
                    embed.set_author(name="Money",
                                     icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    await ctx.channel.send(embed=embed, delete_after=7)
                    return
        else:
            embed = discord.Embed(title="Falsche Benutzung!",
                                  description="!give_pet [spieler] [petname] [xp_multiply] [money_multiply] [rarity]",
                                  color=0xFF0000)
            embed.set_author(name="Money",
                             icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            await ctx.channel.send(embed=embed, delete_after=7)
            return



@client.command()
async def update_nick(ctx: commands.Context, *, member: discord.Member = None):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass
    role = discord.utils.get(ctx.guild.roles, id=741838175919538176)
    if role in ctx.author.roles:
        members = ctx.guild.members
        for member in members:
            await update_player_nick(member)

@client.command()
async def update_roles(ctx: commands.Context, *, member: discord.Member = None):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass
    role = discord.utils.get(ctx.guild.roles, id=741838175919538176)
    if role in ctx.author.roles:
        members = ctx.guild.members
        for member in members:
            await update_player_role(member)

@client.command()
async def clear_booster(ctx: commands.Context, *, member: discord.Member = None):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass
    role = discord.utils.get(ctx.guild.roles, id=741838175919538176)
    if role in ctx.author.roles:
        remove_boosters()

@client.command()
async def booster(ctx: commands.Context, *args):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass

    if ctx.channel.id == 773211644167192637:

        cost = get_cost(ctx.author, 100)
        account_balance = get_money(ctx.author)

        if args[0].upper() == "MONEY" or args[0].upper() == "XP":
            if not has_money(ctx.author, cost):
                embed = discord.Embed(title="Du hast nicht genug Money!",
                                      description="Du brauchst mindestens "+ str(cost) +", aber du hast leider nur "+ str(round(account_balance,2))+" !",
                                      color=0xFF0000)
                embed.set_author(name="Booster",
                                 icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await ctx.channel.send(embed=embed, delete_after=7)
                return

            withdraw_money(ctx.author, cost)

            set_booster(args[0].lower(), 1.25, 120)

            embed = discord.Embed(title="📢BOOOSSSTTTERRR!",
                                  description=ctx.author.name + " hat "+args[0].lower()+" für 2h geboostet! Jeder Spieler bekommt jetzt 1.25x mehr " + args[0].lower() + "!",
                                  color=0x00FF00)
            embed.set_author(name="Booster",
                             icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            await ctx.channel.send(embed=embed)
        else:

            embed = discord.Embed(title="Erlaubte Booster:",
                                  description="money, xp",
                                  color=0xFF0000)
            embed.set_author(name="Booster",
                             icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            await ctx.channel.send(embed=embed, delete_after=7)




@client.command()
async def delpet(ctx: commands.Context, *args):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass

    if ctx.channel.id == 772214299997110292:
        if not len(args) == 1:
            embed = discord.Embed(title="Falsche Benutzung!",
                                  description="!delpet [name] !",
                                  color=0xFF0000)
            embed.set_author(name="Haustier",
                             icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            await ctx.channel.send(embed=embed, delete_after=7)
            return
        remove_pet(ctx.author, args[0].upper())


@client.command()
async def pet(ctx, *, member: discord.Member = None):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass

    if ctx.channel.id == 772214299997110292:

        cost = get_cost(ctx.author, 300)
        account_balance = get_money(ctx.author)

        if not has_money(ctx.author, cost):
            embed = discord.Embed(title="Du hast nicht genug Money!",
                                  description="Du brauchst mindestens "+ str(cost) +", aber du hast leider nur "+ str(round(account_balance,2))+" !",
                                  color=0xFF0000)
            embed.set_author(name="Haustier",
                             icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            await ctx.channel.send(embed=embed, delete_after=7)
            return

        if get_pet_amount(ctx.author) >= 20:
            embed = discord.Embed(title="Du hast bereits deine Maximale Anzahl an Haustieren erreicht!",
                                  description="Du kannst haustiere wegwerfen mit !delpet [name] !",
                                  color=0xFF0000)
            embed.set_author(name="Haustier",
                             icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            await ctx.channel.send(embed=embed, delete_after=7)
            return

        withdraw_money(ctx.author, cost)

        pet_names = ["Unicorn","Lion","Shark","Icebear","Parrot","Horse","Schildkröte","Affe"]

        pet_data = {"Unicorn": {"xpm": 1.8, "mym": 1.8, "rarity": "Legendär"},
                    "Lion": {"xpm": 1.8, "mym": 1.7, "rarity": "Legendär"},
                    "Shark": {"xpm": 1.6, "mym": 1.6, "rarity": "Episch"},
                    "Icebear": {"xpm": 1.6, "mym": 1.5, "rarity": "Episch"},
                    "Parrot": {"xpm": 1.4, "mym": 1.4, "rarity": "Selten"},
                    "Horse": {"xpm": 1.3, "mym": 1.4, "rarity": "Selten"},
                    "Schildkröte": {"xpm": 1.1, "mym": 1.1, "rarity": "Gewöhnlich"},
                    "Affe": {"xpm": 1.1, "mym": 1.05, "rarity": "Gewöhnlich"}}

        rand_list = random.choices(pet_names, weights = [1,1,3,5,7,10,40,60], k = 150)

        random.shuffle(rand_list)

        winning = rand_list[0]

        winning_data = pet_data[winning]

        add_pet(ctx.author, winning, winning_data["xpm"], winning_data["mym"], winning_data["rarity"])

        rarity_color = {"Gewöhnlich": 0x999999, "Selten": 0x00FF00, "Episch": 0x8800FF, "Legendär": 0xE2B007}

        embed = discord.Embed(title="Du hast " + winning + " gewonnen!",
                              description="Daten:",
                              color=rarity_color.get(winning_data["rarity"], 0x999999))
        embed.set_author(name="Haustier",
                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.add_field(name="Rarität",
                        value=winning_data["rarity"],
                        inline=False)
        embed.add_field(name="Xp Multiplikator:",
                        value=str(winning_data["xpm"]),
                        inline=False)
        embed.add_field(name="Money Multiplikator:",
                        value=str(winning_data["mym"]),
                        inline=False)
        await ctx.channel.send(embed=embed, delete_after=30)

# Der Chef darf Channels purgen:
@client.command()
async def equip(ctx: commands.Context, *args):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass


    if ctx.channel.id == 772214299997110292:
        if not len(args) == 1:
            embed = discord.Embed(title="Falsche Benutzung!",
                                  description="!equip [name] !",
                                  color=0xFF8800)
            embed.set_author(name="Haustier",
                             icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            await ctx.channel.send(embed=embed, delete_after=7)
            return

        embed = discord.Embed(title="Antwort: ( " + ctx.author.name + " )",
                              description=equip_pet(ctx.author, args[0]),
                              color=0xFF8800)
        embed.set_author(name="Haustier",
                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        await ctx.channel.send(embed=embed, delete_after=7)

# Der Chef darf Channels purgen:
@client.command()
async def unequip(ctx: commands.Context, *args):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass

    if ctx.channel.id == 772214299997110292:
        if not len(args) == 1:
            embed = discord.Embed(title="Falsche Benutzung!",
                                  description="!uneqip[name] !",
                                  color=0xFF8800)
            embed.set_author(name="Haustier",
                             icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            await ctx.channel.send(embed=embed, delete_after=7)
            return

        embed = discord.Embed(title="Antwort: ( " + ctx.author.name + " )",
                              description=unequip_pet(ctx.author, args[0]),
                              color=0xFF8800)
        embed.set_author(name="Haustier",
                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        await ctx.channel.send(embed=embed, delete_after=7)


# Der Chef darf Channels purgen:
@client.command()
async def clear_pets(ctx: commands.Context, *, member: discord.Member = None):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass
    role = discord.utils.get(ctx.guild.roles, id=744630374855868456)
    if role in ctx.author.roles:
        clear_all_pets()

# Der Chef darf Channels purgen:
@client.command()
async def clear_stats(ctx: commands.Context, *, member: discord.Member = None):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass
    role = discord.utils.get(ctx.guild.roles, id=744630374855868456)
    if role in ctx.author.roles:
        clear_stats()

@client.command()
async def money(ctx: commands.Context, *args):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass
    role = discord.utils.get(ctx.guild.roles, id=744630374855868456)
    if role in ctx.author.roles:
        if len(args) == 3:
            member = ctx.guild.get_member_named(args[1])
            if not member == None:
                if(args[0] == "add"):
                    try:
                        deposit_money(member, int(args[2]))
                    except ValueError:
                        embed = discord.Embed(title="Du musst eine Zahl angeben!",
                                              description="!money add [name] [zahl]",
                                              color=0xFF0000)
                        embed.set_author(name="Money",
                                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        await ctx.channel.send(embed=embed, delete_after=7)
                        return
                if(args[0] == "remove"):
                    try:
                        withdraw_money(member, int(args[2]))
                    except ValueError:
                        embed = discord.Embed(title="Du musst eine Zahl angeben!",
                                              description="!money withdraw [name] [zahl]",
                                              color=0xFF0000)
                        embed.set_author(name="Money",
                                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        await ctx.channel.send(embed=embed, delete_after=7)
                        return
                if(args[0] == "set"):
                    try:
                        set_money(member, int(args[2]))
                    except ValueError:
                        embed = discord.Embed(title="Du musst eine Zahl angeben!",
                                              description="!money set [name] [zahl]",
                                              color=0xFF0000)
                        embed.set_author(name="Money",
                                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        await ctx.channel.send(embed=embed, delete_after=7)
                        return
            else:
                embed = discord.Embed(title="Spieler nicht gefunden!",
                                      description="!money [command] [name] [zahl]",
                                      color=0xFF0000)
                embed.set_author(name="Money",
                                 icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await ctx.channel.send(embed=embed, delete_after=7)
                return


@client.command()
async def xp(ctx: commands.Context, *args):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass
    role = discord.utils.get(ctx.guild.roles, id=744630374855868456)
    if role in ctx.author.roles:
        if len(args) == 3:
            member = ctx.guild.get_member_named(args[1])
            if not member == None:
                if(args[0] == "add"):
                    try:
                        add_xp(member, int(args[2]))
                    except ValueError:
                        embed = discord.Embed(title="Du musst eine Zahl angeben!",
                                              description="!xp add [name] [zahl]",
                                              color=0xFF0000)
                        embed.set_author(name="Xp",
                                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        await ctx.channel.send(embed=embed, delete_after=7)
                        return
                if(args[0] == "set"):
                    try:
                        add_xp(member, int(args[2]))
                    except ValueError:
                        embed = discord.Embed(title="Du musst eine Zahl angeben!",
                                              description="!xp set [name] [zahl]",
                                              color=0xFF0000)
                        embed.set_author(name="Xp",
                                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        await ctx.channel.send(embed=embed, delete_after=7)
                        return
                if(args[0] == "remove"):
                    if not get_xp(ctx.author) >= float(args[2]):
                        embed = discord.Embed(title="Das ergebnis würde ins Minus gehen!",
                                              description="Bitte wähle eine kleinere Zahl",
                                              color=0xFF0000)
                        embed.set_author(name="Xp",
                                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        await ctx.channel.send(embed=embed, delete_after=7)
                        return
                    try:
                        remove_xp(member, float(args[2]))
                    except ValueError:
                        embed = discord.Embed(title="Du musst eine Zahl angeben!",
                                              description="!xp remove [name] [zahl]",
                                              color=0xFF0000)
                        embed.set_author(name="Xp",
                                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        await ctx.channel.send(embed=embed, delete_after=7)
                        return
            else:
                embed = discord.Embed(title="Spieler nicht gefunden!",
                                      description="!xp [command] [name] [zahl]",
                                      color=0xFF0000)
                embed.set_author(name="Money",
                                 icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await ctx.channel.send(embed=embed, delete_after=7)
                return

@client.command()
async def stats(ctx: commands.Context, *args):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass

    if ctx.channel.id == 741835965164814458:
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
            embed = discord.Embed(title="Statistiken von " + member.name + "!", description="Hier sind die Stats:",
                                  color=0x00FF00)
            embed.set_author(name="STATS",
                             icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.add_field(name="Xp:", value=str(xp), inline=False)
            embed.add_field(name="Level:", value=str(level), inline=False)
            embed.add_field(name="Money:", value=str(round(money, 2)), inline=False)
            embed.add_field(name="Rang:", value=player_rank, inline=False)
            embed.add_field(name="Pets:", value=str(pet_amount), inline=False)
            embed.add_field(name="MoneyMiner:",
                            value="Rucksack Lvl: " + str(backpack_level) + "\nSpitzhacken Lvl: " + str(
                                pickaxe_level), inline=False)
            for game in statsdata:
                embed.add_field(name=game,
                                value="Played:" + str(statsdata[game][1]) + ", Wins:" + str(statsdata[game][0]),
                                inline=False)
            await ctx.channel.send(embed=embed, delete_after=20)
            return





