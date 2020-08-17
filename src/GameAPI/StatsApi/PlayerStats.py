import json

filename="player_data_new.json"

class ModStatsData():
    def __init__(self, user_id):
        self.user_id = user_id
        self.data = {}
        
    def __enter__(self):
        if path.isfile(file_path):
            with open(file_path, "r") as fp:
                self.data = json.load(fp)
        self.user = self.data.get( user_id, {"xp":0, "stats": {}} )
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.data[ self.user_id ] = self.user
        with open(filename, "w") as file:
            json.dump( self.data, file, indent=4)

# XP eines Users um bestimmten Wert erhöhen:
def add_xp(user_id , xp):
    with ModStatsData( user_id ) as data:
        data.user["xp"] += xp

# Spielstatistiken 
def add_player_stats(user_id, gamename, wins=0, played=0 ):
    with ModStatsData( user_id ) as data:
        data.user["stats"][game_name] = [ x+y for x,y in zip( data.user["stats"].get(game_name, [0, 0]), [ wins, played ] ) ]

