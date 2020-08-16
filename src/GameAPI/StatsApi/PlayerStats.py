import json


filename="resources/player_data_new.json"

def load_data():
    try:
        file = open( filename, "r")
        data = json.load(file)
        file.close()
    except:
        print("File existiert nicht, leeres Dictionary erzeugen...")
        data = {}
    return data

def modify_user( user_id, todo ):
    data = load_data()

    if user_id in data: # Existiert der Benutzer?
        userdata = data[user_id] # Daten des Benutzer extrahieren
    else:
        userdata = { "xp": 0 } # sonst neuen Benutzer mit xp=0 anlegen

    userdata = todo( userdata ) # Vordefinierte to do Funktion ausführen
    data[user_id]=userdata   # Userdaten aktualisieren

    with open(filename, "w") as file:
        json.dump( data, file, indent=4)


def add_xp(user_id , xp):
    def todo( userdata ):
        userdata["xp"] += xp
        return userdata
    modify_user( user_id, todo)

def add_player_stats(user_id, gamename, won ):
    def todo( userdata ):
        if not gamename in userdata:
            userdata[gamename] = [ 0,0 ]
        userdata[gamename][0] += 1  # Anzahl der gesamten Spiele +1
        if won:
            userdata[gamename][1] += 1
        return userdata
    modify_user( user_id, todo)
