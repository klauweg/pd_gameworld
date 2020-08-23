import math

import discord

from GameAPI.PlayerDataApi.FileManager import getuser, getuserlist, setuser


########################### XP

async def add_xp(member, xp):
    userdata = getuser(member.id)
    oldxp = userdata.get("xp", 0)
    userdata["xp"] = oldxp + xp
    setuser(member.id, userdata)
    await update_player_nick(member)

def get_xp(member):
    userdata = getuser(member.id)
    xp = userdata.get("xp", 0)
    return xp

def get_level(member):
    member_xp = getuser(member.id).get( "xp", 0 )
    member_level = math.ceil(math.sqrt(member_xp/5))
    return member_level


async def update_player_nick(member: discord.Member):
    #Owner können nicht genickt werden: Mit try und except wird Error umgangen
    try:
        await member.edit(nick=member.name + " [Lvl: " + str(await get_level(member.id)) + "]")
    except:
        pass


############################ Stats

def add_to_stats(member, game_name, wins=0, played=0):
    userdata = getuser(member.id)
    stats = userdata.getI("stats", {})
    stats[game_name] = [x + y for x, y in zip(stats.get(game_name, [0, 0]), [wins, played])]
    userdata["stats"] = stats
    setuser(member.id, userdata)


def get_stats(member):
    userdata = getuser(member.id)
    return userdata.get("stats", {})


def get_all_stats():
    return [ getuser(x)["stats"] for x in getuserlist() ]


############################### Economy

def deposit_money(member, amount):
    userdata = getuser(member.id)
    oldmoney = userdata.get("money", 0)
    userdata["money"] = oldmoney + amount
    setuser(member.id, userdata)
    return


def withdraw_money(member, amount):
    userdata = getuser(member.id)
    oldmoney = userdata.get("money", 0)
    if oldmoney >= amount:
        userdata["money"] = oldmoney - amount
        setuser(member.id, userdata)
        return True
    else:
        return False


def set_money(member, amount):
    userdata = getuser(member.id)
    userdata["money"] = amount
    setuser(member.id, userdata)
    return


def get_money(member):
    return getuser(member.id).get("money", 0)


def has_money(member, amount):
    money = getuser(member.id).get("money", 0)
    if money >= amount:
        return True
    else:
        return False
