import math

import discord

from GameAPI.PlayerDataApi.FileManager import JsonData


async def add_xp(member, xp):
    json = JsonData()
    userdata = json.getuser(member.id)
    userdata["xp"] += xp
    json.setuser(member.id, userdata)
    await update_player_nick(member)


async def add_to_stats(member, game_name, wins=0, played=0):
    json = JsonData()
    userdata = json.getuser(member.id)
    userdata["stats"][game_name] = [x + y for x, y in zip(userdata["stats"].get(game_name, [0, 0]), [wins, played])]
    json.setuser(member.id, userdata)

async def get_player_data(member):
    json = JsonData()
    userdata = json.getuser(member.id)
    return userdata

async def get_level(memberid):
    json = JsonData()
    member_xp = json.getuser(memberid)["xp"]
    member_level = math.ceil(math.sqrt(member_xp/5))
    return member_level

async def update_player_nick(member: discord.Member):
    #Owner können nicht genickt werden: Mit try und except wird Error umgangen
    try:
        await member.edit(nick=member.name + " [Lvl: " + str(await get_level(member.id)) + "]")
    except:
        pass