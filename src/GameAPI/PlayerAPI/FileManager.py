import json
import os.path as path

file_path = "../resources/player_data.json"


# Der Decorator baut das Laden und Speichern der JSON Datei um die API Funktionen add_xp, add_to_stats und beliebige weitere:
def json_decorator(api_function):
    def wrapper(user_id, *args):
        data = {}
        if path.isfile(file_path):
            with open(file_path, "r") as fl:
                data = json.load(fl)
        userdata = data.get(user_id, {"xp": 0, "stats": {}})  # Default Value falls User nicht existiert
        data[user_id] = api_function(userdata, user_id, *args)  # Modifikation der Userdaten mit der api funktion
        json.dump(data, open(file_path, "w+"), indent=4)

    return wrapper


# api funktionen:
@json_decorator
def add_xp(userdata, user_id, xp):  # "userdata" muss man beim aufruf nicht wirklich angeben, das macht der Decorator
    userdata["xp"] += xp
    return userdata  # Die modifizierten Daten hier einfach zurückgeben


@json_decorator
def add_to_stats(userdata, user_id, game_name, wins=0, played=0):
    userdata["stats"][game_name] = [x + y for x, y in zip(userdata["stats"].get(game_name, [0, 0]), [wins, played])]
    return userdata
