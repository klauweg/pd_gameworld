import json
import os.path as path

file_path = "../resources/player_data.json"


class JsonData:
    def __init__(self):
        self.data = {}
        if path.isfile(file_path):
            with open(file_path, "r") as fp:
                self.data = json.load(fp)

    def getuser(self, user_id):
        return self.data.get(str(user_id), {"xp": 0, "stats": {}})

    def setuser(self, user_id, userdata):
        self.data[str(user_id)] = userdata
        with open(file_path, "w") as fp:
            json.dump(self.data, fp, indent=4)

