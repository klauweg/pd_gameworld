import math
import traceback

import asyncio

import discord

import pickle

#########################
from GameAPI.Pet import Pet

file_path = "../resources/player_data.pickle"

try:
    with open(file_path,"rb") as fp:
        data = pickle.load(fp)
except FileNotFoundError:
    data = {}


def update_data():
    with open(file_path, "wb") as fp:
        pickle.dump(data, fp)


def get_account( member ):
    id = str( member.id )
    if id not in data:
        data[id]={}
    return data[id]

def get_xp( member ):
    account = get_account( member )
    if "xp" not in account:
        account["xp"] = 0
    return account["xp"]

def set_xp( member, xp ):
    get_account( member )["xp"] = xp
    asyncio.create_task( update_player_nick( member ))

def get_pets( member ):
    account = get_account( member )
    if "pets" not in account:
        account["pets"] = []
    return account["pets"]

def get_stats( member ):
    account = get_account( member )
    if "stats" not in account:
        account["stats"] = {}
    return account["stats"]

################################

def add_xp(member, xp):
    multiplyxp = 0
    for pet in get_pets( member ):
        if pet.equipped == True:
            multiplyxp += xp*pet.xp_multiply - xp
    set_xp( member, get_xp( member ) + (xp + multiplyxp) )
    asyncio.create_task( update_player_nick(member) )
    update_data()


def get_level(member):
    return int(round(math.sqrt(get_xp(member)/5 + 2.25) - 1,5))

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

def add_to_stats(member, game_name, wins=0, played=0):
    stats = get_stats( member )
    if not game_name in stats:
        stats[ game_name ] = [0,0]
    stats[ game_name ][0] += wins
    stats[ game_name ][1] += played
    update_data()

############################### Economy

def get_money(member):
    account = get_account( member )
    if "money" not in account:
        account["money"] = 0
    return account["money"]

def deposit_money(member, amount):
    multiplymoney = 0
    for pet in get_pets( member ):
        if pet.equipped == True:
            multiplymoney += amount*pet.xp_multiply - amount
    set_money( member, get_money( member ) + (amount + multiplymoney) )
    asyncio.create_task( update_player_nick(member) )
    update_data()


def withdraw_money(member, amount):
    if get_money(member) >= amount:
        set_money(member, get_money(member) - amount)
        update_data()
    else:
        return False


def set_money(member, amount):
    get_account( member )["money"] = amount

def has_money(member, amount):
    if get_money(member) >= amount:
        return True
    else:
        return False

############################ PETS

def add_pet(member, name, xp_m, money_m, rarity):
    get_pets(member).append(Pet(name.upper(), xp_m, money_m, rarity))
    update_data()

def get_pets(member):
    account = get_account( member )
    if "pets" not in account:
        account["pets"] = []
    return account["pets"]

def clear_all_pets():
    for memberid in data:
        data[memberid]["pets"] = []
    update_data()

def remove_pet(member, name):
    prepare_account(member)
    if has_pet(member, name):
        for pet in get_pets(member):
            if pet.name == name:
                get_pets.remove(pet)
                update_data()
                return True
        return False
    else:
        return False

def has_pet(member, name):
    for pet in get_pets(member):
        if pet.name == name.upper():
            return True
    return False

def equip_pet(member, name):
    if not has_pet(member, name):
        return "Du hast dieses Pet nicht!"

    equipped_pets_amount = 0
    for pet in get_pets(member):
        if pet.equipped == True:
            equipped_pets_amount += 1
    if equipped_pets_amount == 5:
        return "Du hast die Maximale Anzahl an Pets erreicht! Unequippe erst ein Pet!"
    for pet in get_pets(member):
        if pet.name == name.upper() and pet.equipped == False:
            pet.equipped = True
            update_data()
            return "Du hast " + name + " Equipped"

def unequip_pet(member, name):
    if not has_pet(member, name):
        return "Du hast dieses Pet nicht!"
    if is_pet_equipped(member, name.upper()):
        for pet in get_pets(member):
            if pet.name == name.upper() and pet.equipped == True:
                pet.equipped = False
                update_data()
                return "Du hast " + name + " Unequipped"
    else:
        return "Du hast dieses Pet nicht equipped!"

def is_pet_equipped(member, name):
    for pet in get_pets(member):
        if pet.name == name.upper() and pet.equipped == True:
            return True
    return False

def get_pet_amount(member):
    return len(get_pets(member))



###################### MoneyMiner

def get_moneyminer(member):
    account = get_account( member )
    if "moneyminer" not in account:
        account["moneyminer"] = {}
    return account["moneyminer"]


def levelup_backpack(member):
    moneyminer = get_moneyminer(member)
    if "bp_level" not in moneyminer:
        moneyminer["bp_level"] = 1
    moneyminer["bp_level"] += 1
    update_data()
    return moneyminer["bp_level"]

def levelup_pickaxe(member):
    moneyminer = get_moneyminer(member)
    if "pa_level" not in moneyminer:
        moneyminer["pa_level"] = 1
    moneyminer["pa_level"] += 1
    update_data()
    return moneyminer["pa_level"]

def backpack_set_money(member, money):
    moneyminer = get_moneyminer(member)
    if "bp_fill" not in moneyminer:
        moneyminer["bp_fill"] = 0
    moneyminer["bp_fill"] = money
    update_data()

def get_backpack_money(member):
    moneyminer = get_moneyminer(member)
    if "bp_fill" not in moneyminer:
        moneyminer["bp_fill"] = 0
        update_data()
    return moneyminer["bp_fill"]

def get_max_backpack(member):
    moneyminer = get_moneyminer(member)
    if "bp_level" not in moneyminer:
        moneyminer["bp_level"] = 1
        update_data()
    return 30 * moneyminer["bp_level"]

def get_backpack_level(member):
    moneyminer = get_moneyminer(member)
    if "bp_level" not in moneyminer:
        moneyminer["bp_level"] = 1
    update_data()
    return moneyminer["bp_level"]

def get_pickaxe_level(member):
    moneyminer = get_moneyminer(member)
    if "pa_level" not in moneyminer:
        moneyminer["pa_level"] = 1
    update_data()
    return moneyminer["pa_level"]






