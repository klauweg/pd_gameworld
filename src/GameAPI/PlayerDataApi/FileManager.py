import json
import os.path as path

file_path = "../resources/player_data.json"

data = {}
if path.isfile(file_path):
    with open(file_path, "r") as fp:
        data = json.load(fp)

def getuser(user_id):
    return data.get(str(user_id), {})

def getuserlist():
    return data.keys()

def setuser(user_id, userdata):
    data[str(user_id)] = userdata
    with open(file_path, "w") as fp:
        json.dump(data, fp, indent=4)

