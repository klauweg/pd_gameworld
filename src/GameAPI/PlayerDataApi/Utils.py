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
    userdata["stats"][game_name] = [x + y for x, y in zip(userdata["stats"].get(game_name, [0, 0]), [wins, played])]
    setuser(member.id, userdata)

def get_stats(member):
    userdata = getuser(member.id)
    return userdata.get("stats", {})

def get_all_stats():
    return [ getuser(x)["stats"] for x in getuserlist() ]
