import json
import os.path as path

file_path = "resources/player_data.json"

class JsonData():
    def __init__(self):
        self.data = {}
        if path.isfile(file_path):
            with open(file_path, "r") as fp:
                self.data = json.load(fp)

    def getuser( self, user_id ):
        return self.data.get( user_id, {"xp":0, "stats": {}} )

    def setuser( self, user_id, userdata ):
        self.data[ user_id ] = userdata
        with open( file_path, "w" ) as fp:
            json.dump( self.data, fp, indent=4 )

# api funktionen:
def add_xp( user_id, xp):
    json = JsonData()
    userdata = json.getuser( user_id )
    userdata["xp"] += xp
    json.setuser( user_id, userdata )

def add_to_stats( user_id, game_name, wins=0, played=0):
    json = JsonData()
    userdata = json.getuser( user_id )
    userdata["stats"][game_name] = [ x+y for x,y in zip( userdata["stats"].get(game_name, [0, 0]), [ wins, played ] ) ]
    json.setuser( user_id, userdata )