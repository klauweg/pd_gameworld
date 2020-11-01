import math
import traceback

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

def prepare_account(member):
    id = str(member.id)
    if not id in data:
        data[id] = {"xp": 0, "money": 0, "stats": {}, "pets": []}

def get_level(member):
    return math.ceil(math.sqrt(get_xp(member)/5))

async def add_xp(member, xp):
    prepare_account(member)
    multiplyxp = 0
    for pet in data[str(member.id)]["pets"]:
        multiplyxp += xp*pet.xp_multiply - xp
    data[str(member.id)]["xp"] += (xp+multiplyxp)
    await update_player_nick(member)
    update_data()

async def set_xp(member, xp):
    prepare_account(member)
    data[str(member.id)]["xp"] = xp
    await update_player_nick(member)
    update_data()


def get_xp(member):
    prepare_account(member)
    return data[str(member.id)]["xp"]

async def update_player_nick(member: discord.Member):
    try:
        await member.edit(nick=member.name + " [Lvl: " + str(get_level(member)) + "]")
    except discord.Forbidden:
        pass


################# STATS

def add_to_stats(member, game_name, wins=0, played=0):
    prepare_account(member)
    try:
        data[str(member.id)]["stats"][game_name][0] += wins
        data[str(member.id)]["stats"][game_name][1] += played
    except KeyError:
        data[str(member.id)]["stats"][game_name] = [0, 0]
    update_data()

def get_stats(member):
    prepare_account(member)
    return data[str(member.id)]["stats"]


############################### Economy

def deposit_money(member, amount):
    prepare_account(member)
    multiplymoney= 0
    for pet in data[str(member.id)]["pets"]:
        multiplymoney += amount*pet.money_multiply - amount
    data[str(member.id)]["money"] += (amount + multiplymoney)
    update_data()


def withdraw_money(member, amount):
    prepare_account(member)
    if data[str(member.id)]["money"] >= amount:
        data[str(member.id)]["money"] -= amount
        update_data()
    else:
        return False


def set_money(member, amount):
    if amount >= 0:
        prepare_account(member)
        data[str(member.id)]["money"] = amount
        update_data()


def get_money(member):
    prepare_account(member)
    return data[str(member.id)]["money"]


def has_money(member, amount):
    prepare_account(member)
    if data[str(member.id)]["money"] >= amount:
        return True
    else:
        return False

############################ PETS

def add_pet(member, name, xp_m, money_m, rarity):
    prepare_account(member)
    pet = Pet(name, xp_m, money_m, rarity)
    data[str(member.id)]["pets"].append(pet)
    update_data()

def get_pets(member):
    prepare_account(member)
    return data[str(member.id)]["pets"]

def clear_all_pets():
    for memberid in data:
        data[memberid]["pets"] = []
    update_data()



