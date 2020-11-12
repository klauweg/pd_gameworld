import logging
logger = logging.getLogger("user_ext")

import math
import traceback
import asyncio
import discord
import pickle
from collections import defaultdict
import time

#########################
from Gadgets.Pet import Pet

file_path = "../resources/player_data.pickle"


try:
    with open(file_path,"rb") as fp:
        data = pickle.load(fp)
        logger.info("Old setup loaded.")
except FileNotFoundError:
    data = defaultdict( dict )
    logger.info("New setup created.")

def update_data():
    with open(file_path, "wb") as fp:
        pickle.dump(data, fp)


############## BOOSTER
def set_booster(booster, multiplikator, duration):
    data["booster"][booster.lower()] = {"multiply": multiplikator, "time": duration, "created": time.time()}
    update_data()

def get_booster_multiply(boostername):
    booster =  data["booster"].get(boostername.lower(), None)
    if booster:
        if time.time() - booster["created"] > booster["time"]*60:
            data["booster"].pop(boostername.lower())
            return 1
        else:
            return booster["multiply"]
    return 1

def remove_boosters():
    data["booster"] = {}
    update_data()
################################ XP

def get_xp(member):
    return data[ str(member.id) ].setdefault("xp", 0)

def set_xp(member, xp):
    data[ str(member.id) ]["xp"] = xp
    update_data()
    
def add_xp(member, xp):
    multiplyxp = 0
    for pet in get_pets( member ):
        if pet.equipped == True:
            multiplyxp += xp*pet.xp_multiply - xp
    set_xp(member, get_xp(member) + ((xp + multiplyxp) * get_booster_multiply("xp")))
    asyncio.create_task( update_player_nick(member) )
def remove_xp(member, xp):
    set_xp( member, get_xp(member) - xp)
    asyncio.create_task( update_player_nick(member) )
    update_data()


def get_level(member):
    return int(round(math.sqrt(get_xp(member)/5 + 2.25) - 1,5))

def get_player_role(member):
    rank = "Neuling"
    roles = {0: "Neuling", 10: "Spielender", 20: "Erfahrener", 40: "Ältester"}
    member_level = get_level(member)
    for key in roles:
        if member_level >= key:
            rank = roles[key]
    return rank

async def update_player_role(member: discord.Member):
    roles = {0: 772413848598085662, 10: 772413846987603988, 20: 772414007691837440, 50: 772414093067419648}
    member_level = get_level(member)
    for key in roles:
        if member_level >= key:
            await member.add_roles(discord.utils.get(member.guild.roles, id=roles[key]) )

async def update_player_nick(member: discord.Member):
    try:
        await member.edit(nick=member.name + " [Lvl: " + str(get_level(member)) + "]")
    except discord.Forbidden:
        pass

################# STATS

def get_stats(member):
    return data[ str(member.id) ].setdefault("stats", {})
    
def add_to_stats(member, game_name, wins=0, played=0, even=0):
    stats = get_stats(member).setdefault(game_name, [0,0,0])
    stats[0] += wins
    stats[1] += played
    stats[2] += even
    update_data()

def clear_stats():
    for memberid in data:
        data[memberid]["stats"] = {}
    update_data()

############################### Economy

def get_money(member):
    return data[ str(member.id) ].setdefault("money", 0)

def set_money(member, amount):
    data[ str(member.id) ]["money"] = amount
    update_data()
    
def deposit_money(member, amount):
    multiplymoney = 0
    for pet in get_pets( member ):
        if pet.equipped == True:
            multiplymoney += amount*pet.xp_multiply - amount
    set_money( member, get_money( member ) + ((amount + multiplymoney) * get_booster_multiply("money")) )
    asyncio.create_task( update_player_nick(member) )

def withdraw_money(member, amount):
    if get_money(member) >= amount:
        set_money(member, get_money(member) - amount)
        update_data()
    else:
        return False

def has_money(member, amount):
    return get_money(member) >= amount

############################ PETS

def get_pets(member):
    return data[ str(member.id) ].setdefault("pets", [])    

def get_cost(member, cost):
    extra_money = 0
    #Haustier multiplikator einberechnen
    for pet in get_pets(member):
        extra_money += cost * pet.money_multiply - cost
    #Spitzhackenlevel von MoneyMiner einberechnen
    extra_money += get_pickaxe_level(member) * 8
    #4/5 dazuberechnen damit man durch haustiere trotzdem noch vorteile hat
    cost += extra_money * (4/5)
    #Runden
    return int(round(cost))

def add_pet(member, name, xp_m, money_m, rarity):
    get_pets(member).append( Pet(name, xp_m, money_m, rarity) )
    update_data()

def clear_all_pets():
    for memberid in data:
        data[memberid]["pets"] = []
    update_data()

def search_pet( member, name ):
    for pet in get_pets(member):
        if pet.name.upper() == name.upper():
            return pet
    
def remove_pet(member, name):
    pet = search_pet( member, name )
    if pet:
        get_pets(member).remove( pet )
    
def equip_pet(member, name):
    if not search_pet(member, name):
        return "Du hast dieses Pet nicht!"

    equipped_pets_amount = 0
    for pet in get_pets(member):
        if pet.equipped == True:
            equipped_pets_amount += 1
    if equipped_pets_amount == 5:
        return "Du hast die Maximale Anzahl an Pets erreicht! Unequippe erst ein Pet!"
    for pet in get_pets(member):
        if pet.name.upper() == name.upper() and pet.equipped == False:
            pet.equipped = True
            update_data()
            return "Du hast " + name + " Equipped"

def unequip_pet(member, name):
    if not search_pet(member, name):
        return "Du hast dieses Pet nicht!"
    if is_pet_equipped(member, name):
        for pet in get_pets(member):
            if pet.name.upper() == name.upper() and pet.equipped == True:
                pet.equipped = False
                update_data()
                return "Du hast " + name + " Unequipped"
    else:
        return "Du hast dieses Pet nicht equipped!"

def is_pet_equipped(member, name):
    for pet in get_pets(member):
        if pet.name.upper() == name.upper() and pet.equipped == True:
            return True
    return False

def get_pet_amount(member):
    return len(get_pets(member))



###################### MoneyMiner

def get_moneyminer(member):
    return data[str(member.id)].setdefault("moneyminer", {"pa_level": 0, "bp_level": 1, "bp_fill": 0})

def levelup_backpack(member, level):
    get_moneyminer(member)["bp_level"] += level
    update_data()
    return get_moneyminer(member)["bp_level"]

def levelup_pickaxe(member, level):
    get_moneyminer(member)["pa_level"] += level
    update_data()
    return get_moneyminer(member)["pa_level"]

def backpack_set_money(member, money):
    get_moneyminer(member)["bp_fill"] = money
    update_data()

def get_backpack_money(member):
    return get_moneyminer(member)["bp_fill"]

def get_max_backpack(member):
    return 30 * get_moneyminer(member)["bp_level"]

def get_backpack_level(member):
    return get_moneyminer(member)["bp_level"]

def get_pickaxe_level(member):
    return get_moneyminer(member)["pa_level"]






